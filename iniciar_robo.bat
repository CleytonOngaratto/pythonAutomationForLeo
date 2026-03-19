@echo off
title DIAGNOSTICO DE AUTOMACAO
echo ============================================
echo      PROCURANDO ERROS NO SISTEMA...
echo ============================================
echo.

:: 1. Entra na pasta
cd /d "C:\Users\LEO_USER\DEV\sistemaautomacao"

:: 2. Tenta ativar o ambiente
echo [1/3] Ativando ambiente virtual...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERRO] Nao foi possivel ativar o .venv. Verifique se a pasta existe.
    pause
    exit
)

:: 3. Verifica a Senha no Windows
echo [2/3] Verificando variavel TIM_PASS...
if "%TIM_PASS%"=="" (
    echo [AVISO] A senha TIM_PASS nao foi encontrada no ambiente do Windows!
) else (
    echo [OK] Senha encontrada na memoria do Windows.
)

:: 4. Roda o Python e SEGURA O ERRO na tela
echo [3/3] Tentando iniciar o Maestro...
echo.
set PYTHONPATH=%cd%
python main.py

echo.
echo ============================================
echo      O SCRIPT PAROU ACIMA.
echo      LEIA O ERRO E ME MANDE AQUI!
echo ============================================
pause