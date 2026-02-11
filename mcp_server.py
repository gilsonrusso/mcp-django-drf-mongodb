from mcp.server.fastmcp import FastMCP
import httpx
import logging
import json

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cria o servidor MCP
mcp = FastMCP("DjangoTaskManager")

# URL base da API Django
API_URL = "http://localhost:8000/api/tasks/"

@mcp.tool()
async def list_tasks():
    """Lista todas as tarefas do banco de dados PostgreSQL via API Django."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_URL)
            response.raise_for_status()
            tasks = response.json()
            if not tasks:
                return "Nenhuma tarefa encontrada no banco de dados."
            return json.dumps(tasks, indent=2)
        except Exception as e:
            logger.error(f"Erro ao listar tarefas: {str(e)}")
            return f"Erro ao listar tarefas: {str(e)}"

@mcp.tool()
async def create_task(title: str, description: str):
    """Cria uma nova tarefa no banco de dados PostgreSQL via API Django."""
    async with httpx.AsyncClient() as client:
        try:
            data = {"title": title, "description": description}
            response = await client.post(API_URL, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao criar tarefa: {str(e)}")
            return f"Erro ao criar tarefa: {str(e)}"

@mcp.tool()
async def list_completed_tasks():
    """Lista apenas as tarefas que já foram marcadas como concluídas."""
    async with httpx.AsyncClient() as client:
        try:
            # Usando a nova rota customizada /api/tasks/completed/
            response = await client.get(f"{API_URL}completed/")
            response.raise_for_status()
            tasks = response.json()
            if not tasks:
                return "Nenhuma tarefa marcada como concluída encontrada."
            return json.dumps(tasks, indent=2)
        except Exception as e:
            return f"Erro ao listar tarefas concluídas: {str(e)}"

@mcp.prompt()
def sugestao_tarefa(tema: str) -> str:
    """Gera uma sugestão de tarefa baseada em um tema."""
    return f"Sugira uma tarefa criativa sobre '{tema}'. O retorno deve ter um título e uma descrição obrigatória."

@mcp.prompt()
def formato_conclusao_tarefa(tarefa_id: int, titulo: str) -> str:
    """Retorna um template de como a IA deve anunciar que uma tarefa foi criada."""
    return f"A tarefa '{titulo}' (ID: {tarefa_id}) foi salva com sucesso no PostgreSQL! Deseja que eu agende um lembrete para ela?"

if __name__ == "__main__":
    mcp.run()
