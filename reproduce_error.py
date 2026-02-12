import os
import django
import asyncio
import json

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcp_project.settings')
django.setup()

from dotenv import load_dotenv
load_dotenv()

from fastmcp import FastMCP
from core.mcp_registry import DRFMCPRegistry
from core.urls import router

async def test_creation():
    mcp = FastMCP("Test")
    API_URL = "http://localhost:8000/api"
    API_TOKEN = os.getenv("DJANGO_API_TOKEN")

    registry = DRFMCPRegistry(mcp, API_URL, API_TOKEN)
    registry.register_router(router)

    # Pegamos a ferramenta task_create
    # Note: No FastMCP, podemos chamar a função interna do tool se a encontrarmos
    # Mas como ela foi registrada no mcp, o jeito mais fácil é simular a chamada.
    
    print("--- Testando Criação de Tarefa ---")
    
    # Tenta encontrar a ferramenta task_create
    # FastMCP armazena ferramentas de forma que possamos acessá-las
    # Mas vamos apenas testar a lógica do DRFMCPRegistry diretamente se for mais fácil.
    
    # Simula a chamada dynamic_post_tool que foi registrada
    # Vamos criar uma tarefa de teste
    test_data = {"title": "Tarefa de Teste Auto-Discovery", "description": "Criada via script de reprodução"}
    
    # Como não temos acesso fácil ao objeto dynamic_post_tool sem rodar o servidor,
    # vamos testar o _handle_response e a lógica de request.
    
    import httpx
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Token {API_TOKEN}"}
        url = "http://localhost:8000/api/tasks/"
        
        print(f"Enviando POST para {url}")
        # O erro pode ser que o DRF espera title/description no root,
        # mas o mcp_registry passa o que o usuário mandar.
        
        response = await client.post(url, json=test_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_creation())
