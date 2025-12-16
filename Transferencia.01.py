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
from pathlib import Path
from datetime import datetime
import warnings

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

# Detectar diretório base (funciona tanto para .py quanto para .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------------------------------------------
# CONSTANTES E CONFIGURAÇÕES
# -----------------------------------------------------------------------------

NOME_ARQUIVO_EXCEL = os.path.join(BASE_DIR, "Ajuste.xlsx")
USUARIO_JSON = os.path.join(BASE_DIR, "usuario.json")
SHEET_ERROS = "Erros"
ARQUIVO_VERSAO = os.path.join(BASE_DIR, "app_version.json")

# URLs - ALTERE PARA SEU REPOSITÓRIO GITHUB
URL_GITHUB_RAW = "https://raw.githubusercontent.com/JhonatasPSoares/ordem-e-ajuste/main/Transferencia.01.py"
URL_GITHUB_VERSAO = "https://raw.githubusercontent.com/JhonatasPSoares/ordem-e-ajuste/main/app_version.json"
URL_GITHUB_EXE = "https://github.com/JhonatasPSoares/ordem-e-ajuste/releases/download/latest/Transferencia.01.exe"

# URLs
URL_LOGIN = "https://nespresso.wiser.log.br/login"
URL_LISTAGEM = "https://nespresso.wiser.log.br/ordem-ajuste"
URL_CREATE_ENTRADA = "https://nespresso.wiser.log.br/ordem-ajuste/create/entrada"
URL_CREATE_ITEM = "https://nespresso.wiser.log.br/ordem-ajuste/ordem-ajuste-item/{ID}/create"

# XPaths - Login
XPATH_USER = '//*[@id="email"]'
XPATH_PASS = '//*[@id="password"]'

# XPaths - Criação de Ordem
XPATH_SELECT_DEPOSITANTE_CONTAINER = '//*[@id="select2-depositante-container"]'
XPATH_SELECT_MOTIVO_CONTAINER = '//*[@id="select2-ordem_ajuste_motivo_id-container"]'
XPATH_SELECT_SEARCH_INPUT = '//input[@class="select2-search__field"]'
# Especifica o textarea explicitamente para evitar capturar o <label> com mesmo id
XPATH_OBSERVACAO = '//textarea[@id="observacao"]'
XPATH_BTN_SALVAR_ORDEM = '//*[@id="page-wrapper"]/div/div[2]/form/button'

# XPaths - Inserção de Item
XPATH_POSICAO = '//*[@id="estoque_posicao"]'
XPATH_SKU = '//*[@id="produto"]'
XPATH_QUANTIDADE = '//*[@id="quantidade"]'
XPATH_VALIDADE = '//*[@id="data_vcto"]'
XPATH_LOTE = '//*[@id="lote"]'
XPATH_ESTOQUE_CONTAINER = '//*[@id="select2-status_estoque_id-container"]'
XPATH_ESTOQUE_INPUT = '//input[@class="select2-search__field"]'
XPATH_BTN_ADICIONAR_ITEM = '//*[@id="page-wrapper"]/div/div[2]/form/button'

# Constantes Transferência
COLUNA_SKU = 'Sku'
COLUNA_QUANTIDADE = 'QUANTIDADE'
COLUNA_SERIAL = 'Serial'

# Variáveis Globais de Controle
automacao_transferencia_rodando = False
automacao_transferencia_pausada = False
modo_headless = True


# -----------------------------------------------------------------------------
# UTILITÁRIOS
# -----------------------------------------------------------------------------

def salvar_usuario(usuario, senha):
    """Salva as credenciais em arquivo JSON local."""
    with open(USUARIO_JSON, "w", encoding="utf-8") as f:
        json.dump({"usuario": usuario, "senha": senha}, f)


def carregar_usuario():
    """Carrega as credenciais do arquivo JSON local, se existir."""
    if os.path.exists(USUARIO_JSON):
        with open(USUARIO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"usuario": "", "senha": ""}


