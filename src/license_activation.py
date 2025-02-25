import sys
from pathlib import Path

# Adiciona o diretório src ao PYTHONPATH
src_dir = Path(__file__).parent
sys.path.append(str(src_dir))

from utils.license_generator import get_hardware_id
from .license_manager import LicenseManager
import requests
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LicenseActivation:
    def __init__(self):
        self.license_manager = LicenseManager()
        self.server_url = "http://localhost:5000"  # Atualizado para usar localhost
        
    def activate(self, license_key):
        """Ativa a licença no computador atual"""
        try:
            hardware_id = get_hardware_id()
            logger.debug(f"Tentando ativar licença: {license_key}")
            logger.debug(f"Hardware ID: {hardware_id}")
            logger.debug(f"Servidor: {self.server_url}")
            
            # Primeiro, testa a conexão com o servidor
            try:
                test_response = requests.get(f"{self.server_url}/test_connection")
                logger.debug(f"Teste de conexão: {test_response.status_code}")
            except Exception as e:
                logger.error(f"Erro ao conectar ao servidor: {e}")
                return False, "Erro ao conectar ao servidor. Verifique sua conexão."
            
            # Verifica com o servidor
            data = {
                "license_key": license_key,
                "hardware_id": hardware_id
            }
            logger.debug(f"Enviando dados: {data}")
            
            response = requests.post(
                f"{self.server_url}/validate_license",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10  # Adiciona timeout
            )
            
            logger.debug(f"Resposta do servidor: {response.status_code}")
            logger.debug(f"Conteúdo da resposta: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result["valid"]:
                    # Salva localmente
                    self.license_manager.activate_license(license_key)
                    return True, "Licença ativada com sucesso!"
                return False, result.get("message", "Licença inválida")
            
            return False, f"Erro ao conectar ao servidor: {response.status_code}"
            
        except Exception as e:
            logger.error(f"Erro durante ativação: {str(e)}")
            return False, f"Erro durante ativação: {str(e)}"

    def check_license(self):
        """Verifica se a licença ainda é válida"""
        try:
            if not self.license_manager.is_valid:
                return False
            
            hardware_id = get_hardware_id()
            response = requests.post(
                f"{self.server_url}/validate_license",
                json={
                    "license_key": self.license_manager.license_key,
                    "hardware_id": hardware_id
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["valid"]
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar licença: {str(e)}")
            return False 