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

## 🛠️ Novidades do Projeto

- **MCP Prompts**: O servidor agora fornece modelos de resposta e sugestões dinâmicas.
- **Validação Rigorosa**: A descrição da tarefa é um campo obrigatório no banco PostgreSQL.
- **Logs de Debug**: O cliente mostra `[DEBUG]` para que você veja a conversa entre a IA e o Servidor.

---

## 📚 Arquivos Principais

- `mcp_server.py`: Onde moram as **Tools** e **Prompts**.
- `mcp_client.py`: O agente autônomo baseado em LlamaIndex.
- `core/models.py`: A estrutura da tarefa (Título e Descrição).

**Dica:** Leia o arquivo `APRENDIZADO.md` para entender a teoria por trás de cada linha de código! 🚀🍿
