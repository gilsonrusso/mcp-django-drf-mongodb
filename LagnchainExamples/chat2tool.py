from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_core.tools import tool

# Tools simples
@tool
def somar(a: int, b: int) -> int:
    """Soma dois números"""
    return a + b

@tool
def multiplicar(a: int, b: int) -> int:
    """Multiplica dois números"""
    return a * b

@tool
def clima(cidade: str) -> str:
    """Consulta o clima de uma cidade"""
    return f"O clima em {cidade} está 28°C, ensolarado."

# Cria o agente - LangChain 1.0
agent = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[somar, multiplicar, clima],
    system_prompt="Você é um assistente útil que responde em português."
)

print("Chat com Tools (digite 'sair' pra encerrar)\n")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break
    resultado = agent.invoke({"messages": [{"role": "user", "content": pergunta}]})

    for msg in resultado["messages"]:
        tipo = msg.__class__.__name__
        if tipo == "AIMessage" and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  🔧 Tool chamada: {tc['name']}({tc['args']})")
        elif tipo == "ToolMessage":
            print(f"  📦 Resultado: {msg.content}")
        elif tipo == "AIMessage" and msg.content:
            print(f"Claude: {msg.content}\n")