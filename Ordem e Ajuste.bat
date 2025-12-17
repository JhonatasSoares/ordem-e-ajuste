@echo off
setlocal enabledelayedexpansion

REM Obtém o diretório do script
set SCRIPT_DIR=%~dp0

REM Executa o launcher
cd /d "%SCRIPT_DIR%"
python launcher.py

REM Se houver erro, mostra mensagem
if errorlevel 1 (
    echo.
    echo Erro ao executar o aplicativo.
    echo Certifique-se de que Python está instalado.
    pause
)