def calcular_hash_arquivo(caminho_arquivo):
    """Calcula o hash SHA256 do arquivo."""
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def salvar_versao_app():
    """Salva a versão/hash do aplicativo atual."""
    timestamp = datetime.now().isoformat()
    
    if getattr(sys, 'frozen', False):
        hash_app = "exe_build"
    else:
        script_atual = os.path.join(BASE_DIR, "Transferencia.01.py")
        if os.path.exists(script_atual):
            hash_app = calcular_hash_arquivo(script_atual)
        else:
            hash_app = "unknown"
    
    with open(ARQUIVO_VERSAO, "w", encoding="utf-8") as f:
        json.dump({"hash": hash_app, "timestamp": timestamp}, f)


def verificar_atualizacao_github():
    """Verifica e baixa atualização do GitHub se disponível."""
    if getattr(sys, 'frozen', False):
        return False
    
    try:
        response = requests.get(URL_GITHUB_VERSAO, timeout=5)
        if response.status_code != 200:
            return False
        
        dados_github = response.json()
        hash_github = dados_github.get("hash", "")
        
        script_atual = os.path.join(BASE_DIR, "Transferencia.01.py")
        if not os.path.exists(script_atual):
            return False
        hash_atual = calcular_hash_arquivo(script_atual)
        
        if hash_github and hash_github != hash_atual and hash_github != "exe_build":
            try:
                response_script = requests.get(URL_GITHUB_RAW, timeout=10)
                if response_script.status_code == 200:
                    with open(script_atual, "w", encoding="utf-8") as f:
                        f.write(response_script.text)
                    salvar_versao_app()
                    return True
            except Exception as e:
                print(f"Erro ao baixar atualização: {e}")
                return False
    except Exception as e:
        print(f"Erro ao verificar atualização: {e}")
    
    return False


def verificar_atualizacao_app():
    """Verifica se o aplicativo foi atualizado desde a última execução."""
    if getattr(sys, 'frozen', False):
        return False
    
    script_atual = os.path.join(BASE_DIR, "Transferencia.01.py")
    if not os.path.exists(script_atual):
        return False
    hash_atual = calcular_hash_arquivo(script_atual)
    
    if os.path.exists(ARQUIVO_VERSAO):
        with open(ARQUIVO_VERSAO, "r", encoding="utf-8") as f:
            dados = json.load(f)
            hash_anterior = dados.get("hash", "")
            
            if hash_atual != hash_anterior:
                salvar_versao_app()
                return True
    else:
        salvar_versao_app()
        return False
    
    return False


def verificar_atualizacao_simples():
    """Verifica atualização simples via GitHub."""
    try:
        response = requests.get(URL_GITHUB_VERSAO, timeout=5)
        if response.status_code != 200:
            return False
        
        dados_github = response.json()
        hash_github = dados_github.get("hash", "")
        
        script_local = os.path.join(BASE_DIR, "Transferencia.01.py")
        
        if os.path.exists(script_local):
            hash_local = calcular_hash_arquivo(script_local)
            
            if hash_github and hash_github != hash_local and hash_github != "exe_build":
                try:
                    response_script = requests.get(URL_GITHUB_RAW, timeout=10)
                    if response_script.status_code == 200:
                        with open(script_local, "w", encoding="utf-8") as f:
                            f.write(response_script.text)
                        return True
                except Exception:
                    pass
    except Exception:
        pass
    
    return False


def type_by_chars(element, text, delay=0.02):
    """Digita texto caractere por caractere para simular digitação humana."""
    if text is None:
        return
    for ch in str(text):
        element.send_keys(ch)
        time.sleep(random.uniform(delay, delay + 0.03))


def human_click(driver, element):
    """Tenta clicar num elemento movendo o mouse ou via JavaScript como fallback."""
    try:
        action = ActionChains(driver)
        action.move_to_element(element).perform()
        time.sleep(random.uniform(0.1, 0.3))
        action.click(element).perform()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            return False


def get_chrome_major_version():
    """Detecta a versão principal do Chrome instalada no Windows."""
    try:
        import winreg
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            try:
                key = winreg.OpenKey(hive, r"Software\Google\Chrome\BLBeacon")
                ver, _ = winreg.QueryValueEx(key, "version")
                return int(str(ver).split('.')[0])
            except Exception:
                continue
    except Exception:
        pass
    try:
        possible_bins = [shutil.which(n) for n in ("chrome", "chrome.exe", "google-chrome")]
        possible_bins = [p for p in possible_bins if p]
        if possible_bins:
            out = subprocess.check_output([possible_bins[0], '--version'], stderr=subprocess.STDOUT).decode(errors='ignore')
            ver = out.strip().split()[-1]
            return int(ver.split('.')[0])
    except Exception:
        pass
    return None


