from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Callable

# ========== CONTEXT SCHEMA ==========

class TenantContext(TypedDict):
    tenant_id: str
    user_id: str
    plano: str
    nome_empresa: str

# ========== TOOLS ==========

@tool
def somar(a: int, b: int) -> int:
    """Soma dois números"""
    return a + b

@tool
def clima(cidade: str) -> str:
    """Consulta o clima de uma cidade"""
    return f"O clima em {cidade} está 28°C, ensolarado."

# ========== MIDDLEWARES ==========

@wrap_model_call
def logger_middleware(request, handler):
    """Loga antes e depois do modelo, incluindo dados do tenant."""
    ctx = request.runtime.context
    print(f"  ⚡ [PRÉ-MODELO] Tenant: {ctx['tenant_id']} | Empresa: {ctx['nome_empresa']} | Plano: {ctx['plano']}")
    print(f"  ⚡ [PRÉ-MODELO] Usuário: {ctx['user_id']}")
    print(f"  ⚡ [PRÉ-MODELO] Tools disponíveis: {[t.name for t in request.tools]}")

    response = handler(request)

    ai_msg = response.result[0]
    if ai_msg.tool_calls:
        print(f"  ⚡ [PÓS-MODELO] LLM decidiu chamar: {[tc['name'] for tc in ai_msg.tool_calls]}")
    else:
        print(f"  ⚡ [PÓS-MODELO] LLM respondeu direto (sem tools)")

    return response

@wrap_model_call
def billing_middleware(request, handler):
    """Conta tokens e verifica o plano do tenant."""
    ctx = request.runtime.context
    input_chars = sum(len(m.content or "") for m in request.messages)

    response = handler(request)

    ai_msg = response.result[0]
    output_chars = len(ai_msg.content or "")
    input_tokens = input_chars // 4
    output_tokens = output_chars // 4

    # Simula limite por plano
    limite = {"free": 100, "pro": 1000, "enterprise": 10000}
    max_tokens = limite.get(ctx["plano"], 100)

    print(f"  💰 [BILLING] Input: ~{input_tokens} tokens | Output: ~{output_tokens} tokens")
    print(f"  💰 [BILLING] Plano: {ctx['plano']} | Limite: {max_tokens} tokens/msg")

    if output_tokens > max_tokens:
        print(f"  🚫 [BILLING] ALERTA: Resposta excedeu o limite do plano!")

    return response

# ========== AGENTE ==========

checkpointer = InMemorySaver()

agent = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[somar, clima],
    system_prompt="Você é um assistente útil que responde em português.",
    middleware=[logger_middleware, billing_middleware],
    checkpointer=checkpointer,
    context_schema=TenantContext,
)

print("Chat com Context Schema (digite 'sair' pra encerrar)\n")

config = {"configurable": {"thread_id": "conversa-1"}}

# Simula o contexto do tenant (em produção vem do banco/auth)
tenant = {
    "tenant_id": "tenant_001",
    "user_id": "user_breno",
    "plano": "pro",
    "nome_empresa": "Cresce Vendas"
}

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break

    print()
    resultado = agent.invoke(
        {"messages": [{"role": "user", "content": pergunta}]},
        config=config,
        context=tenant  # ← injeta o contexto do tenant a cada chamada
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