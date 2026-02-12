from langchain_ollama import ChatOllama

# Configuração do modelo Ollama para o LangChain
llm = ChatOllama(
    model="qwen2.5-coder:7b",
    temperature=0.1,
    num_predict=1024,
)
