import requests

def test_create_license():
    # URL do seu servidor
    api_url = "https://tktkcreate.onrender.com/api/create_license"
    
    # Dados para criar licença
    data = {
        "admin_key": "DARKTK-MASTER-2024",
        "email": "teste@exemplo.com",
        "type": "professional",
        "duration": 30,
        "purchase_id": "TESTE-123"
    }
    
    try:
        print("Tentando criar licença...")
        response = requests.post(api_url, json=data)
        
        print(f"Status code: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code == 200:
            license_data = response.json()
            print("\nLicença criada com sucesso!")
            print(f"Chave: {license_data['license_key']}")
            print(f"Expira em: {license_data['expires_at']}")
            
            # Testar a verificação
            verify_url = "https://tktkcreate.onrender.com/api/verify_license"
            verify_response = requests.post(
                verify_url,
                json={"key": license_data['license_key']}
            )
            print("\nTestando verificação...")
            print(f"Status: {verify_response.status_code}")
            print(f"Resposta: {verify_response.text}")
            
    except Exception as e:
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    test_create_license() 