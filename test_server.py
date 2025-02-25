import requests

BASE_URL = "https://tktkcreate.onrender.com"

def test_generate_license():
    # Teste de geração de licença
    response = requests.post(f"{BASE_URL}/licenses/generate", 
        json={
            "order_id": "TEST-001",
            "type": "standard"
        }
    )
    print("Gerando licença:", response.json())
    return response.json().get('key')

def test_verify_license(key):
    # Teste de verificação de licença
    response = requests.post(f"{BASE_URL}/licenses/verify", 
        json={
            "license_key": key
        }
    )
    print("Verificando licença:", response.json())

def run_tests():
    print("Iniciando testes...")
    key = test_generate_license()
    if key:
        test_verify_license(key)

if __name__ == "__main__":
    run_tests() 