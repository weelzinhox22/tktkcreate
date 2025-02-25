import requests
import json

def generate_new_license(type="professional", duration=365):
    response = requests.post(
        "https://tktkcreate.onrender.com/licenses/generate",
        json={
            "type": type,
            "duration": duration
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Nova licença gerada:")
        print(f"Chave: {data['key']}")
        print(f"Tipo: {data['license_data']['type']}")
        print(f"Expira em: {data['license_data']['expires']}")
    else:
        print("Erro ao gerar licença:", response.text)

if __name__ == "__main__":
    # Gerar licença profissional por 1 ano
    generate_new_license("professional", 365)
    
    # Gerar licença standard por 30 dias
    generate_new_license("standard", 30) 