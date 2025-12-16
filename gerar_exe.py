import subprocess
import os
import shutil
from pathlib import Path
import stat
import time

projeto_dir = r"c:\Users\NNSoaresJh\OneDrive - NESTLE\Área de Trabalho\Code Ordem e ajuste"

os.chdir(projeto_dir)

def remover_pasta(pasta):
    try:
        shutil.rmtree(pasta, ignore_errors=True)
        time.sleep(0.5)
        if os.path.exists(pasta):
            for root, dirs, files in os.walk(pasta, topdown=False):
                for arquivo in files:
                    caminho = os.path.join(root, arquivo)
                    try:
                        os.chmod(caminho, stat.S_IWRITE)
                        os.remove(caminho)
                    except:
                        pass
                for d in dirs:
                    try:
                        os.rmdir(os.path.join(root, d))
                    except:
                        pass
            try:
                os.rmdir(pasta)
            except:
                pass
    except:
        pass

for pasta in ["build", "dist"]:
    if os.path.exists(pasta):
        print(f"Removendo {pasta}...")
        remover_pasta(pasta)
        
for spec_file in Path(".").glob("*.spec"):
    try:
        spec_file.unlink()
    except:
        pass

print("🔨 Gerando novo executável...")
resultado = subprocess.run([
    "python", "-m", "PyInstaller", 
    "--onefile", 
    "--windowed", 
    "Transferencia.01.py"
])

if resultado.returncode == 0:
    print("\n" + "="*60)
    print("✅ EXECUTÁVEL CRIADO COM SUCESSO!")
    print("="*60)
    print(f"\nCaminho: {projeto_dir}\\dist\\Transferencia.01.exe")
    print("\nPróximo passo:")
    print("1. Execute: python update_and_push.py")
    print("2. Ele fará upload automático para GitHub")
else:
    print("❌ Erro ao gerar executável")

input("\nPressione Enter para fechar...")
