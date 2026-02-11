import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llmModel import llm

async def run_client():
    # Parâmetros para conectar ao servidor MCP local
    server_params = StdioServerParameters(
        command=sys.executable,  # Usa o mesmo python da venv atual
        args=["mcp_server.py"],   # O servidor que criamos
        env=None
    )

    print("--- Conectando ao Servidor MCP ---")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Inicializa a sessão com o servidor
            await session.initialize()
            
            # 2. Lista as ferramentas disponíveis no servidor
            result = await session.list_tools()
            mcp_tools = result.tools
            
            # 3. Transforma ferramentas MCP em ferramentas que o LlamaIndex entende
            llama_tools = []
            
            def create_tool_wrapper(tool_name):
                # Esta função interna NÃO tem t_name na assinatura, então a LLM não se confunde
                async def _mcp_tool_wrapper(**kwargs):
                    # Se a IA enviar os argumentos dentro de uma chave 'kwargs', nós desempacotamos
                    actual_args = kwargs.get('kwargs', kwargs) if isinstance(kwargs.get('kwargs'), dict) else kwargs
                    
                    print(f"\n[DEBUG] IA chamando ferramenta '{tool_name}' com: {actual_args}")
                    response = await session.call_tool(tool_name, actual_args)
                    content = "\n".join([c.text for c in response.content if hasattr(c, 'text')])
                    
                    print(f"[DEBUG] Resposta do MCP para '{tool_name}': {content}")
                    
                    # Se for criação, retornamos uma confirmação clara para evitar que a IA tente de novo
                    if "create" in tool_name:
                        return f"SUCESSO: Tarefa criada ou processada. Detalhes: {content}"
                    return content
                return _mcp_tool_wrapper

            for tool in mcp_tools:
                llama_tool = FunctionTool.from_defaults(
                    async_fn=create_tool_wrapper(tool.name),
                    name=tool.name,
                    description=tool.description
                )
                llama_tools.append(llama_tool)

            # 3.2 Transforma Prompts MCP em ferramentas de suporte
            try:
                result_prompts = await session.list_prompts()
                for p in result_prompts.prompts:
                    def create_prompt_wrapper(p_name):
                        async def _mcp_prompt_wrapper(**kwargs):
                            actual_args = kwargs.get('kwargs', kwargs) if isinstance(kwargs.get('kwargs'), dict) else kwargs
                            res = await session.get_prompt(p_name, actual_args)
                            return "\n".join([m.content.text for m in res.messages if hasattr(m.content, 'text')])
                        return _mcp_prompt_wrapper

                    llama_prompt_tool = FunctionTool.from_defaults(
                        async_fn=create_prompt_wrapper(p.name),
                        name=f"obter_prompt_{p.name}",
                        description=f"Usa este template/sugestão: {p.description}"
                    )
                    llama_tools.append(llama_prompt_tool)
            except Exception as e:
                print(f"[Aviso] Não foi possível carregar prompts: {e}")

            # 4. Cria o Agente com o "Cérebro" (LLM) e os "Braços" (Ferramentas Django + Prompts)
            all_tool_names = [t.metadata.name for t in llama_tools]
            system_prompt = (
                f"Você é um assistente de gerenciamento de tarefas para Django/PostgreSQL.\n"
                f"Ferramentas: {', '.join(all_tool_names)}\n\n"
                "REGRAS CRÍTICAS:\n"
                "1. Se uma ferramenta exige um campo (como 'description') que o usuário não forneceu, NÃO invente o conteúdo. Pare e pergunte.\n"
                "2. Use 'obter_prompt_sugestao_tarefa' se o usuário pedir ideias.\n"
                "3. Após criar uma tarefa com sucesso, use 'obter_prompt_formato_conclusao_tarefa' para formatar sua resposta final.\n"
                "4. Responda sempre em Português e seja breve."
            )
            # Agente configurado para ser preciso e usar as ferramentas de suporte
            agent = ReActAgent(tools=llama_tools, llm=llm, verbose=False, system_prompt=system_prompt)

            print("--- Cliente Pronto! Pode conversar com a IA sobre suas tarefas. ---")
            print("(Digite 'sair' para encerrar)\n")

            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Você: ")
                
                if user_input.lower() in ["sair", "exit", "quit"]:
                    break
                
                handler = agent.run(user_msg=user_input)
                response = await handler
                
                print(f"\nIA: {response}\n")

if __name__ == "__main__":
    asyncio.run(run_client())
