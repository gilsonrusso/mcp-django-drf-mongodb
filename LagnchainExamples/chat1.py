from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-haiku-4-5-20251001")

print("Chat com Claude (digite 'sair' pra encerrar)\n")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == "sair":
        break
    resposta = llm.invoke(pergunta)
    print(f"Claude: {resposta.content}\n")