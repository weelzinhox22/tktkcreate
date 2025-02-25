import uuid
import hashlib
import platform
import subprocess

def generate_license_key():
    """Gera uma chave de licença única"""
    return str(uuid.uuid4()).upper()

def get_hardware_id():
    """Gera um ID único baseado no hardware do computador"""
    system = platform.system()
    
    if system == "Windows":
        # Obtém serial do HD e CPU ID no Windows
        cmd = 'wmic csproduct get uuid'
        uuid = subprocess.check_output(cmd, shell=True).decode()
        uuid = uuid.split('\n')[1].strip()
        
        cmd = 'wmic diskdrive get serialnumber'
        hd_serial = subprocess.check_output(cmd, shell=True).decode()
        hd_serial = hd_serial.split('\n')[1].strip()
        
        hardware_id = f"{uuid}-{hd_serial}"
    else:
        # Para Linux/Mac
        cmd = "dmidecode -s system-uuid"
        uuid = subprocess.check_output(cmd, shell=True).decode().strip()
        hardware_id = uuid
    
    # Cria um hash do hardware_id
    return hashlib.sha256(hardware_id.encode()).hexdigest() 