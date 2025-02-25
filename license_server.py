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
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (key TEXT PRIMARY KEY, order_id TEXT, 
                  type TEXT, expires TEXT, active INTEGER)''')
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
    """Gera uma nova licença"""
    try:
        data = request.json
        license_type = data.get('type', 'standard')
        duration_days = data.get('duration', 365)
        
        # Gerar chave única
        unique_id = str(uuid.uuid4())[:8].upper()
        key = f"DARKTK-{license_type[:3].upper()}-{unique_id}"
        
        # Calcular data de expiração
        expiry_date = (datetime.datetime.now() + 
                      datetime.timedelta(days=duration_days)).strftime('%Y-%m-%d')
        
        # Definir features baseado no tipo
        features = ["all"] if license_type.lower() == "professional" else ["basic"]
        
        # Salvar licença
        LICENSES_DB[key] = {
            "type": license_type,
            "expires": expiry_date,
            "features": features
        }
        
        return jsonify({
            "success": True,
            "key": key,
            "license_data": LICENSES_DB[key]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/licenses/verify', methods=['POST'])
def verify_license():
    """Verifica uma licença"""
    try:
        data = request.json
        key = data.get('license_key')
        
        if key in LICENSES_DB:
            license_data = LICENSES_DB[key]
            # Verificar expiração
            expiry = datetime.datetime.strptime(license_data['expires'], '%Y-%m-%d')
            if expiry > datetime.datetime.now():
                return jsonify({
                    "valid": True,
                    "license_data": license_data
                })
        
        return jsonify({"valid": False})
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/licenses/deactivate', methods=['POST'])
def deactivate_license():
    data = request.json
    order_id = data.get('order_id')
    
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('UPDATE licenses SET active = 0 WHERE order_id = ?', (order_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

print(secrets.token_hex(32)) 