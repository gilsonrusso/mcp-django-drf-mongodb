import os
import django
import asyncio
from dotenv import load_dotenv

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcp_project.settings')
django.setup()
load_dotenv()

from core.mcp_registry import DRFMCPRegistry
from fastmcp import FastMCP
from core.urls import router

async def test_all_actions():
    mcp = FastMCP("AllActionsTest")
    API_URL = "http://localhost:8000/api"
    API_TOKEN = os.getenv("DJANGO_API_TOKEN")

    registry = DRFMCPRegistry(mcp, API_URL, API_TOKEN)
    registry.register_router(router)

    print("\n--- Ferramentas MCP Registradas ---")
    tools = await mcp.list_tools()
    for tool in tools:
        print(f"Tool found: {tool.name}")

    # Teste 1: Buscar uma tarefa (Retrieve - Path Param)
    print("\n--- Testando RETRIEVE (id=1) ---")
    # Como não podemos chamar mcp diretamente sem o server rodando fácil, 
    # vamos usar o execute_generic_call do registry que é o coração da lógica.
    res = await registry._execute_generic_call("task_retrieve", "GET", "/tasks/{id}/", {"id": 1})
    print(f"Resultado Retrieve: {res}")

    # Teste 2: Listar com Filtro (Query Param - Search)
    # Assumindo que o ViewSet tenha search_fields (vou adicionar no core/views.py se não tiver)
    print("\n--- Testando LIST com Query Param ---")
    res = await registry._execute_generic_call("task_list", "GET", "/tasks/", {"search": "Auto-Discovery"})
    print(f"Resultado List: {res}")

    # Teste 3: Update (PUT - Path + Body)
    print("\n--- Testando UPDATE (id=1) ---")
    res = await registry._execute_generic_call("task_update", "PUT", "/tasks/{id}/", {"id": 1, "title": "Título Atualizado", "description": "Desc atualizada"})
    print(f"Resultado Update: {res}")

if __name__ == "__main__":
    asyncio.run(test_all_actions())
