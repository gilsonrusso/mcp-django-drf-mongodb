# pip install langgraph-supervisor langgraph langchain-anthropic python-dotenv

import asyncio
from dotenv import load_dotenv
from typing import Annotated
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor

load_dotenv()


# ==================== TOOLS DO PESQUISADOR ====================

@tool
def buscar_web(query: str) -> str:
    """Busca informações na web sobre qualquer assunto."""
    # Em produção: Tavily, Google Search, etc.
    return f"📚 Resultado da pesquisa para '{query}': Informação simulada sobre o tema."


@tool
def buscar_documentacao(tecnologia: str) -> str:
    """Busca documentação técnica de uma tecnologia específica."""
    return f"📖 Documentação de {tecnologia}: [simulado] - Em produção usaria busca real."


# ==================== TOOLS DO CODIFICADOR ====================

@tool
def executar_python(codigo: str) -> str:
    """Executa código Python e retorna o resultado."""
    try:
        import io, contextlib
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(codigo, {"__builtins__": {
                "print": print, "range": range, "len": len,
                "sum": sum, "max": max, "min": min, "abs": abs,
                "list": list, "dict": dict, "str": str, "int": int,
                "float": float, "round": round, "sorted": sorted,
                "enumerate": enumerate, "zip": zip, "map": map,
            }})
        resultado = output.getvalue()
        return f"✅ Output:\n{resultado}" if resultado else "✅ Executado (sem output)"
    except Exception as e:
        return f"❌ Erro: {type(e).__name__}: {e}"


@tool
def gerar_codigo(descricao: str, linguagem: str = "python") -> str:
    """Gera código baseado em uma descrição."""
    return f"📝 Código {linguagem} gerado para: {descricao}"


# ==================== AGENTES ====================

pesquisador = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[buscar_web, buscar_documentacao],
    name="pesquisador",
    system_prompt="Você é um pesquisador. Busque informações usando suas ferramentas. Não escreva código."
)

codificador = create_agent(
    model="anthropic:claude-haiku-4-5-20251001",
    tools=[executar_python, gerar_codigo],
    name="codificador",
    system_prompt="Você é um codificador Python/JS. Escreva e execute código. Não pesquise na web."
)


# ==================== SUPERVISOR ====================

workflow = create_supervisor(
    agents=[pesquisador, codificador],
    model="anthropic:claude-haiku-4-5-20251001",
    prompt="""Você é o Supervisor com 2 agentes:
    1. pesquisador - busca informações e documentação
    2. codificador - escreve e executa código
    Delegue para o agente certo. Para tarefas complexas, use os dois em sequência.""",
    add_handoff_back_messages=True,
    output_mode="full_history",
)

app = workflow.compile()


# ==================== EXECUÇÃO ====================

if __name__ == "__main__":
    print("🤖 MULTI-AGENTE: Supervisor + Pesquisador + Codificador")
    print("Digite 'sair' para encerrar\n")

    while True:
        pergunta = input("👤 Você: ").strip()
        if pergunta.lower() in ["sair", "exit", "quit"]:
            break
        if not pergunta:
            continue

        print("\n🔄 Processando...")
        for chunk in app.stream({"messages": [("user", pergunta)]}):
            for node_name, node_output in chunk.items():
                if node_name == "__interrupt__":
                    continue
                messages = node_output.get("messages", [])
                if messages:
                    content = getattr(messages[-1], "content", "")
                    if content and "Successfully transferred" not in str(content):
                        icons = {"supervisor": "🧠", "pesquisador": "🔍", "codificador": "💻"}
                        print(f"\n{icons.get(node_name, '📦')} {node_name}: {content[:500]}")
        print()