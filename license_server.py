from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (license_key TEXT PRIMARY KEY, email TEXT, status TEXT, expires_at TEXT, purchase_id TEXT, trial_period INTEGER)''')
    conn.commit()
    conn.close()

@app.route('/create_license', methods=['POST'])
def create_license():
    data = request.json
    email = data['email']
    purchase_id = data['purchase_id']
    license_key = generate_license_key(purchase_id)
    expires_at = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
    trial_period = 7  # 7 days trial

    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('INSERT INTO licenses (license_key, email, status, expires_at, purchase_id, trial_period) VALUES (?, ?, ?, ?, ?, ?)',
              (license_key, email, 'active', expires_at, purchase_id, trial_period))
    conn.commit()
    conn.close()

    return jsonify({"license_key": license_key})

@app.route('/verify_license', methods=['POST'])
def verify_license():
    data = request.json
    license_key = data['license_key']

    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('SELECT status, expires_at FROM licenses WHERE license_key = ?', (license_key,))
    result = c.fetchone()
    conn.close()

    if result and result[0] == 'active' and datetime.strptime(result[1], '%Y-%m-%d') > datetime.now():
        return jsonify({"valid": True})
    return jsonify({"valid": False})

@app.route('/revoke_license', methods=['POST'])
def revoke_license():
    data = request.json
    license_key = data['license_key']

    conn = sqlite3.connect('licenses.db')
    c = conn.cursor()
    c.execute('UPDATE licenses SET status = "revoked" WHERE license_key = ?', (license_key,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

def generate_license_key(purchase_id):
    return f"LIC-{purchase_id[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 