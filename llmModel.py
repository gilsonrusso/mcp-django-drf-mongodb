from llama_index.llms.ollama import Ollama


llm = Ollama(
    model="qwen2.5-coder:7b",
    request_timeout=120.0,
    context_window=8000,
    # Forçamos parâmetros simples para modelos que não suportam 'thinking' tags
    additional_kwargs={"num_predict": 1024, "temperature": 0.1},
)
