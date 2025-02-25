import json
import os
from datetime import datetime

class LicenseManager:
    def __init__(self):
        self.license_file = "license_data.json"
        self.license_key = None
        self.activation_date = None
        self.is_valid = False
        self.load_license_data()

    def load_license_data(self):
        """Carrega dados da licença do arquivo"""
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    data = json.load(f)
                    self.license_key = data.get('license_key')
                    self.activation_date = data.get('activation_date')
                    self.is_valid = data.get('is_valid', False)
        except Exception as e:
            print(f"Erro ao carregar dados da licença: {e}")
            self.is_valid = False

    def save_license_data(self):
        """Salva dados da licença no arquivo"""
        try:
            data = {
                'license_key': self.license_key,
                'activation_date': self.activation_date,
                'is_valid': self.is_valid
            }
            with open(self.license_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Erro ao salvar dados da licença: {e}")

    def activate_license(self, license_key):
        """Ativa uma nova licença"""
        self.license_key = license_key
        self.activation_date = datetime.now().isoformat()
        self.is_valid = True
        self.save_license_data()

    def deactivate_license(self):
        """Desativa a licença atual"""
        self.license_key = None
        self.activation_date = None
        self.is_valid = False
        self.save_license_data()

    def check_license_validity(self):
        """Verifica se a licença ainda é válida"""
        return self.is_valid and self.license_key is not None

    def get_activation_date(self):
        """Retorna a data de ativação"""
        return self.activation_date

    def get_days_since_activation(self):
        """Retorna o número de dias desde a ativação"""
        if not self.activation_date:
            return 0
        activation = datetime.fromisoformat(self.activation_date)
        delta = datetime.now() - activation
        return delta.days 