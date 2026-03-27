@echo off
title ACT // TIM - Automacao Radar Blue
color 0B
echo ========================================================
echo         SISTEMA DE ALOCACAO INTELIGENTE - ACT / TIM
echo ========================================================
echo.

:: 1. Entra na pasta
cd /d "C:\Users\LEO_USER\DEV\sistemaautomacao"

:: 2. Tenta ativar o ambiente
echo [*] Preparando ambiente corporativo...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERRO CRITICO] Falha ao carregar o ambiente virtual.
    pause
    exit
)

:: 3. Verifica a Senha da Automacao no Windows
echo [*] Validando credenciais de seguranca...
if "%ROBO_PASS%"=="" (
    echo [AVISO] A senha ROBO_PASS nao foi encontrada nas variaveis do Windows!
    echo         Configure a senha antes de iniciar.
    pause
    exit
)

:: 4. Roda o Python
echo.
echo ========================================================
echo              INICIANDO MOTOR DE ORQUESTRACAO
echo ========================================================
echo.
set PYTHONPATH=%cd%
python main.py

:: 5. Finalizacao dinamica
echo.
echo ========================================================
if %errorlevel% neq 0 (
    color 0C
    echo [AVISO] A execucao encontrou um erro critico.
    echo         Revise os logs da aplicacao impressos acima.
) else (
    color 0A
    echo [SUCESSO] Operacao ACT concluida com exito!
    echo           Verifique o relatorio na area de trabalho.
)
echo ========================================================
pause