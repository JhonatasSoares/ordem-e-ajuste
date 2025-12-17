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
    except Exception as e:
        print(f"Erro ao baixar: {e}")
    
    return None

if __name__ == "__main__":
    script_path = baixar_codigo_github()
    
    if script_path:
        try:
            subprocess.run([sys.executable, script_path])
        except Exception as e:
            print(f"Erro ao executar: {e}")
            input("Pressione Enter para sair...")
    else:
        print("Falha ao carregar código.")
        input("Pressione Enter para sair...")
