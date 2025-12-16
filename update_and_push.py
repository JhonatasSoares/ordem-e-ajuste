import hashlib
import json
import subprocess
import os
import shutil
from datetime import datetime
from pathlib import Path

SCRIPT_FILE = "Transferencia.01.py"
VERSION_FILE = "app_version.json"
REQUIREMENTS_FILE = "requirements.txt"
LAST_IMPORTS_FILE = ".last_imports.json"
GITHUB_REPO = "JhonatasPSoares/ordem-e-ajuste"

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

def atualizar_versao(com_exe=False):
    if com_exe:
        novo_hash = "exe_build"
    else:
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no Git: {e}")
        return False

def gerar_exe():
    try:
        print("🔨 Gerando executável...")
        
        if os.path.exists("build"):
            shutil.rmtree("build", ignore_errors=True)
        if os.path.exists("dist"):
            shutil.rmtree("dist", ignore_errors=True)
        for spec_file in Path(".").glob("*.spec"):
            try:
                spec_file.unlink()
            except:
                pass
        
        subprocess.run(["python", "-m", "PyInstaller", "--onefile", "--windowed", SCRIPT_FILE], check=True)
        print("✅ Executável criado em: dist/Transferencia.01.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar .exe: {e}")
        return False

def fazer_release_git(tag="latest"):
    try:
        exe_path = "dist/Transferencia.01.exe"
        
        if not os.path.exists(exe_path):
            print(f"❌ Arquivo {exe_path} não encontrado!")
            return False
        
        print(f"\n📤 Fazendo release via Git com tag '{tag}'...")
        
        subprocess.run(["git", "add", exe_path], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Release: {tag} - novo executável"], check=True, capture_output=True)
        
        subprocess.run(["git", "tag", "-d", tag], capture_output=True)
        subprocess.run(["git", "push", "origin", f":{tag}"], capture_output=True)
        
        subprocess.run(["git", "tag", tag], check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", tag], check=True, capture_output=True)
        
        print(f"✅ Release '{tag}' criada com sucesso!")
        print(f"✅ .exe armazenado no repositório Git")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar release: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 ATUALIZAR E FAZER PUSH PARA GITHUB")
    print("=" * 60)
    
    mensagem = input("\n📝 Digite a mensagem de commit (ex: Update: versão 2.5.2): ").strip()
    
    if not mensagem:
        print("❌ Mensagem vazia. Abortado.")
        exit(1)
    
    print("\n⏳ Processando...")
    
    tem_mudanca_deps = verificar_mudanca_dependencias()
    
    if tem_mudanca_deps:
        print("\n⚠️  Detectadas mudanças nas dependências!")
        atualizar_versao(com_exe=True)
        
        if gerar_exe():
            fazer_commit(mensagem)
            print("\n🔗 Criando release no Git...")
            fazer_release_git()
    else:
        print("\n✨ Nenhuma mudança de dependências detectada.")
        atualizar_versao(com_exe=False)
        fazer_commit(mensagem)
        print("   (Usuários receberão atualização automática do .py)")
    
    print("\n" + "=" * 60)
    print("✅ TUDO PRONTO! SEU APP FOI ATUALIZADO.")
    print("=" * 60)
    print("\n📌 Resumo:")
    print("   - Código atualizado no GitHub")
    print("   - .exe armazenado no repositório (se houver mudança de dependências)")
    print("   - Usuários receberão atualização automática na próxima execução")
