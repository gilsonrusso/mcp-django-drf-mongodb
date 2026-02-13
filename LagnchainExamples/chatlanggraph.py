from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated, TypedDict

# Tools
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

# State do grafo
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Modelo com tools
llm = init_chat_model("anthropic:claude-haiku-4-5-20251001")
llm_com_tools = llm.bind_tools([somar, multiplicar, clima])

# Nó do agente (chama o LLM)
def agente(state: State):
    resposta = llm_com_tools.invoke(state["messages"])
    return {"messages": [resposta]}

# Monta o grafo manualmente
grafo = StateGraph(State)

# Adiciona os nós
grafo.add_node("agente", agente)
grafo.add_node("tools", ToolNode([somar, multiplicar, clima]))

# Define o fluxo
grafo.set_entry_point("agente")
grafo.add_conditional_edges(
    "agente",
    tools_condition,  # se tem tool_calls vai pra "tools", senão vai pro END
)
grafo.add_edge("tools", "agente")  # depois da tool, volta pro agente

# Compila
agent = grafo.compile()

print("Chat com LangGraph Explícito (digite 'sair' pra encerrar)\n")

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