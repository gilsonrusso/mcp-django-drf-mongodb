import os
import django
import asyncio
import httpx
from dotenv import load_dotenv

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcp_project.settings')
django.setup()
load_dotenv()

from core.mcp_registry import DRFMCPRegistry
from fastmcp import FastMCP

async def final_check():
    mcp = FastMCP("FinalCheck")
    API_URL = "http://localhost:8000/api"
    API_TOKEN = os.getenv("DJANGO_API_TOKEN")
    
    registry = DRFMCPRegistry(mcp, API_URL, API_TOKEN)
    
    print("--- Testando _execute_call diretamente ---")
    # Simula o que o MCP faria ao chamar a ferramenta dinâmica
    kwargs = {
        "title": "Verificação Final Direta",
        "description": "Se você ler isso, a lógica do registry está correta."
    }
    
    result = await registry._execute_call("task_create", "POST", "/tasks/", kwargs)
    print(f"--- RESULTADO DA API ---\n{result}")
    
    # Verifica no banco (Sync para facilitar)
    from asgiref.sync import sync_to_async
    from core.models import Task
    
    @sync_to_async
    def check_db():
        return Task.objects.filter(title="Verificação Final Direta").exists()
    
    exists = await check_db()
    print(f"--- SUCESSO NO BANCO? {exists} ---")

if __name__ == "__main__":
    asyncio.run(final_check())
