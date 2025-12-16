import subprocess
import os
import sys
import requests
import hashlib

URL_GITHUB_RAW = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/Transferencia.01.py"
URL_GITHUB_VERSAO = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/app_version.json"

def calcular_hash(arquivo):
    sha256_hash = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verificar_atualizacao():
    try:
        response = requests.get(URL_GITHUB_VERSAO, timeout=5)
        if response.status_code != 200:
            return False
        
        dados = response.json()
        hash_github = dados.get("hash", "")
        
        script_path = os.path.join(os.path.dirname(__file__), "Transferencia.01.py")
        
        if os.path.exists(script_path):
            hash_local = calcular_hash(script_path)
            
            if hash_github and hash_github != hash_local and hash_github != "exe_build":
                print("Atualizando código...")
                response_script = requests.get(URL_GITHUB_RAW, timeout=10)
                if response_script.status_code == 200:
                    with open(script_path, "w", encoding="utf-8") as f:
                        f.write(response_script.text)
                    print("Código atualizado! Reiniciando...")
                    return True
    except Exception as e:
        print(f"Erro ao verificar atualização: {e}")
    
    return False

if __name__ == "__main__":
    verificar_atualizacao()
    subprocess.run([sys.executable, "Transferencia.01.py"])
