import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

from src.license_activation import LicenseActivation
import logging

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_license():
    try:
        activation = LicenseActivation()
        
        # Teste com uma licença de teste
        print("Testando licença válida...")
        success, message = activation.activate('TEST-1234-5678-9ABC')
        print(f"Resultado: {success}")
        print(f"Mensagem: {message}")
        
        # Teste com uma licença inválida
        print("\nTestando licença inválida...")
        success, message = activation.activate('INVALID-KEY')
        print(f"Resultado: {success}")
        print(f"Mensagem: {message}")
        
    except Exception as e:
        print(f"Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_license() 