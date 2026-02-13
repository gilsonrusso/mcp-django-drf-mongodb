import httpx
import logging
from fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de Logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configurações vindas do .env
API_SCHEMA_URL = os.getenv("API_SCHEMA_URL", "http://localhost:8000/api/schema/")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TOKEN = os.getenv("API_TOKEN")


def create_mcp_server():
    """
    Cria e configura o servidor MCP usando a integração nativa com OpenAPI do FastMCP.
    """
    logger.info("Carregando schema OpenAPI para inicializar o Gateway...")

    # Configura o cliente HTTP com autenticação se o token existir
    headers = {"Accept": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Token {API_TOKEN}"

    # Cliente assíncrono para as chamadas de API
    api_client = httpx.AsyncClient(base_url=API_BASE_URL, headers=headers, timeout=30.0)

    try:
        # Busca o schema para inicializar o server
        # Usamos uma chamada síncrona simples aqui para facilitar a inicialização do FastMCP
        response = httpx.get(API_SCHEMA_URL, headers=headers, timeout=30.0)
        response.raise_for_status()
        openapi_spec = response.json()

        logger.info(f"Schema OpenAPI carregado com sucesso de {API_SCHEMA_URL}")

        # Cria o servidor MCP dinamicamente a partir do OpenAPI
        # O FastMCP 2.0+ converte automaticamente endpoints em Tools/Resources
        mcp = FastMCP.from_openapi(
            openapi_spec=openapi_spec, client=api_client, name="Django Task Gateway"
        )

        return mcp
    except Exception as e:
        logger.error(f"Falha crítica ao carregar OpenAPI: {e}")
        # Retorna um servidor com aviso se não conseguir carregar
        mcp = FastMCP("Empty Gateway")

        @mcp.tool()
        def info():
            return f"Erro ao carregar schema da API: {e}"

        return mcp


if __name__ == "__main__":
    # Inicializa o servidor
    mcp = create_mcp_server()

    # Roda o servidor MCP via HTTP (streamable-http)
    # Porta padrão: 8001
    mcp.run(transport="streamable-http", port=8001)
