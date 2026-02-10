# Guia de Aprendizado: Django + DRF + MongoDB + MCP

Este projeto foi criado para ajudar você a entender como integrar o **Django** (um framework web robusto), o **Django Rest Framework (DRF)** (para APIs), o **MongoDB** (banco NoSQL) e o **Model Context Protocol (MCP)** (para estender capacidades de IAs).

## 🚀 Como Executar o Projeto

### 1. Requisitos

- Python 3.10+
- Docker e Docker Compose instalados

### 2. Configuração do Banco de Dados (Docker)

Para rodar o MongoDB sem precisar instalar nada na sua máquina:

```bash
docker-compose up -d
```

Isso iniciará o MongoDB em segundo plano na porta 27017.

### 3. Configuração do Ambiente e Execução

Primeiro, ative seu ambiente virtual:

```bash
source .venv/bin/activate
```

Agora, instale as dependências dentro do ambiente:

```bash
pip install django djangorestframework django-mongodb-backend mcp[cli] httpx pytz six
```

### 4. Preparar o Banco de Dados (Migrações)

Execute os comandos abaixo para criar a estrutura no MongoDB:

```bash
# Cria os arquivos de migração baseados nos modelos
python manage.py makemigrations core

# Aplica as migrações no MongoDB
python manage.py migrate
```

### 5. Iniciar os Servidores

```bash
# Rodar o servidor Django (API)
python manage.py runserver
```

A API estará disponível em: `http://localhost:8000/api/tasks/`

### 6. Rodar o Servidor MCP (Modo de Teste)

O MCP não é um servidor web comum, ele espera comandos via terminal. Para testar visualmente, use o comando abaixo:

```bash
mcp dev mcp_server.py
```

Isso abrirá uma interface no seu navegador (geralmente em `http://localhost:5173`) onde você poderá ver e clicar nas suas ferramentas (`list_tasks`, `create_task`) para testá-las!

---

## 📚 Conceitos Básicos para seu Aprendizado

### 🍃 MongoDB & Djongo

O **MongoDB** é um banco de dados NoSQL orientado a documentos (JSON-like). Ao contrário do SQL tradicional, ele não usa tabelas fixas.
O **django-mongodb-backend** é o driver moderno que permite que o Django "fale" com o MongoDB, lidando com as particularidades do NoSQL (como o uso de `ObjectId` para IDs).

### 🎸 Django Rest Framework (DRF)

O DRF transforma seu projeto Django em uma API. Os componentes principais que usamos aqui são:

- **Models**: Definem a estrutura dos dados (`core/models.py`).
- **Serializers**: Convertem objetos do banco em JSON (`core/serializers.py`).
- **Views**: Definem a lógica (listar, criar, deletar) (`core/views.py`).
- **Routers**: Criam automaticamente as URLs da API (`core/urls.py`).

### 🤖 Model Context Protocol (MCP) com FastMCP

O **MCP** é a "ponte" entre a Inteligência Artificial (como o Claude ou este chat) e o seu código local.
Usamos o **FastMCP** em `mcp_server.py` para criar ferramentas:

- `@mcp.tool()`: Transforma uma função Python comum em uma ferramenta que a IA pode "chamar".
- `httpx`: Usado pelo servidor MCP para fazer requisições à sua API Django.

## 🛠️ Ferramentas Disponíveis no MCP

1. `list_tasks`: Consulta sua API Django e retorna todas as tarefas do MongoDB.
2. `create_task`: Envia um comando para a API Django criar uma nova tarefa.

---

**Dica de Estudo:** Tente adicionar um novo campo ao modelo `Task` (ex: `priority`) e veja como atualizar o Serializer e a Ferramenta no MCP para suportar esse novo campo!
