from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os
import secrets
import uuid

app = Flask(__name__)

# Banco de dados de licenças (em memória para exemplo)
LICENSES_DB = {
    "DARKTK-PRO-2024": {
        "type": "Professional",
        "expires": "2025-12-31",
        "features": ["all"]
    },
    "DARKTK-STD-2024": {
        "type": "Standard",
        "expires": "2025-12-31",
        "features": ["basic"]
    }
}

def init_db():
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    # Tabela de licenças
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (key TEXT PRIMARY KEY,
                  type TEXT,
                  expires TEXT,
                  activations INTEGER DEFAULT 0,
                  max_activations INTEGER DEFAULT 3,
                  reseller_id TEXT,
                  created_at TEXT,
                  status TEXT)''')
    
    # Tabela de revendedores
    c.execute('''CREATE TABLE IF NOT EXISTS resellers
                 (id TEXT PRIMARY KEY,
                  name TEXT,
                  email TEXT,
                  commission_rate REAL)''')
    
    # Tabela de uso
    c.execute('''CREATE TABLE IF NOT EXISTS usage_logs
                 (id TEXT PRIMARY KEY,
                  license_key TEXT,
                  action TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def generate_unique_key(order_id):
    """Gera uma chave única baseada no ID do pedido"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    unique_id = hashlib.sha256(f"{order_id}{timestamp}".encode()).hexdigest()[:12]
    return f"DARKTK-{unique_id.upper()}"

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "online", "message": "License server is running"})

@app.route('/licenses/generate', methods=['POST'])
def generate_license():
    try:
        data = request.json
        license_type = data.get('type', 'standard')
        duration_days = data.get('duration', 365)
        reseller_id = data.get('reseller_id')
        max_activations = data.get('max_activations', 3)
        
        # Gerar chave única
        unique_id = str(uuid.uuid4())[:8].upper()
        key = f"DARKTK-{license_type[:3].upper()}-{unique_id}"
        
        # Salvar no banco
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('''INSERT INTO licenses 
                     (key, type, expires, max_activations, reseller_id, created_at, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (key, license_type,
                  (datetime.datetime.now() + datetime.timedelta(days=duration_days)).strftime('%Y-%m-%d'),
                  max_activations, reseller_id,
                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                  'active'))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "key": key,
            "type": license_type,
            "max_activations": max_activations
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/licenses/verify', methods=['POST'])
def verify_license():
    try:
        data = request.json
        key = data.get('license_key')
        
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('SELECT * FROM licenses WHERE key = ?', (key,))
        license_data = c.fetchone()
        
        if license_data:
            # Verificar status e expiração
            expires = datetime.datetime.strptime(license_data[2], '%Y-%m-%d')
            activations = license_data[3]
            max_activations = license_data[4]
            status = license_data[7]
            
            if status == 'active' and expires > datetime.datetime.now() and activations < max_activations:
                # Registrar ativação
                c.execute('UPDATE licenses SET activations = activations + 1 WHERE key = ?', (key,))
                # Registrar uso
                c.execute('''INSERT INTO usage_logs (id, license_key, action, timestamp)
                            VALUES (?, ?, ?, ?)''',
                         (str(uuid.uuid4()), key, 'verify',
                          datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
                
                return jsonify({
                    "valid": True,
                    "type": license_data[1],
                    "expires": license_data[2],
                    "activations": activations + 1,
                    "max_activations": max_activations
                })
        
        conn.close()
        return jsonify({"valid": False})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/licenses/upgrade', methods=['POST'])
def upgrade_license():
    try:
        data = request.json
        key = data.get('license_key')
        new_type = data.get('new_type')
        
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('UPDATE licenses SET type = ? WHERE key = ?', (new_type, key))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "License upgraded successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/resellers/register', methods=['POST'])
def register_reseller():
    try:
        data = request.json
        reseller_id = str(uuid.uuid4())
        
        conn = sqlite3.connect('licenses.db')
        c = conn.cursor()
        c.execute('''INSERT INTO resellers (id, name, email, commission_rate)
                     VALUES (?, ?, ?, ?)''',
                 (reseller_id, data.get('name'), data.get('email'),
                  data.get('commission_rate', 0.2)))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "reseller_id": reseller_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

print(secrets.token_hex(32)) 