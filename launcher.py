#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests

URL_GITHUB_RAW = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/Transferencia.01.py"

def main():
    try:
        print("Baixando código do GitHub...")
        response = requests.get(URL_GITHUB_RAW, timeout=10)
        
        if response.status_code != 200:
            print(f"Erro: Status {response.status_code}")
            return
        
        print("Executando aplicativo...")
        
        # Define variáveis globais necessárias
        globals_dict = {
            '__name__': '__main__',
            '__file__': 'Transferencia.01.py',
            '__cached__': None,
            '__loader__': None,
            '__package__': None,
            '__spec__': None,
        }
        
        # Executa o código
        exec(response.text, globals_dict)
        
    except KeyboardInterrupt:
        print("Encerrando...")
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
