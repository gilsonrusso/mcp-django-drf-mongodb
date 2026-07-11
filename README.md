# Django + DRF + MCP Gateway (OpenAPI) 🚀

Este projeto demonstra uma arquitetura moderna para integrar **Django REST Framework** com **Model Context Protocol (MCP)** usando **OpenAPI** como ponte de comunicação.

## 🏗️ Arquitetura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Django    │─────▶│ MCP Gateway  │─────▶│  LangChain  │
│  API:8000   │ JSON │  (FastMCP)   │ HTTP │   Client    │
│             │◀─────│   :8001      │◀─────│             │
└─────────────┘      └──────────────┘      └─────────────┘
     │                      │
     │                      │
  OpenAPI              Auto-Discovery
  Schema               de Ferramentas
```

1. **Django API** (porta 8000): Serve a API REST + schema OpenAPI via `drf-spectacular`
2. **MCP Gateway** (porta 8001): Servidor independente que consome o schema e cria ferramentas MCP
3. **Cliente LangChain**: Conecta-se ao Gateway via HTTP e usa LLM local (Ollama)

---

## ✨ Funcionalidades

### 📦 Modelos

#### Project (Projetos)

- Gerenciamento completo de projetos
- Status: planning, active, completed, archived
- Datas de início e conclusão
- Relacionamento 1:N com Tasks
- Estatísticas automáticas (total de tarefas, concluídas, % conclusão)

#### Task (Tarefas)

- CRUD completo de tarefas
- Prioridades: low, medium, high
- Associação opcional a projetos
- Filtros por projeto, prioridade e status

### 🔧 Ferramentas MCP (17 disponíveis)

**Projetos (9 ferramentas):**

- `projects_list` - Listar projetos (com filtro por status)
- `projects_create` - Criar projeto
- `projects_retrieve` - Detalhes do projeto (inclui tarefas)
- `projects_update` / `projects_partial_update` - Atualizar
- `projects_destroy` - Deletar
- `projects_activate_create` - Ativar projeto
- `projects_archive_create` - Arquivar projeto
- `projects_statistics_retrieve` - Estatísticas detalhadas

**Tarefas (8 ferramentas):**

- `tasks_list` - Listar tarefas (filtros: projeto, prioridade, completed)
- `tasks_create` - Criar tarefa
- `tasks_retrieve` - Detalhes da tarefa
- `tasks_update` / `tasks_partial_update` - Atualizar
- `tasks_destroy` - Deletar
- `tasks_complete_create` - Marcar como concluída
- `tasks_completed_list` - Listar apenas concluídas

---

## 🚀 Início Rápido

### 1. Requisitos

- Python 3.10+
- Docker & Docker Compose
- **Ollama** ([ollama.com](https://ollama.com))

### 2. Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configurar Ollama

```bash
# Baixar modelo
ollama pull qwen2.5-coder:7b

# Verificar se está rodando
ollama list
```

### 4. Iniciar Infraestrutura

```bash
# Banco de dados
docker compose up -d

# Migrações
python manage.py migrate

# (Opcional) Criar superusuário
python manage.py createsuperuser
```

### 5. Executar Serviços

**Terminal 1 - Django API:**

```bash
python manage.py runserver
```

**Terminal 2 - MCP Gateway:**

```bash
python mcp_gateway.py
```

**Terminal 3 - Cliente LangChain:**

```bash
python mcp_client.py
```

---

## 🧪 Testando

### Via Cliente LangChain

```bash
python mcp_client.py
```

O cliente carregará automaticamente as 17 ferramentas e você poderá interagir via linguagem natural.

### Via Swagger UI

Acesse: `http://localhost:8000/api/schema/swagger-ui/`

### Via cURL

```bash
# Listar projetos
curl http://localhost:8000/api/projects/

# Criar projeto
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Meu Projeto", "status": "active"}'

# Estatísticas do projeto
curl http://localhost:8000/api/projects/1/statistics/
```

---

## 📁 Estrutura do Projeto

```
learning-mcp-python/
├── core/
│   ├── models.py          # Project, Task
│   ├── serializers.py     # ProjectSerializer, TaskSerializer
│   ├── views.py           # ProjectViewSet, TaskViewSet
│   └── urls.py            # Rotas da API
├── mcp_gateway.py         # Gateway MCP (FastMCP + OpenAPI)
├── mcp_client.py          # Cliente LangChain
├── llmModel.py            # Configuração do Ollama
├── requirements.txt       # Dependências
└── old/                   # Arquivos legados
```

---

## 🔑 Conceitos-Chave

### OpenAPI → MCP

O `mcp_gateway.py` usa `FastMCP.from_openapi()` para converter automaticamente endpoints OpenAPI em ferramentas MCP. **Qualquer mudança na API Django é refletida automaticamente** após reiniciar o Gateway.

### HTTP Transport

O Gateway usa `streamable-http` na porta 8001. O cliente conecta via `langchain-mcp-adapters` usando HTTP transport.

### LangChain Integration

Usa `langchain.agents.create_agent()` (API oficial) para criar agentes que podem executar as ferramentas MCP.

---

## 🐛 Troubleshooting

### Gateway retorna apenas 1 ferramenta (`info`)

**Causa:** Django não está retornando JSON no schema.  
**Solução:** Certifique-se de que o header `Accept: application/json` está sendo enviado (já corrigido no código).

### Cliente não executa ferramentas

**Causa:** Usando API deprecated do LangGraph.  
**Solução:** Use `from langchain.agents import create_agent` (já atualizado).

### Ferramentas não aparecem após adicionar endpoints

**Causa:** Gateway não foi reiniciado.  
**Solução:** Reinicie o `mcp_gateway.py` para recarregar o schema OpenAPI.

---

## 📚 Documentação Adicional

- [APRENDIZADO.md](./APRENDIZADO.md) - Conceitos e arquitetura detalhada

---

## 🤝 Contribuindo

Este é um projeto de aprendizado. Sinta-se livre para:

- Adicionar novos endpoints no Django
- Testar com diferentes LLMs
- Melhorar a documentação

---

## 📄 Licença

MIT