def create_uc_driver(options):
    """Cria instância do undetected_chromedriver gerenciando versão."""
    if modo_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
    
    ver = get_chrome_major_version()
    if ver:
        try:
            return uc.Chrome(options=options, version_main=ver)
        except Exception:
            return uc.Chrome(options=options)
    else:
        return uc.Chrome(options=options)


def append_errors_to_excel(file_path, errors_df):
    """Adiciona/Atualiza a aba de erros no arquivo Excel."""
    from openpyxl import load_workbook
    file = Path(file_path)
    try:
        with pd.ExcelWriter(file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            writer.book = load_workbook(file)
            writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
            errors_df.to_excel(writer, sheet_name=SHEET_ERROS, index=False)
    except Exception:
        try:
            errors_df.to_excel(f"erros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", index=False)
        except Exception:
            pass


def abrir_ou_criar_planilha_ajuste():
    """Abre o Excel de ajuste ou cria um template se não existir."""
    if os.path.exists(NOME_ARQUIVO_EXCEL):
        try:
            os.startfile(NOME_ARQUIVO_EXCEL)
        except Exception:
            messagebox.showinfo("Arquivo", f"{NOME_ARQUIVO_EXCEL} existe, abra manualmente.")
    else:
        colunas = ["Posição", "Sku", "DESCRIÇÃO", "QUANTIDADE", "LOTE", "VALIDADE", "Estoque"]
        df = pd.DataFrame(columns=colunas)
        df.to_excel(NOME_ARQUIVO_EXCEL, index=False, sheet_name="Dados")
        try:
            os.startfile(NOME_ARQUIVO_EXCEL)
        except Exception:
            pass
        messagebox.showinfo("Criado", f"'{NOME_ARQUIVO_EXCEL}' criado com cabeçalho padrão.")


# -----------------------------------------------------------------------------
# AUTOMAÇÃO 1: ORDEM E AJUSTE (SELENIUM)
# -----------------------------------------------------------------------------

def executar_automacao_ajuste(file_path, tipo_ajuste, transferencia, log_fn, update_id_callback):
    """
    Executa o fluxo completo:
    1. Login.
    2. Criação da Ordem (Entrada de Devolução).
    3. Captura do ID gerado na tabela.
    4. Inserção dos itens do Excel.
    5. Efetivação da ordem.
    """
    errors = []
    driver = None
    id_ordem = None
    
    obs_texto = f"{tipo_ajuste} Transf: {transferencia}"

    try:
        df = pd.read_excel(file_path, dtype=str)
        df.columns = df.columns.str.strip()
    except Exception as e:
        log_fn(f"Erro ao ler planilha: {e}")
        return

    try:
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")
        options.page_load_strategy = 'eager'

        log_fn("Iniciando driver...")
        driver = create_uc_driver(options)
        wait = WebDriverWait(driver, 30)
        
        creds = carregar_usuario()
        if not creds.get("usuario") or not creds.get("senha"):
            log_fn("Credenciais ausentes.")
            return

        time.sleep(3)
        # --- Login ---
        driver.get(URL_LOGIN)
        log_fn("Realizando login...")
        
        time.sleep(2)
        
        wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_USER))).send_keys(creds["usuario"])
        time.sleep(2)
        el_pass = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_PASS)))
        time.sleep(3)
        el_pass.send_keys(creds["senha"], Keys.ENTER)
        
        wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, 'Cockpit Gerencial')))
        log_fn("Login OK.")
        # driver.Timeouts.PageLoad (3)

        # --- Criar Ordem ---
        log_fn("Criando Ordem de Ajuste...")
        driver.get(URL_CREATE_ENTRADA)

        # Depositante
        wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_SELECT_DEPOSITANTE_CONTAINER))).click()
        el_search = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_SELECT_SEARCH_INPUT)))
        el_search.send_keys("60409075054082 | Nespresso")
        time.sleep(0.5)
        el_search.send_keys(Keys.ENTER)

        # Motivo
        wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_SELECT_MOTIVO_CONTAINER))).click()
        el_search = wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_SELECT_SEARCH_INPUT)))
        el_search.send_keys("ENTRADA DE DEVOLUÇÃO")
        time.sleep(0.5)
        el_search.send_keys(Keys.ENTER)
        
        time.sleep(1)
        
        # --- ALTERAÇÃO AQUI: CLIQUE + DIGITAÇÃO SEGURO COM FALLBACK JS ---
        log_fn(f"Preenchendo observação: {obs_texto}")
        try:
            # 1. Encontra o elemento (ID)
            el_obs = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_OBSERVACAO)))
            
            # 2. Garante visibilidade e foca o elemento
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el_obs)
            except Exception:
                pass
            human_click(driver, el_obs)
            time.sleep(0.4)
            
            # 3. Tenta limpar e digitar via Selenium (send_keys) com helper que simula humana
            typed_ok = False
            try:
                tag = el_obs.tag_name.lower()
                # limpa se for input/textarea
                if tag in ("input", "textarea"):
                    try:
                        el_obs.clear()
                    except Exception:
                        # fallback: limpar via JS
                        driver.execute_script("arguments[0].value = '';", el_obs)
                # digita caractere a caractere
                try:
                    type_by_chars(el_obs, obs_texto, delay=0.03)
                    time.sleep(0.3)
                    # checa se o valor foi aplicado
                    current = driver.execute_script("return arguments[0].value || arguments[0].innerText || arguments[0].textContent || '';", el_obs)
                    if str(current).strip() == str(obs_texto).strip():
                        typed_ok = True
                except Exception:
                    typed_ok = False
            except Exception:
                typed_ok = False

            # 4. Se digitação falhar, injeta via JS e dispara eventos para frameworks reagirem
            if not typed_ok:
                try:
                    driver.execute_script("""
                        var el = arguments[0];
                        var val = arguments[1];
                        if (el.tagName.toLowerCase() === 'input' || el.tagName.toLowerCase() === 'textarea') {
                            el.value = val;
                        } else if (el.isContentEditable) {
                            el.innerText = val;
                        } else {
                            el.textContent = val;
                        }
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    """, el_obs, obs_texto)
                    time.sleep(0.3)
                except Exception as e_js:
                    log_fn(f"Erro no fallback JS da observação: {e_js}")
        except Exception as e:
            log_fn(f"Erro ao preencher observação: {e}")
            
        # ---------------------------------------------
        time.sleep(1.5)
        # Salvar Ordem
        driver.find_element(By.XPATH, XPATH_BTN_SALVAR_ORDEM).click()
        log_fn("Ordem salva. Buscando ID...")       
        time.sleep(10)
        
        # --- Capturar ID ---
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "tr")))
        # XPath procura TR que tenha o texto e pega o primeiro TD
        xpath_busca_id = f'//tr[contains(., "{obs_texto}")]/td[1]'
        
        try:
            el_id = wait.until(EC.presence_of_element_located((By.XPATH, xpath_busca_id)))
            id_ordem = el_id.text.strip()
            log_fn(f"✅ ID CAPTURADO: {id_ordem}")
            if update_id_callback:
                update_id_callback(id_ordem)
        except Exception as e:
            log_fn(f"❌ Falha ao capturar ID: {e}")
            return

        # --- Inserir Itens ---
        total = len(df)
        log_fn(f"Inserindo {total} itens na ordem {id_ordem}...")

        for idx, row in df.iterrows():
            linha_excel = idx + 2
            sku_val = str(row.get("Sku") or row.get("SKU") or row.get("sku") or "")
            
            try:
                driver.get(URL_CREATE_ITEM.format(ID=id_ordem))
                wait.until(EC.visibility_of_element_located((By.XPATH, XPATH_POSICAO)))

                driver.find_element(By.XPATH, XPATH_POSICAO).send_keys(str(row.get("Posição", "")))
                driver.find_element(By.XPATH, XPATH_SKU).send_keys(sku_val)
                driver.find_element(By.XPATH, XPATH_QUANTIDADE).send_keys(str(row.get("QUANTIDADE", "")))

                # Validade
                validade_raw = str(row.get("VALIDADE", "")).strip()
                if validade_raw and validade_raw not in ["0", "nan"]:
                    try:
                        parsed_date = pd.to_datetime(validade_raw, dayfirst=True)
                        date_input = parsed_date.strftime("%Y-%m-%d")
                        el_validade = driver.find_element(By.XPATH, XPATH_VALIDADE)
                        driver.execute_script("arguments[0].value = arguments[1];", el_validade, date_input)
                    except Exception:
                        pass
                
                # Lote
                lote_raw = str(row.get("LOTE", "")).strip() 
                if lote_raw and lote_raw not in ["0", "nan"]:
                    driver.find_element(By.XPATH, XPATH_LOTE).send_keys(lote_raw)

                # Estoque
                estoque_val = str(row.get("Estoque", "")).strip()
                if estoque_val:
                    try:
                        human_click(driver, wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_ESTOQUE_CONTAINER))))
                        el_input = driver.find_element(By.XPATH, XPATH_ESTOQUE_INPUT)
                        type_by_chars(el_input, estoque_val)
                        el_input.send_keys(Keys.ENTER)
                    except Exception as e:
                        log_fn(f"[{linha_excel}] Erro Estoque: {e}")

                human_click(driver, wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_BTN_ADICIONAR_ITEM))))
                log_fn(f"[{linha_excel}] Item inserido.")
                time.sleep(random.uniform(0.6, 1.2))

            except Exception as exc:
                log_fn(f"[{linha_excel}] Falha item: {exc}")
                errors.append({"linha": linha_excel, "sku": sku_val, "erro": str(exc)})

        # --- Efetivar Ordem ---
        log_fn("Tentando efetivar ordem...")
        try:
            driver.get(URL_LISTAGEM)
            xpath_efetivar = f"//*[@onclick='efetivarAction({id_ordem});']"
            btn_efetivar = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_efetivar)))
            human_click(driver, btn_efetivar)
            time.sleep(1.5)
            driver.find_element(By.CLASS_NAME, "confirm").click()
            time.sleep(5)
            
            
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                driver.switch_to.alert.accept()
            except:
                pass
            
            log_fn(f"✅ Ordem {id_ordem} efetivada.")
        except Exception as e:
            log_fn(f"⚠️ Erro ao efetivar: {e}")

        if errors:
            append_errors_to_excel(file_path, pd.DataFrame(errors))
            log_fn(f"Concluído com {len(errors)} erros.")
        else:
            log_fn("Concluído sem erros.")

    except Exception as e:
        log_fn("ERRO CRÍTICO NA AUTOMAÇÃO")
        log_fn(traceback.format_exc())
    finally:
        if driver:
            driver.quit()


