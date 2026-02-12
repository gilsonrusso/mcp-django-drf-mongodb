import httpx
import json
import logging
from fastmcp import FastMCP

# Nota: DefaultRouter é importado apenas quando necessário dentro dos métodos
# para evitar erros de configuração do Django (settings) em execuções standalone.

logger = logging.getLogger(__name__)

class DRFMCPRegistry:
    """
    Classe responsável por mapear automaticamente ViewSets do Django REST Framework (DRF)
    para ferramentas do Model Context Protocol (MCP).
    """
    
    def __init__(self, mcp: FastMCP, api_url: str, api_token: str = None):
        """
        Inicializa o registry com a instância do FastMCP, a URL base da API
        e opcionalmente um token de autenticação.
        """
        self.mcp = mcp
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.registered_tools = [] # Armazena metadados para geração da documentação markdown

    def get_auth_headers(self):
        """
        Retorna os headers de autenticação se o token estiver presente.
        """
        if not self.api_token:
            return {}
        return {"Authorization": f"Token {self.api_token}"}

    def register_router(self, router: 'DefaultRouter'):
        """
        Ponto de entrada principal: Varre um router do DRF e registra ferramentas 
        para cada ViewSet encontrada.
        """
        # Itera sobre o registro do router (prefixo da URL, classe da ViewSet, nome base)
        for prefix, viewset_class, basename in router.registry:
            self._register_viewset(router, prefix, viewset_class, basename)
        
        # Gera a documentação após registrar todas as ferramentas
        self.generate_markdown_docs()

    def _register_viewset(self, router, prefix, viewset_class, basename):
        """
        Introspecta uma ViewSet específica para descobrir ações, campos e filtros.
        """
        logger.info(f"--- Deep Mapping: {basename} (Prefix: {prefix}) ---")
        
        from rest_framework.settings import api_settings
        
        # 1. Obtém as rotas dinâmicas do router para esta ViewSet específica.
        # Isso garante que respeitamos a configuração de rotas do próprio DRF.
        try:
            routes = router.get_routes(viewset_class)
        except Exception as e:
            logger.error(f"Falha ao obter rotas para {basename}: {e}")
            return

        # 2. Extrai os campos do corpo (Body) e seu status de 'obrigatório' via Serializer.
        body_fields = {}
        try:
            if hasattr(viewset_class, 'serializer_class') and viewset_class.serializer_class:
                serializer = viewset_class.serializer_class()
                body_fields = {
                    name: field.required 
                    for name, field in serializer.fields.items() 
                    if not field.read_only
                }
        except: pass

        # 3. Descoberta de parâmetros de Paginação e Filtros.
        # Padrões do DRF caso não consigamos instrospectar as classes específicas
        pagination_params = ['page', 'page_size', 'limit', 'offset']
        filter_params = []
        
        # Detecta filtros habilitados diretamente na classe da ViewSet (search/ordering).
        if hasattr(viewset_class, 'search_fields'): filter_params.append('search')
        if hasattr(viewset_class, 'ordering_fields'): filter_params.append('ordering')
        if hasattr(viewset_class, 'filterset_fields'): filter_params.extend(viewset_class.filterset_fields)

        # 4. Processa cada rota individualmente.
        # O DRF usa placeholders como {prefix}, {lookup} e {trailing_slash}.
        lookup_field = getattr(viewset_class, 'lookup_field', 'pk')
        trailing_slash = '/' if getattr(router, 'trailing_slash', True) else ''

        for route in routes:
            url_pattern = route.url
            
            # Resolve os placeholders do DRF para o formato real.
            mcp_path = url_pattern.replace('{prefix}', prefix)
            mcp_path = mcp_path.replace('{lookup}', f'{{{lookup_field}}}')
            mcp_path = mcp_path.replace('{trailing_slash}', trailing_slash)
            
            import re
            # Descobre grupos nomeados adicionais (ex: custom actions com regex próprio).
            named_groups = re.findall(r'\(\?P<([^>]+)>[^)]+\)', mcp_path)
            
            # Limpa marcadores de regex (^, $) e converte grupos (?P<name>...) para {name} estilo MCP.
            clean_path = mcp_path.lstrip('^').rstrip('$').replace('\\.', '.')
            for name in named_groups:
                clean_path = re.sub(rf'\(\?P<{name}>[^)]+\)', f'{{{name}}}', clean_path)
            
            actual_path = f"/{clean_path}".replace('//', '/')
            
            # Uma rota pode ter múltiplos métodos (ex: GET e POST no mesmo endpoint).
            for method, action_name in route.mapping.items():
                if not hasattr(viewset_class, action_name): continue
                
                method = method.upper()
                tool_name = f"{basename}_{action_name}"
                desc = getattr(viewset_class, action_name).__doc__ or f"Action {action_name} on {basename}."
                
                relevant_fields = {} # {nome_do_campo: eh_obrigatorio}
                
                # Campos de Path (presentes na URL, como {pk}) são sempre obrigatórios.
                if '{' in actual_path:
                    path_vars = re.findall(r'\{([^}]+)\}', actual_path)
                    for pv in path_vars:
                        relevant_fields[pv] = True
                
                # Campos de Body (para métodos de escrita: POST, PUT, PATCH).
                if method in ['POST', 'PUT', 'PATCH']:
                    for name, required in body_fields.items():
                        # No PATCH (partial_update), nada é obrigatório (semântica de atualização parcial).
                        is_req = required if method != 'PATCH' and action_name != 'partial_update' else False
                        relevant_fields[name] = is_req
                
                # Campos de Query Search/Pagination (apenas para ações de listagem GET).
                if method == 'GET':
                    # Adiciona filtros se a URL não tiver PK (listagem) ou se for explicitamente a ação 'list'.
                    if '{' not in actual_path or action_name == 'list':
                        all_query = list(set(pagination_params + filter_params))
                        for name in all_query:
                            relevant_fields[name] = False

                # Registra a ferramenta dinamicamente.
                self._add_generic_tool(tool_name, method, actual_path, desc, relevant_fields)
        
        logger.info(f"--- Fim do Deep Mapping: {basename} ---\n")

    def _add_generic_tool(self, name, method, path, description, fields):
        """
        Cria uma ferramenta MCP real, gerando a assinatura da função em tempo de execução
        para que a IA veja exatamente quais argumentos ela aceita.
        """
        args = []
        # Ordenamos os itens para que obrigatórios venham antes de opcionais (regra do Python).
        sorted_items = sorted(fields.items(), key=lambda x: not x[1])
        
        for f, required in sorted_items:
            if not f.isidentifier(): continue
            
            # Tenta prever o tipo: IDs e paginação costumam ser int, o resto str.
            f_type = "int" if f in ['id', 'pk', 'page', 'limit', 'offset', 'page_size'] else "str"
            
            if required:
                # Argumentos obrigatórios não têm valor padrão (default).
                args.append(f"{f}: {f_type}")
            else:
                # Argumentos opcionais usam a sintaxe do Python 3.10+ (type | None = None).
                args.append(f"{f}: {f_type} | None = None")
        
        arg_list = ", ".join(args)
        logger.info(f"  [Tool] {name:20} | {method:6} | Path: {path:30} | Args: ({arg_list})")
        
        # Guarda os metadados para gerar o README/Markdown depois.
        self.registered_tools.append({
            "name": name,
            "method": method,
            "path": path,
            "description": description,
            "arg_list": f"({arg_list})"
        })
        
        # Contexto para a função que será 'executada' dinamicamente.
        ctx = {
            'self': self,
            'method': method,
            'path': path,
            'name': name,
            'httpx': httpx,
            'json': json,
            'logger': logger
        }
        
        # Geramos o código da função assíncrona com a assinatura correta.
        code = f"""
async def {name}({arg_list}):
    # locals() captura todos os argumentos passados para a função
    kwargs = locals()
    return await self._execute_generic_call(name, method, path, kwargs)
"""
        try:
            # Interpreta o código gerado no contexto definido acima.
            exec(code, ctx)
            func = ctx[name]
            # Registra no FastMCP usando o decorator como uma chamada de função.
            self.mcp.tool(name=name, description=description)(func)
            logger.info(f"Ferramenta registrada: {name} ({method} {path})")
        except Exception as e:
            logger.error(f"Erro ao registrar {name}: {str(e)}")

    async def _execute_generic_call(self, name, method, path, kwargs):
        """
        A lógica que roda quando a ferramenta é invocada pela IA.
        Resolve URLs e decide se o campo vai na URL, na Query ou no Body.
        """
        kwargs.pop('self', None) # Remove 'self' que vem do contexto do exec
        
        actual_url = f"{self.api_url}{path}"
        query_params = {}
        body_params = {}

        for key, value in list(kwargs.items()):
            if value is None:
                continue # Ignora parâmetros opcionais não preenchidos
            
            placeholder = f"{{{key}}}"
            if placeholder in actual_url:
                # Resolve variáveis de path (ex: substitui {id} pelo valor real na URL).
                actual_url = actual_url.replace(placeholder, str(value))
            elif method == 'GET':
                # No GET, o que não é path vira query param (?name=value).
                query_params[key] = value
            else:
                # Nos outros métodos, o que não é path vira corpo JSON.
                body_params[key] = value

        # Realiza a chamada HTTP assíncrona.
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, 
                    actual_url, 
                    params=query_params if query_params else None,
                    json=body_params if body_params else None,
                    headers=self.get_auth_headers()
                )
                return self._handle_response(response, name)
            except Exception as e:
                return f"Erro ao executar {name}: {str(e)}"

    def _handle_response(self, response, name):
        """
        Trata o retorno da API para que o Agente entenda o que aconteceu.
        """
        if response.status_code in [401, 403]:
            return "ERRO DE AUTENTICAÇÃO: Token inválido ou expirado."
        
        # O DRF retorna 204 para DELETE e opcionalmente para atualizações.
        if response.status_code == 204:
            return f"Sucesso: {name} concluído (Sem conteúdo de retorno)."

        try:
            response.raise_for_status()
            result = response.json()
            # Retorna o JSON formatado para facilitar a leitura pela IA.
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            details = f" - {response.text}" if response.text else ""
            return f"Erro na ferramenta {name}: {str(e)}{details} (Status: {response.status_code})"

    def generate_markdown_docs(self, filename="mcp_mappings.md"):
        """
        Gera um arquivo Markdown documentando todas as ferramentas registradas.
        """
        try:
            with open(filename, "w") as f:
                f.write("# Mapeamento Automático: Django REST -> MCP Tools\n\n")
                f.write("Este documento mostra como o `DRFMCPRegistry` mapeou as ViewSets para ferramentas MCP.\n\n")
                f.write("| MCP Tool | Verb | Path | Descrição | Parâmetros (Assinatura) |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- |\n")
                
                for t in self.registered_tools:
                    f.write(f"| `{t['name']}` | **{t['method']}** | `{t['path']}` | {t['description']} | `{t['arg_list']}` |\n")
            
            logger.info(f"Documentação automática gerada em {filename}")
        except Exception as e:
            logger.error(f"Falha ao gerar documentação: {str(e)}")

# Bloco de execução para gerar documentação sem precisar rodar o servidor full.
if __name__ == "__main__":
    import os
    import django
    import sys
    from dotenv import load_dotenv
    
    sys.path.append(os.getcwd())
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcp_project.settings')
    
    try:
        django.setup()
        load_dotenv()
        
        from core.urls import router
        
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        
        # Instância fake apenas para rodar a varredura e gerar o markdown.
        mcp_doc = FastMCP("DocGenerator")
        registry = DRFMCPRegistry(mcp_doc, "http://localhost:8000/api")
        registry.register_router(router)
        
        print("\n✨ Documentação MCP gerada com sucesso em mcp_mappings.md")
    except Exception as e:
        print(f"\n❌ Erro ao gerar documentação: {e}")
