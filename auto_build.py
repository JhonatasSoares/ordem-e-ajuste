import subprocess
import os
import shutil
from pathlib import Path

projeto_dir = r"c:\Users\NNSoaresJh\OneDrive - NESTLE\Área de Trabalho\Code Ordem e ajuste"
os.chdir(projeto_dir)

print("Limpando builds anteriores...")
for pasta in ["build", "dist"]:
    if os.path.exists(pasta):
        shutil.rmtree(pasta, ignore_errors=True)

for spec_file in Path(".").glob("*.spec"):
    try:
        spec_file.unlink()
    except:
        pass

print("Gerando executável...")
resultado = subprocess.run(["python", "-m", "PyInstaller", "--onefile", "--windowed", "Transferencia.01.py"], capture_output=True, text=True)

if resultado.returncode == 0:
    print("\n✅ Executável criado com sucesso!")
    print("📁 Caminho: dist/Transferencia.01.exe")
    
    print("\n⏳ Atualizando no GitHub...")
    
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(["git", "commit", "-m", "Update: versão com sistema de logs de verificação"], capture_output=True)
    subprocess.run(["git", "push"], capture_output=True)
    
    print("✅ Enviado para GitHub!")
else:
    print("❌ Erro ao gerar executável")
    print(resultado.stderr)
