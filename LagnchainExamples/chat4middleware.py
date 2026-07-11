from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from typing import Callable

# Tools simples
@tool
def somar(a: int, b: int) -> int:
    """Soma dois números"""
    return a + b

@tool
def clima(cidade: str) -> str:
    """Consulta o clima de uma cidade"""
    return f"O clima em {cidade} está 28°C, ensolarado."

# ========== MIDDLEWARES ==========

# Middleware 1: Log antes e depois do modelo
@wrap_model_call
def logger_middleware(request, handler):
    """Loga antes e depois do modelo processar."""
    print("  ⚡ [PRÉ-MODELO] Enviando para o LLM...")
    print(f"  ⚡ [PRÉ-MODELO] Tools disponíveis: {[t.name for t in request.tools]}")

    response = handler(request)

    ai_msg = response.result[0]
    if ai_msg.tool_calls:
        print(f"  ⚡ [PÓS-MODELO] LLM decidiu chamar: {[tc['name'] for tc in ai_msg.tool_calls]}")
    else:
        print(f"  ⚡ [PÓS-MODELO] LLM respondeu direto (sem tools)")

    return response

# Middleware 2: Conta tokens (simulado)
@wrap_model_call
def token_counter(request, handler):
    """Conta tokens consumidos."""
    input_chars = sum(len(m.content or "") for m in request.messages)

    response = handler(request)

    ai_msg = response.result[0]
    output_chars = len(ai_msg.content or "")
    print(f"  💰 [BILLING] Input: ~{input_chars // 4} tokens | Output: ~{output_chars // 4} tokens")

    return response

# ========== AGENTE ==========

checkpointer = InMemorySaver()

agent = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[somar, clima],
    system_prompt="Você é um assistente útil que responde em português.",
    middleware=[logger_middleware, token_counter],
    checkpointer=checkpointer,
)

print("Chat com Middleware (digite 'sair' pra encerrar)\n")

config = {"configurable": {"thread_id": "conversa-1"}}

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break

    print()
    resultado = agent.invoke(
        {"messages": [{"role": "user", "content": pergunta}]},
        config=config
    )

    for msg in resultado["messages"]:
        tipo = msg.__class__.__name__
        if tipo == "AIMessage" and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  🔧 Tool chamada: {tc['name']}({tc['args']})")
        elif tipo == "ToolMessage":
            print(f"  📦 Resultado: {msg.content}")
        elif tipo == "AIMessage" and msg.content:
            print(f"\nClaude: {msg.content}\n")