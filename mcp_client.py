import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from llmModel import llm

load_dotenv()

# Configuração do servidor MCP Gateway via HTTP
MCP_GATEWAY_URL = os.getenv("MCP_GATEWAY_URL", "http://localhost:8001/mcp")


async def run_client():
    print(f"--- Conectando ao MCP Gateway via HTTP: {MCP_GATEWAY_URL} ---\n")

    # Configura o cliente MCP usando HTTP transport (oficial do LangChain)
    client = MultiServerMCPClient(
        {
            "django_gateway": {
                "transport": "http",
                "url": MCP_GATEWAY_URL,
            }
        }
    )

    try:
        # Carrega as ferramentas do servidor MCP
        print("Carregando ferramentas do MCP Gateway...")
        tools = await client.get_tools()

        if not tools:
            print(
                "❌ Nenhuma ferramenta foi descoberta. Verifique se o Gateway está rodando e o schema está acessível."
            )
            return

        print(f"✅ {len(tools)} ferramentas carregadas:\n")
        for tool in tools:
            print(f"  - {tool.name}")

        # Cria o agente usando a API oficial do LangChain
        # Usa o LLM configurado (Ollama qwen2.5-coder:7b)
        agent = create_agent(llm, tools)

        print("\n--- Cliente LangChain + MCP (HTTP) Ativo! ---")
        print("(Digite 'sair' para encerrar)\n")

        while True:
            try:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "Você: "
                )

                if user_input.lower() in ["sair", "exit", "quit"]:
                    break

                if not user_input.strip():
                    continue

                # Invoca o agente com a mensagem do usuário
                result = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )

                # Extrai a resposta final
                final_message = result["messages"][-1]
                print(f"\n🤖 IA: {final_message.content}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Erro no Agente: {e}\n")

    except Exception as e:
        print(f"\n❌ Erro ao conectar ao Gateway: {e}\n")


if __name__ == "__main__":
    asyncio.run(run_client())
