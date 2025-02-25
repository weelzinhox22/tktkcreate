from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import uuid
import os

app = Flask(__name__)

# Configurar banco de dados
DATABASE_PATH = 'data/licenses.db'

def init_db():
    # Garantir que o diretório existe
    os.makedirs('data', exist_ok=True)
    
    with sqlite3.connect(DATABASE_PATH) as conn:
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
        conn.commit()

def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

# Inicializar banco de dados na inicialização
init_db()

@app.route('/api/verify_license', methods=['POST'])
def verify_license():
    data = request.json
    key = data.get('key')
    
    try:
        db = get_db()
        cursor = db.cursor()
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
        db.commit()
        
        return jsonify({
            'valid': True,
            'type': license['type'],
            'expires_at': license['expires_at']
        })
    except Exception as e:
        print(f"Erro na verificação: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/create_license', methods=['POST'])
def create_license():
    data = request.json
    admin_key = data.get('admin_key')
    
    if admin_key != 'DARKTK-MASTER-2024':
        return jsonify({'error': 'Acesso negado'}), 401
    
    try:
        email = data.get('email')
        license_type = data.get('type', 'standard')
        duration_days = data.get('duration', 30)
        purchase_id = data.get('purchase_id')
        
        license_key = f"DARKTK-{uuid.uuid4().hex[:8].upper()}"
        expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat()
        
        db = get_db()
        cursor = db.cursor()
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
        db.commit()
        
        return jsonify({
            'success': True,
            'license_key': license_key,
            'expires_at': expires_at
        })
    except Exception as e:
        print(f"Erro na criação: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/list_licenses', methods=['GET'])
def list_licenses():
    admin_key = request.args.get('admin_key')
    
    if admin_key != 'DARKTK-MASTER-2024':
        return jsonify({'error': 'Acesso negado'}), 401
    
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM licenses')
        licenses = cursor.fetchall()
        
        return jsonify([dict(lic) for lic in licenses])
    except Exception as e:
        print(f"Erro na listagem: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/revoke_license', methods=['POST'])
def revoke_license():
    data = request.json
    admin_key = data.get('admin_key')
    
    if admin_key != 'DARKTK-MASTER-2024':
        return jsonify({'error': 'Acesso negado'}), 401
    
    try:
        key = data.get('key')
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'UPDATE licenses SET status = "revoked" WHERE key = ?',
            (key,)
        )
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Erro na revogação: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 