# -----------------------------------------------------------------------------
# AUTOMAÇÃO 2: TRANSFERÊNCIA (KEYBOARD)
# -----------------------------------------------------------------------------

def abrir_planilha_transferencia():
    """Abre ou cria planilha de transferência."""
    try:
        if not os.path.exists(NOME_ARQUIVO_EXCEL):
            df_template = pd.DataFrame(columns=[COLUNA_SKU, COLUNA_QUANTIDADE, COLUNA_SERIAL])
            df_template.to_excel(NOME_ARQUIVO_EXCEL, index=False, sheet_name="Dados")
        os.startfile(NOME_ARQUIVO_EXCEL)
    except Exception as e:
        messagebox.showerror("Erro", str(e))


def executar_automacao_transferencia(status_label, progress_bar):
    """Lê a planilha e executa a digitação de dados via keyboard."""
    global automacao_transferencia_rodando, automacao_transferencia_pausada
    automacao_transferencia_rodando = True
    
    def update_status(text):
        status_label.config(text=text)
    
    update_status("Lendo dados...")
    try:
        df = pd.read_excel(NOME_ARQUIVO_EXCEL, dtype=str)
        df[COLUNA_SKU] = df[COLUNA_SKU].str.strip()
        df.dropna(subset=[COLUNA_SKU], inplace=True)
        
        # Lógica de tratamento de seriais vs quantidade
        df[COLUNA_SERIAL] = df.get(COLUNA_SERIAL, '').fillna('').str.strip().replace('nan', '')
        
        df_com_serial = df[df[COLUNA_SERIAL] != ''].copy()
        df_com_serial[COLUNA_QUANTIDADE] = 1
        
        df_sem_serial = df[df[COLUNA_SERIAL] == ''].copy()
        df_sem_serial[COLUNA_QUANTIDADE] = pd.to_numeric(df_sem_serial[COLUNA_QUANTIDADE], errors='coerce').fillna(0)
        df_agg = df_sem_serial.groupby(COLUNA_SKU)[COLUNA_QUANTIDADE].sum().reset_index()
        df_agg[COLUNA_SERIAL] = ''
        
        df_final = pd.concat([df_com_serial, df_agg[df_agg[COLUNA_QUANTIDADE] > 0]], ignore_index=True)
        total_items = len(df_final)
        
    except Exception as e:
        messagebox.showerror("Erro Leitura", str(e))
        return

    for i in range(3, 0, -1):
        if not automacao_transferencia_rodando: return
        update_status(f"Iniciando em {i}...")
        time.sleep(1)

    update_status("Executando...")
    
    for index, row in df_final.iterrows():
        while automacao_transferencia_pausada:
            if not automacao_transferencia_rodando: break
            time.sleep(0.1)

        if not automacao_transferencia_rodando: break

        progress_bar['value'] = ((index + 1) / total_items) * 100
        update_status(f"Item {index + 1}/{total_items}")

        sku = str(row[COLUNA_SKU])
        qtd = str(int(float(row[COLUNA_QUANTIDADE])))
        serial = str(row[COLUNA_SERIAL])

        keyboard.write(sku, delay=0.02)
        time.sleep(0.3)
        keyboard.press_and_release('tab')
        time.sleep(0.3)

        if serial:
            keyboard.write(serial, delay=0.02)
        else:
            keyboard.write(qtd, delay=0.03)
        
        time.sleep(0.3)
        keyboard.press_and_release('down')
        time.sleep(0.4)

    automacao_transferencia_rodando = False
    automacao_transferencia_pausada = False
    update_status("Concluído.")


