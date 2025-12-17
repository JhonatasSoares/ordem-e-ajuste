import subprocess
import os
import sys
import requests
import hashlib
import tempfile

URL_GITHUB_RAW = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/Transferencia.01.py"
URL_GITHUB_VERSAO = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/app_version.json"

def baixar_codigo_github():
    """Baixa o código mais recente do GitHub."""
    try:
        print("Verificando atualizações...")
        response = requests.get(URL_GITHUB_RAW, timeout=10)
        
        if response.status_code == 200:
            print("Código atualizado carregado!")
            return response.text
    except Exception as e:
        print(f"Erro ao baixar: {e}")
    
    return None

def executar_codigo_dinamico(codigo):
    """Executa o código Python dinamicamente com __file__ definido."""
    try:
        exec_globals = {
            '__name__': '__main__',
            '__file__': os.path.join(os.path.dirname(__file__), 'Transferencia.01.py'),
            '__cached__': None,
            '__package__': None
        }
        exec(codigo, exec_globals)
    except Exception as e:
        print(f"Erro ao executar código: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    codigo = baixar_codigo_github()
    
    if codigo:
        executar_codigo_dinamico(codigo)
    else:
        print("Falha ao carregar código. Tente novamente.")
        input("Pressione Enter para sair...")
