from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os
import secrets

app = Flask(__name__)

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
    try:
        data = request.json
        order_id = data.get('order_id')
        
        # Gerar chave única
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        unique_id = hashlib.sha256(f"{order_id}{timestamp}".encode()).hexdigest()[:12]
        key = f"DARKTK-{unique_id.upper()}"
        
        return jsonify({
            "success": True,
            "key": key,
            "message": "License generated successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/licenses/verify', methods=['POST'])
def verify_license():
    try:
        data = request.json
        key = data.get('license_key')
        
        # Simples verificação de formato
        if key and key.startswith("DARKTK-"):
            return jsonify({
                "valid": True,
                "license_data": {
                    "type": "standard",
                    "expires": "2025-12-31"
                }
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