# -----------------------------------------------------------------------------
# INTERFACE GRÁFICA (GUI) E CONTROLE DE THREADS
# -----------------------------------------------------------------------------

def append_log_gui(text):
    """Adiciona texto ao widget de log de forma segura."""
    if 'log_box' in globals() and log_box.winfo_exists():
        log_box.configure(state="normal")
        log_box.insert(tk.END, text + "\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")
        root.update_idletasks()


def start_ajuste_threaded_execution():
    """Valida inputs e inicia a thread de ajuste."""
    if not os.path.exists(NOME_ARQUIVO_EXCEL):
        messagebox.showerror("Erro", f"Arquivo {NOME_ARQUIVO_EXCEL} ausente.")
        return
    
    t_ajuste = entry_tipo_ajuste.get().strip()
    t_transf = entry_transferencia.get().strip()
    
    if not t_ajuste or not t_transf:
        messagebox.showerror("Erro", "Preencha 'Tipo de Ajuste' e 'Transferência'.")
        return

    def atualizar_label_id(novo_id):
        lbl_id_gerado.config(text=f"ID Gerado: {novo_id}", bootstyle="inverse-success")

    def target():
        append_log_gui("--- INICIANDO FLUXO AUTOMÁTICO ---")
        executar_automacao_ajuste(NOME_ARQUIVO_EXCEL, t_ajuste, t_transf, append_log_gui, atualizar_label_id)
        append_log_gui(f"[{datetime.now().strftime('%H:%M:%S')}] Finalizado.")
        
        # Verifica se só restou a thread principal para emitir alerta
        if not [e for e in threading.enumerate() if e.name != 'MainThread' and not e.daemon and e.is_alive()]:
             messagebox.showinfo("Fim", "Processo finalizado.")

    threading.Thread(target=target, daemon=True).start()


