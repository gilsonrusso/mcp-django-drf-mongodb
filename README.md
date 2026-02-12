# Guia Completo: Django + Postgres + MCP + LLM (Ollama) 🤖🐘

Este projeto é um ecossistema completo para aprender como integrar uma Inteligência Artificial local com um sistema web profissional (Django).

## 🏗️ Arquitetura do Sistema

1.  **Banco de Dados**: PostgreSQL (rodando via Docker).
2.  **Back-end**: Django + Django Rest Framework (API de Tarefas).
3.  **Servidor MCP**: Uma ponte que expõe a API do Django como "ferramentas" e "prompts" para a IA.
4.  **Agente LLM**: Um cliente que usa o modelo **Qwen2.5-Coder** (via Ollama) com LlamaIndex para gerenciar suas tarefas.

---

## 🚀 Como Configurar e Executar

### 1. Requisitos Prévios

- Python 3.10+
- Docker & Docker Compose
- **Ollama** (Baixe em [ollama.com](https://ollama.com))

### 2. Preparar Ambiente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux
# No Windows use: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Iniciar Infraestrutura

```bash
docker compose up -d
python manage.py makemigrations core
python manage.py migrate
python manage.py runserver  # Terminal 1
```

---

## 🤖 Conversando com a IA

Em um novo terminal (com o Django rodando), inicie o cliente:

```bash
python mcp_client.py
```

### O que você pode testar:

- **Sugestões**: _"Me sugira uma tarefa sobre Docker"_ (Usa MCP Prompts).
- **Criação Obrigatória**: _"Crie uma tarefa chamada Estudar"_ (A IA vai te pedir a descrição, pois agora ela é obrigatória).
- **Listagem**: _"Quais tarefas eu tenho?"_ ou _"Liste as concluídas"_.

---

- **Introspecção Profunda (Deep Mapping) ⚖️**: O `DRFMCPRegistry` agora extrai automaticamente todas as rotas, campos obrigatórios (via Serializers) e parâmetros de busca/paginação do Django, sem necessidade de configuração manual.
- **Assinaturas Dinâmicas**: A IA vê exatamente quais campos são obrigatórios e quais são opcionais, evitando erros de preenchimento.
- **Auto-Documentação**: Gera o arquivo `mcp_mappings.md` com o mapa detalhado de todas as ferramentas disponíveis.
- **Logs de Debug**: O cliente mostra `[DEBUG]` para que você veja a conversa entre a IA e o Servidor.

---

## 📚 Arquivos Principais

- `mcp_server.py`: Onde moram os **Tools** e **Prompts**.
- `mcp_client.py`: O agente autônomo baseado em LlamaIndex.
- `core/models.py`: A estrutura da tarefa (Título e Descrição).
- `core/mcp_registry.py`: O motor de **Auto-Discovery** que faz o mapeamento inteligente do Django para o MCP.
- `mcp_mappings.md`: Documentação gerada automaticamente detalhando as ferramentas registradas.

---

## 🛠️ Comandos de Desenvolvedor (FastMCP CLI)

O `FastMCP` fornece ferramentas poderosas para inspecionar e testar o seu servidor:

- **Listar Ferramentas**: Veja tudo o que o Auto-Discovery mapeou:
  ```bash
  fastmcp list mcp_server.py
  ```
- **Interface de Teste (Inspector)**: Abre uma interface web para testar as ferramentas:
  ```bash
  fastmcp dev mcp_server.py
  ```
- **Relatório Técnico**: Veja o esquema JSON completo do servidor:
  ```bash
  fastmcp inspect mcp_server.py
  ```
- **Atualizar Documentação**: Gera o arquivo `mcp_mappings.md` com os mapeamentos atuais:
  ```bash
  python core/mcp_registry.py
  ```

**Dica:** Leia o arquivo `APRENDIZADO.md` para entender a teoria por trás de cada linha de código! 🚀🍿
