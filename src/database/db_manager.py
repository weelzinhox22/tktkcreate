import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        # Garante que o diretório existe
        os.makedirs('data', exist_ok=True)
        self.db_path = 'data/licenses.db'
        
        # Apaga o banco existente para recriá-lo corretamente
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            
        self.init_db()
        self.create_test_licenses()

    def init_db(self):
        """Inicializa o banco de dados com a tabela necessária"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cria a tabela com todas as colunas necessárias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                user_id TEXT,
                purchase_date TEXT,
                activation_date TEXT,
                status TEXT,
                hardware_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_test_licenses(self):
        """Cria algumas licenças de teste"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insere licenças de teste
        test_licenses = [
            ('TEST-1234-5678-9ABC', 'test_user', datetime.now().isoformat(), None, 'active', None),
            ('DEMO-1234-5678-9ABC', 'demo_user', datetime.now().isoformat(), None, 'active', None)
        ]

        cursor.executemany('''
            INSERT OR REPLACE INTO licenses 
            (license_key, user_id, purchase_date, activation_date, status, hardware_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', test_licenses)

        conn.commit()
        conn.close()

    def get_license(self, license_key):
        """Busca uma licença no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM licenses WHERE license_key = ?', (license_key,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'license_key': result[0],
                'user_id': result[1],
                'purchase_date': result[2],
                'activation_date': result[3],
                'status': result[4],
                'hardware_id': result[5]
            }
        return None

    def update_license_status(self, license_key, status):
        """Atualiza o status de uma licença"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE licenses SET status = ? WHERE license_key = ?',
            (status, license_key)
        )
        
        conn.commit()
        conn.close()

    def validate_license_format(self, license_key):
        """Valida o formato da chave de licença"""
        # Verifica se a chave tem o formato correto (exemplo: XXXX-XXXX-XXXX-XXXX)
        parts = license_key.split('-')
        if len(parts) != 4 or not all(len(part) == 4 for part in parts):
            return False
        return True 