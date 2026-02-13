from dotenv import load_dotenv
load_dotenv()

import anthropic
import json

client = anthropic.Anthropic()

# Tools - precisa definir o schema JSON manualmente
tools = [
    {
        "name": "somar",
        "description": "Soma dois números",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "Primeiro número"},
                "b": {"type": "integer", "description": "Segundo número"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "multiplicar",
        "description": "Multiplica dois números",
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "Primeiro número"},
                "b": {"type": "integer", "description": "Segundo número"}
            },
            "required": ["a", "b"]
        }
    },
    {
        "name": "clima",
        "description": "Consulta o clima de uma cidade",
        "input_schema": {
            "type": "object",
            "properties": {
                "cidade": {"type": "string", "description": "Nome da cidade"}
            },
            "required": ["cidade"]
        }
    }
]

# Funções reais - precisa mapear manualmente
def executar_tool(nome, args):
    if nome == "somar":
        return str(args["a"] + args["b"])
    elif nome == "multiplicar":
        return str(args["a"] * args["b"])
    elif nome == "clima":
        return f"O clima em {args['cidade']} está 28°C, ensolarado."

print("Chat com Tools SEM LangChain (digite 'sair' pra encerrar)\n")

messages = []

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break

    messages.append({"role": "user", "content": pergunta})

    # Loop manual - VOCÊ precisa implementar o loop de tools
    while True:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="Você é um assistente útil que responde em português.",
            tools=tools,
            messages=messages
        )

        # Se o modelo quer chamar tools
        if response.stop_reason == "tool_use":
            # Adiciona a resposta do modelo ao histórico
            messages.append({"role": "assistant", "content": response.content})

            # Processa cada tool call manualmente
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  🔧 Tool chamada: {block.name}({block.input})")
                    resultado = executar_tool(block.name, block.input)
                    print(f"  📦 Resultado: {resultado}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": resultado
                    })

            # Adiciona resultados ao histórico
            messages.append({"role": "user", "content": tool_results})

            # Continua o loop pra o modelo processar os resultados
            continue

        # Se o modelo respondeu direto (sem tools), sai do loop
        texto = ""
        for block in response.content:
            if hasattr(block, "text"):
                texto += block.text
        print(f"Claude: {texto}\n")

        messages.append({"role": "assistant", "content": response.content})
        break