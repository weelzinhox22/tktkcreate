import requests
import json

class LicenseAPI:
    def __init__(self, api_url="https://tktkcreate.onrender.com"):
        self.api_url = api_url
    
    def generate_license(self, type="standard", duration=365, reseller_id=None):
        response = requests.post(f"{self.api_url}/licenses/generate", json={
            "type": type,
            "duration": duration,
            "reseller_id": reseller_id
        })
        return response.json()
    
    def verify_license(self, key):
        response = requests.post(f"{self.api_url}/licenses/verify", json={
            "license_key": key
        })
        return response.json()
    
    def upgrade_license(self, key, new_type):
        response = requests.post(f"{self.api_url}/licenses/upgrade", json={
            "license_key": key,
            "new_type": new_type
        })
        return response.json()
    
    def register_reseller(self, name, email, commission_rate=0.2):
        response = requests.post(f"{self.api_url}/resellers/register", json={
            "name": name,
            "email": email,
            "commission_rate": commission_rate
        })
        return response.json()

# Exemplo de uso:
if __name__ == "__main__":
    api = LicenseAPI()
    
    # Registrar revendedor
    reseller = api.register_reseller("João Silva", "joao@example.com", 0.25)
    print("Revendedor registrado:", reseller)
    
    # Gerar licença através do revendedor
    license = api.generate_license("professional", 365, reseller["reseller_id"])
    print("Licença gerada:", license)
    
    # Verificar licença
    verification = api.verify_license(license["key"])
    print("Verificação:", verification)
    
    # Upgrade de licença
    upgrade = api.upgrade_license(license["key"], "enterprise")
    print("Upgrade:", upgrade) 