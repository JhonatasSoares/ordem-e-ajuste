import hashlib
import json
import subprocess
import os
import shutil
from datetime import datetime
from pathlib import Path

SCRIPT_FILE = "Transferencia.01.py"
VERSION_FILE = "app_version.json"

def calcular_hash(arquivo):
    sha256_hash = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def atualizar_versao():
    novo_hash = calcular_hash(SCRIPT_FILE)
    timestamp = datetime.now().isoformat()
    
    dados = {
        "hash": novo_hash,
        "timestamp": timestamp
    }
    
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)
    
    print(f"Hash atualizado: {novo_hash}")

def fazer_commit(mensagem):
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", mensagem], check=True, capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)
        print(f"Commit e push realizados: {mensagem}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro no Git: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("ATUALIZAR E FAZER PUSH PARA GITHUB")
    print("="*60)
    
    mensagem = input("\nDigite a mensagem de commit: ").strip()
    
    if not mensagem:
        print("Mensagem vazia. Abortado.")
        exit(1)
    
    print("Processando...")
    
    atualizar_versao()
    fazer_commit(mensagem)
    
    print("\n" + "="*60)
    print("TUDO PRONTO! APP ATUALIZADO.")
    print("="*60)
