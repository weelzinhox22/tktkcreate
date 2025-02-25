from flask import Flask, request, jsonify
import sys
from pathlib import Path
import logging
import requests

# Configuração de logging mais detalhada
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adiciona o diretório src ao PYTHONPATH
src_dir = Path(__file__).parent.parent
sys.path.append(str(src_dir))

from database.db_manager import DatabaseManager

app = Flask(__name__)
db = DatabaseManager()

@app.route('/validate_license', methods=['POST'])
def validate_license():
    try:
        data = request.get_json()
        logger.debug(f"Dados recebidos na validação: {data}")
        
        license_key = data.get('license_key')
        hardware_id = data.get('hardware_id')
        
        logger.debug(f"Verificando licença: {license_key}")
        logger.debug(f"Hardware ID recebido: {hardware_id}")
        
        # Verifica se a chave foi fornecida
        if not license_key:
            logger.warning("Chave de licença não fornecida")
            return jsonify({
                'valid': False,
                'message': 'Chave de licença não fornecida'
            })

        # Valida o formato da chave
        if not db.validate_license_format(license_key):
            logger.debug(f"Formato inválido para chave: {license_key}")
            return jsonify({
                'valid': False,
                'message': 'Formato de chave inválido. Use o formato: XXXX-XXXX-XXXX-XXXX'
            })
        
        # Verifica licença no banco
        license = db.get_license(license_key)
        logger.debug(f"Resultado da busca no banco: {license}")
        
        if not license:
            logger.warning(f"Licença não encontrada: {license_key}")
            return jsonify({
                'valid': False,
                'message': 'Chave de licença não encontrada. Verifique se digitou corretamente.'
            })
        
        if license['status'] == 'revoked':
            logger.warning(f"Licença revogada: {license_key}")
            return jsonify({
                'valid': False,
                'message': 'Esta licença foi revogada. Entre em contato com o suporte.'
            })
        
        # Verifica se a licença já está em uso em outro computador
        if license['hardware_id'] and license['hardware_id'] != hardware_id:
            return jsonify({
                'valid': False,
                'message': 'Esta licença já está em uso em outro computador.'
            })
        
        logger.info(f"Licença válida: {license_key}")
        return jsonify({
            'valid': True,
            'message': 'Licença válida!'
        })
        
    except Exception as e:
        logger.error(f"Erro ao validar licença: {str(e)}")
        return jsonify({
            'valid': False,
            'message': f'Erro ao validar licença: {str(e)}'
        })

@app.route('/revoke_license', methods=['POST'])
def revoke_license():
    license_key = request.json['license_key']
    db.update_license_status(license_key, 'revoked')
    return jsonify({'success': True})

@app.route('/test_connection', methods=['GET'])
def test_connection():
    logger.debug("Teste de conexão recebido")
    return jsonify({
        'status': 'online',
        'message': 'Servidor funcionando corretamente'
    })

# Remova ou comente estas linhas de teste do arquivo api.py
# def test_license(license_key):
#     response = requests.post(
#         'http://localhost:5000/validate_license',
#         json={
#             'license_key': license_key,
#             'hardware_id': 'TEST-HARDWARE-ID'
#         }
#     )
#     print(response.json())

# # Teste com uma chave válida
# test_license('TEST-1234-5678-9ABC')

# # Teste com uma chave inválida
# test_license('INVALID-KEY')

if __name__ == '__main__':
    logger.info("Iniciando servidor de licenças...")
    app.run(debug=True) 