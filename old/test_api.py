import requests

API_URL = "http://localhost:8000/api/tasks/"

def test_api():
    print("--- Testando Conexão com a API Django ---")
    try:
        # 1. Testar Listagem
        response = requests.get(API_URL)
        print(f"Status GET: {response.status_code}")
        print(f"Tarefas Atuais: {response.json()}")
        
        # 2. Testar Criação
        if response.status_code == 200:
            data = {"title": "Tarefa de Teste Debug", "description": "Criada pelo script de teste"}
            post_resp = requests.post(API_URL, json=data)
            print(f"Status POST: {post_resp.status_code}")
            print(f"Resposta POST: {post_resp.json()}")
            
    except Exception as e:
        print(f"ERRO DE CONEXÃO: {e}")

if __name__ == "__main__":
    test_api()
