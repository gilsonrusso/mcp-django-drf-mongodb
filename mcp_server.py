from mcp.server.fastmcp import FastMCP
import httpx
import logging

# Cria o servidor MCP
mcp = FastMCP("Django Task Manager")

# URL base da API Django
API_URL = "http://localhost:8000/api/tasks/"

@mcp.tool()
async def list_tasks():
    """Lista todas as tarefas do banco de dados MongoDB via API Django."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_URL)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Erro ao listar tarefas: {str(e)}"

@mcp.tool()
async def create_task(title: str, description: str = ""):
    """Cria uma nova tarefa no banco de dados MongoDB via API Django."""
    async with httpx.AsyncClient() as client:
        try:
            data = {"title": title, "description": description}
            response = await client.post(API_URL, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Erro ao criar tarefa: {str(e)}"

@mcp.tool()
async def list_completed_tasks():
    """Lista apenas as tarefas que já foram marcadas como concluídas."""
    async with httpx.AsyncClient() as client:
        try:
            # Usando a nova rota customizada /api/tasks/completed/
            response = await client.get(f"{API_URL}completed/")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Erro ao listar tarefas concluídas: {str(e)}"

if __name__ == "__main__":
    mcp.run()
