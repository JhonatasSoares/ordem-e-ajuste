import subprocess
import os
import sys
import requests

URL_GITHUB_RAW = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/Transferencia.01.py"
TEMP_SCRIPT = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "app_temp.py")

def baixar_codigo_github():
    """Baixa o código mais recente do GitHub."""
    try:
        print("Verificando atualizações...")
        response = requests.get(URL_GITHUB_RAW, timeout=10)
        
        if response.status_code == 200:
            print("Código atualizado carregado!")
            os.makedirs(os.path.dirname(TEMP_SCRIPT), exist_ok=True)
            with open(TEMP_SCRIPT, "w", encoding="utf-8") as f:
                f.write(response.text)
            return TEMP_SCRIPT
        else:
            print(f"Erro: Status {response.status_code}")
    except Exception as e:
        print(f"Erro ao baixar: {e}")
    
    return None

if __name__ == "__main__":
    try:
        script_path = baixar_codigo_github()
        
        if script_path:
            print(f"Executando: {script_path}")
            resultado = subprocess.run([sys.executable, script_path], capture_output=False)
            print(f"Código encerrado com status: {resultado.returncode}")
        else:
            print("Falha ao carregar código.")
            input("Pressione Enter para sair...")
    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")
