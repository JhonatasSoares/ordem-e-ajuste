import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

SCRIPT_FILE = "Transferencia.01.py"
VERSION_FILE = "app_version.json"
REQUIREMENTS_FILE = "requirements.txt"
LAST_IMPORTS_FILE = ".last_imports.json"

def calcular_hash(arquivo):
    sha256_hash = hashlib.sha256()
    with open(arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def extrair_imports():
    imports = set()
    try:
        with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith("import ") or linha.startswith("from "):
                    imports.add(linha)
    except Exception as e:
        print(f"⚠️ Erro ao ler imports: {e}")
    return sorted(list(imports))

def verificar_mudanca_dependencias():
    imports_atuais = extrair_imports()
    
    if not Path(LAST_IMPORTS_FILE).exists():
        with open(LAST_IMPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(imports_atuais, f, indent=2)
        return True
    
    with open(LAST_IMPORTS_FILE, "r", encoding="utf-8") as f:
        imports_anteriores = json.load(f)
    
    if imports_atuais != imports_anteriores:
        with open(LAST_IMPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(imports_atuais, f, indent=2)
        return True
    
    return False

def atualizar_versao():
    novo_hash = calcular_hash(SCRIPT_FILE)
    timestamp = datetime.now().isoformat()
    
    dados = {
        "hash": novo_hash,
        "timestamp": timestamp
    }
    
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)
    
    print(f"✅ Hash atualizado: {novo_hash}")
    print(f"✅ Timestamp: {timestamp}")

def fazer_commit(mensagem):
    try:
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", mensagem], check=True, capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)
        print(f"✅ Commit realizado e enviado: {mensagem}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")

def gerar_exe():
    try:
        print("🔨 Gerando executável...")
        subprocess.run(["python", "-m", "PyInstaller", "--onefile", "--windowed", SCRIPT_FILE], check=True)
        print("✅ Executável criado em: dist/Transferencia.01.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar .exe: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Atualizar e Fazer Push para GitHub")
    print("=" * 50)
    
    mensagem = input("\n📝 Digite a mensagem de commit (ex: Fix: corrigir erro de login): ").strip()
    
    if not mensagem:
        print("❌ Mensagem vazia. Abortado.")
        exit(1)
    
    print("\n⏳ Processando...")
    
    atualizar_versao()
    fazer_commit(mensagem)
    
    if verificar_mudanca_dependencias():
        print("\n⚠️  Detalhadas mudanças nas dependências!")
        gerar_exe_opcao = input("🔨 Gerar novo .exe? (s/n): ").strip().lower()
        if gerar_exe_opcao == "s":
            gerar_exe()
    else:
        print("\n✨ Nenhuma mudança de dependências detectada.")
        print("   (Usuários receberão atualização automática do .py)")
    
    print("\n" + "=" * 50)
    print("✅ Tudo pronto! Seu app foi atualizado.")
    print("=" * 50)
