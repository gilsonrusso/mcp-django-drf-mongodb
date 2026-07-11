from fastmcp import FastMCP
import httpx
import logging
import json
import os
import django
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configura o ambiente Django para permitir imports do core
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcp_project.settings')
django.setup()

# Importa o router e o registry
from core.urls import router
from core.mcp_registry import DRFMCPRegistry

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações do Django API
API_URL = "http://localhost:8000/api"
API_TOKEN = os.getenv("DJANGO_API_TOKEN")

# Cria o servidor MCP
mcp = FastMCP("DjangoTaskManager")

# Registra automaticamente todas as ferramentas baseadas no Router do DRF
registry = DRFMCPRegistry(mcp, API_URL, API_TOKEN)
registry.register_router(router)

# Mantemos os prompts manuais por enquanto, pois eles são mais "criativos" 
# e menos "estruturais" que os endpoints da API.
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
