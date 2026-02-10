# Aprendizado: Entendendo o Back-end e MCP

Este documento explica os conceitos fundamentais do projeto, detalhando o papel de cada tecnologia e arquivo para facilitar o seu aprendizado.

---

## 1. O "Cérebro" do Projeto: `mcp_project/settings.py`

Este arquivo centraliza todas as configurações da aplicação.

- **INSTALLED_APPS**: Onde registramos o Django Rest Framework (`rest_framework`) e o nosso app (`core`).
  - **Atenção**: Note que removemos aplicativos como `admin`, `auth` e `sessions`.
  - **Por que?** Esses componentes padrão do Django foram feitos para bancos SQL. No MongoDB, eles exigem configurações complexas de compatibilidade. Como estamos focados no **básico**, mantivemos apenas o essencial para a sua API funcionar.
- **DATABASES**: Configuramos o **django-mongodb-backend**. O MongoDB salva dados como documentos (tipo JSON). Este backend é a solução moderna que permite que o Django use o MongoDB, lidando com campos específicos como o `ObjectId`.

## 2. A Estrutura dos Dados: `core/models.py`

O **Model** define a "forma" dos seus dados.

- Criamos a classe `Task`. No Django, você não cria tabelas ou coleções no banco de dados manualmente; você define uma classe em Python e o Django gera a estrutura necessária para você.

## 3. O Tradutor: `core/serializers.py` (DRF)

Este é um componente específico do Django Rest Framework.

- O Serializador transforma objetos complexos do Python em **JSON** (um formato de texto que a internet entende).
- **Desafio do MongoDB**: Como o banco usa um ID especial (`ObjectId`), o Django Rest Framework às vezes se confunde ao tentar transformar isso em número. No arquivo `core/serializers.py`, nós forçamos o campo `id` a ser tratado como um texto simples (`CharField`) para que ele possa ser enviado via JSON sem erros.

## 4. A Lógica de Negócio: `core/views.py`

Aqui decidimos o que acontece quando alguém acessa sua API.

- Usamos o `ModelViewSet`. Ele é uma ferramenta poderosa que já traz pronto o código para as 4 operações básicas: Criar, Ler, Atualizar e Deletar (CRUD).

## 5. O Mapa da Cidade: `core/urls.py` e `mcp_project/urls.py`

As URLs são os endereços da sua API.

- O **Router** gera os endereços automaticamente (ex: `/api/tasks/`).
- **Filtros (Query Parameters)**: Podemos passar dados pela URL, como `/api/tasks/?completed=true`. No arquivo `views.py`, capturamos isso para filtrar o banco de dados.
- **Ações Customizadas (@action)**: Criamos uma "outra rota" nova (`/api/tasks/completed/`) para buscas específicas, usando o decorador `@action`.

## 6. A Praticidade do Docker: `docker-compose.yml`

O **Docker** permite que você rode softwares (como o MongoDB) dentro de "containers" isolados.

- **Por que usar no desafio?** Em vez de você ter que baixar e instalar o MongoDB manualmente no seu Windows/Linux/Mac, o Docker faz isso para você com um único comando. Ele garante que o banco de dados que eu uso aqui seja exatamente o mesmo que você vai usar aí.

## 7. A Integração: `mcp_server.py` (FastMCP)

O servidor MCP é o que conecta a Inteligência Artificial ao seu código.

- **Tools (`@mcp.tool`)**: São funções Python "especiais" que a IA "sabe" que pode chamar para realizar ações.
- **Httpx**: É a biblioteca que o servidor MCP usa para "conversar" com a sua API Django (fazendo requisições HTTP).

---

## Fluxo de Funcionamento (Passo a Passo):

1. **Você ou a IA** solicita uma ação (ex: "Liste as tarefas").
2. O **Servidor MCP** faz um pedido (request) para a sua **API Django**.
3. O **Django** recebe o pedido, valida os dados com o **Serializer**.
4. O **Django** usa o **Model** e o driver **django-mongodb-backend** para buscar a informação no **MongoDB**.
5. A informação faz o caminho de volta até aparecer na tela para você.

---

**💡 Dica de Estudo:** O melhor jeito de aprender é "quebrar" as coisas! Tente mudar o nome de um campo no `models.py` e veja quais outros arquivos param de funcionar. Isso vai te mostrar exatamente como cada peça depende da outra.
