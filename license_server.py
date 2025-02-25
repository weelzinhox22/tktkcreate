from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import hashlib
import os

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

@app.route('/licenses/generate', methods=['POST'])
def generate_license():
    data = request.json
    order_id = data.get('order_id')
    license_type = data.get('type', 'standard')
    
    # Gerar chave única
    key = generate_unique_key(order_id)
    
    # Salvar no banco
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('''INSERT INTO licenses (key, order_id, type, expires, active)
                 VALUES (?, ?, ?, ?, ?)''',
              (key, order_id, license_type, 
               (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
               1))
    conn.commit()
    conn.close()
    
    return jsonify({"key": key})

@app.route('/licenses/verify', methods=['POST'])
def verify_license():
    data = request.json
    key = data.get('license_key')
    
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM licenses WHERE key = ? AND active = 1', (key,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            "valid": True,
            "license_data": {
                "type": result[2],
                "expires": result[3]
            }
        })
    return jsonify({"valid": False})

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