def open_config_user():
    """Janela para configurar usuário e senha."""
    creds = carregar_usuario()
    w = tk.Toplevel(root)
    w.title("Configuração")
    
    ttk.Label(w, text="Email:").pack(padx=10, pady=5)
    usr = ttk.Entry(w, width=40)
    usr.pack(padx=10)
    usr.insert(0, creds.get("usuario", ""))
    
    ttk.Label(w, text="Senha:").pack(padx=10, pady=5)
    pwd = ttk.Entry(w, width=40, show="*")
    pwd.pack(padx=10)
    pwd.insert(0, creds.get("senha", ""))
    
    def save():
        salvar_usuario(usr.get().strip(), pwd.get().strip())
        messagebox.showinfo("Salvo", "Dados salvos.")
        w.destroy()
    
    ttk.Button(w, text="Salvar", command=save, bootstyle="success").pack(pady=15)


def test_login_gui():
    """Executa teste rápido de login visível."""
    creds = carregar_usuario()
    if not creds.get("usuario"):
        return messagebox.showerror("Erro", "Configure o usuário.")
    
    def target():
        try:
            opts = uc.ChromeOptions()
            driver = create_uc_driver(opts)
            driver.get(URL_LOGIN)
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, XPATH_USER))).send_keys(creds["usuario"])
            WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, XPATH_PASS))).send_keys(creds["senha"], Keys.ENTER)
            messagebox.showinfo("Teste", "Login enviado.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
    
    threading.Thread(target=target, daemon=True).start()


def iniciar_transf_thread(lbl, pbar, btn_start, btn_stop):
    """Prepara e inicia thread de transferência."""
    global automacao_transferencia_rodando
    if automacao_transferencia_rodando: return
    
    btn_start.configure(state="disabled")
    btn_stop.configure(state="normal")
    pyautogui.hotkey('alt', 'tab')
    
    def target():
        executar_automacao_transferencia(lbl, pbar)
        btn_start.configure(state="normal")
        btn_stop.configure(state="disabled")
    
    threading.Thread(target=target, daemon=True).start()


def parar_transf(lbl):
    """Para a automação de transferência."""
    global automacao_transferencia_rodando, automacao_transferencia_pausada
    if automacao_transferencia_rodando:
        automacao_transferencia_pausada = False
        automacao_transferencia_rodando = False
        lbl.config(text="Parando...")


def toggle_pause_transf(lbl):
    """Pausa ou retoma a transferência."""
    global automacao_transferencia_pausada
    if not automacao_transferencia_rodando: return
    automacao_transferencia_pausada = not automacao_transferencia_pausada
    if automacao_transferencia_pausada:
        lbl.config(text='PAUSADO (Ctrl para voltar)')
    else:
        lbl.config(text="Continuando...")
        pyautogui.hotkey('alt', 'tab')


def toggle_modo_headless():
    """Alterna o modo headless do Selenium."""
    global modo_headless, btn_headless
    modo_headless = not modo_headless
    status = "✓ ATIVADO" if modo_headless else "✗ DESATIVADO"
    bootstyle_btn = "success-outline" if modo_headless else "danger-outline"
    if btn_headless:
        btn_headless.config(bootstyle=bootstyle_btn)
    messagebox.showinfo("Modo Headless", f"Modo Headless {status}")



if __name__ == "__main__":
    root = ttk.Window(themename="litera")
    root.title("🤖 Ordem e Ajuste 2.5.4")
    root.geometry("900x800")
    
    btn_headless = None
    
    if verificar_atualizacao_simples():
        messagebox.showinfo("Atualização", "✅ Aplicativo foi atualizado com sucesso!\n\nFavor reiniciar para carregar as mudanças.")
        root.destroy()
        exit(0)
    
    # Estilos
    style = ttk.Style()
    def setup_styles():
        colors = {"bg": "#1A1A1D", "fg": "#C5C6C7", "w": "#242529"} if theme_var.get() else {"bg": "#F5F5F7", "fg": "#0B0C10", "w": "#FFFFFF"}
        t = 'darkly' if theme_var.get() else 'litera'
        root.style.theme_use(t)

    theme_var = tk.BooleanVar(value=True)

    # Header
    hdr = ttk.Frame(root, padding=15)
    hdr.pack(fill='x')
    ttk.Label(hdr, text="Ordem e Ajuste", font=("Inter", 18, "bold")).pack(side='left')
    ttk.Checkbutton(hdr, text="Modo Escuro", variable=theme_var, command=setup_styles, bootstyle="round-toggle").pack(side='right')

    # Abas
    nb = ttk.Notebook(root, padding=5)
    nb.pack(fill="both", expand=True, padx=20, pady=10)

    # --- ABA 1: ORDEM E AJUSTE ---
    tab1 = ttk.Frame(nb, padding=25)
    nb.add(tab1, text="Ordem e Ajuste")

    # Controles Superiores
    fr_top = ttk.Frame(tab1)
    fr_top.pack(fill="x", pady=(0, 20))
    ttk.Button(fr_top, text="⚙️ Config User", command=open_config_user, bootstyle="outline").pack(side="left", padx=5)
    ttk.Button(fr_top, text="🧪 Testar Login", command=test_login_gui, bootstyle="outline").pack(side="left", padx=5)
    ttk.Button(fr_top, text="📄 Abrir Excel", command=abrir_ou_criar_planilha_ajuste, bootstyle="outline").pack(side="left", padx=5)
    btn_headless = ttk.Button(fr_top, text="🖥️ Headless", command=toggle_modo_headless, bootstyle="success-outline")
    btn_headless.pack(side="left", padx=5)

    # Inputs de Criação
    fr_inputs = ttk.Frame(tab1)
    fr_inputs.pack(fill="x", pady=10)
    
    f_tipo = ttk.Frame(fr_inputs)
    f_tipo.pack(side="left", fill="x", expand=True, padx=(0,5))
    ttk.Label(f_tipo, text="Tipo de Ajuste:").pack(anchor="w")
    entry_tipo_ajuste = ttk.Entry(f_tipo)
    entry_tipo_ajuste.pack(fill="x")
    
    f_transf = ttk.Frame(fr_inputs)
    f_transf.pack(side="left", fill="x", expand=True, padx=(5,0))
    ttk.Label(f_transf, text="Transferência:").pack(anchor="w")
    entry_transferencia = ttk.Entry(f_transf)
    entry_transferencia.pack(fill="x")

    # Display ID
    lbl_id_gerado = ttk.Label(tab1, text="ID Gerado: ---", font=("Inter", 12, "bold"), bootstyle="secondary", anchor="center")
    lbl_id_gerado.pack(fill="x", pady=10)

    # Botão Iniciar
    ttk.Button(tab1, text="▶️ INICIAR PROCESSO COMPLETO", command=start_ajuste_threaded_execution, bootstyle="success").pack(fill='x', ipady=10)

    # Log
    lf_log = ttk.LabelFrame(tab1, text="Log", padding=10)
    lf_log.pack(fill="both", expand=True, pady=10)
    log_box = scrolledtext.ScrolledText(lf_log, state="disabled", height=10)
    log_box.pack(fill="both", expand=True)

    # --- ABA 2: TRANSFERÊNCIA ---
    tab2 = ttk.Frame(nb, padding=25)
    nb.add(tab2, text="Transferência")
    
    ttk.Label(tab2, text="Automação via Teclado", font=("Inter", 14, "bold")).pack(pady=10)
    
    fr_act = ttk.Frame(tab2)
    fr_act.pack(fill='x')
    ttk.Button(fr_act, text="Abrir Excel", command=abrir_planilha_transferencia, bootstyle="outline").pack(fill='x', pady=5)
    
    btn_exec_transf = ttk.Button(fr_act, text="▶️ Executar", bootstyle="success")
    btn_exec_transf.pack(fill='x', pady=10, ipady=5)
    
    btn_stop_transf = ttk.Button(fr_act, text="⏹️ Parar (Delete)", bootstyle="danger", state="disabled")
    btn_stop_transf.pack(fill='x', pady=5)

    lbl_status_transf = ttk.Label(tab2, text="Aguardando...", font=("Inter", 11))
    lbl_status_transf.pack(pady=10)
    pbar_transf = ttk.Progressbar(tab2, length=300, mode='determinate', bootstyle='success-striped')
    pbar_transf.pack(pady=10)

    # Binds Transferência
    btn_exec_transf.config(command=lambda: iniciar_transf_thread(lbl_status_transf, pbar_transf, btn_exec_transf, btn_stop_transf))
    btn_stop_transf.config(command=lambda: parar_transf(lbl_status_transf))
    keyboard.add_hotkey('delete', lambda: parar_transf(lbl_status_transf))
    keyboard.add_hotkey('ctrl', lambda: toggle_pause_transf(lbl_status_transf))

    setup_styles()
    root.mainloop()