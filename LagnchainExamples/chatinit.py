from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model

llm = init_chat_model(
    "anthropic:claude-haiku-4-5-20251001",
    temperature=0.2,
    max_tokens=500,
)

print("Chat com temperatura baixa (digite 'sair' pra encerrar)\n")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break
    resposta = llm.invoke(pergunta)
    print(f"Claude: {resposta.content}\n")