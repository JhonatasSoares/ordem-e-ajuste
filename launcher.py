#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import traceback
import threading
import random
import shutil
import subprocess
import hashlib
import warnings
from pathlib import Path
from datetime import datetime

import requests
import pandas as pd
import tkinter as tk
from tkinter import messagebox, scrolledtext

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import keyboard
import pyautogui

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

URL_GITHUB_RAW = "https://raw.githubusercontent.com/JhonatasSoares/ordem-e-ajuste/main/Transferencia.01.py"

def main():
    try:
        print("=" * 60)
        print("🤖 Ordem e Ajuste - Carregando aplicativo...")
        print("=" * 60)
        print()
        print("Baixando código atualizado do GitHub...")
        
        response = requests.get(URL_GITHUB_RAW, timeout=30)
        
        if response.status_code != 200:
            print(f"Erro: Status {response.status_code}")
            print("Verifique sua conexão com a internet.")
            input("\nPressione ENTER para sair...")
            return False
        
        print("✓ Código baixado com sucesso")
        print("Inicializando aplicativo...\n")
        
        exec(response.text, globals())
        return True
        
    except requests.exceptions.Timeout:
        print("Erro: Timeout ao conectar no GitHub")
        print("Verifique sua conexão com a internet.")
        input("\nPressione ENTER para sair...")
        return False
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar no GitHub")
        print("Verifique sua conexão com a internet.")
        input("\nPressione ENTER para sair...")
        return False
    except Exception as e:
        print(f"Erro: {e}")
        print()
        print("Detalhes do erro:")
        traceback.print_exc()
        input("\nPressione ENTER para sair...")
        return False

if __name__ == '__main__':
    main()
