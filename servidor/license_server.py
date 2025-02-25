from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import uuid
import os

app = Flask(__name__)

# Configurar banco de dados
def init_db():
    with sqlite3.connect('licenses.db') as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            key TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            last_check TEXT,
            purchase_id TEXT
        )
        ''')

init_db()

@app.route('/api/verify_license', methods=['POST'])
def verify_license():
    data = request.json
    key = data.get('key')
    
    with sqlite3.connect('licenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM licenses WHERE key = ? AND status = "active"',
            (key,)
        )
        license = cursor.fetchone()
        
        if not license:
            return jsonify({
                'valid': False,
                'message': 'Licença inválida ou desativada'
            }), 401
            
        cursor.execute(
            'UPDATE licenses SET last_check = ? WHERE key = ?',
            (datetime.now().isoformat(), key)
        )
        conn.commit()
        
        return jsonify({
            'valid': True,
            'type': license[3],
            'expires_at': license[6]
        })

@app.route('/api/create_license', methods=['POST'])
def create_license():
    data = request.json
    admin_key = data.get('admin_key')
    
    if admin_key != 'DARKTK-MASTER-2024':
        return jsonify({'error': 'Acesso negado'}), 401
    
    email = data.get('email')
    license_type = data.get('type', 'standard')
    duration_days = data.get('duration', 30)
    purchase_id = data.get('purchase_id')
    
    license_key = f"DARKTK-{uuid.uuid4().hex[:8].upper()}"
    expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
    
    with sqlite3.connect('licenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO licenses (id, email, key, type, status, created_at, expires_at, purchase_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            email,
            license_key,
            license_type,
            'active',
            datetime.now().isoformat(),
            expires_at,
            purchase_id
        ))
        conn.commit()
    
    return jsonify({
        'success': True,
        'license_key': license_key,
        'expires_at': expires_at
    })

@app.route('/api/list_licenses', methods=['GET'])
def list_licenses():
    admin_key = request.args.get('admin_key')
    
    if admin_key != 'DARKTK-MASTER-2024':
        return jsonify({'error': 'Acesso negado'}), 401
    
    with sqlite3.connect('licenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM licenses')
        licenses = cursor.fetchall()
        
        return jsonify([{
            'id': lic[0],
            'email': lic[1],
            'key': lic[2],
            'type': lic[3],
            'status': lic[4],
            'created_at': lic[5],
            'expires_at': lic[6],
            'last_check': lic[7],
            'purchase_id': lic[8]
        } for lic in licenses])

@app.route('/api/revoke_license', methods=['POST'])
def revoke_license():
    data = request.json
    admin_key = data.get('admin_key')
    
    if admin_key != 'DARKTK-MASTER-2024':
        return jsonify({'error': 'Acesso negado'}), 401
    
    key = data.get('key')
    
    with sqlite3.connect('licenses.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE licenses SET status = "revoked" WHERE key = ?',
            (key,)
        )
        conn.commit()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 