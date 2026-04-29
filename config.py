import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    _home = Path.home()

    # --- CAMINHOS (via env ou padrão relativo ao usuário do SO) ---
    PATH_COTAS = os.getenv("PATH_COTAS", str(_home / "Desktop" / "matriz_alocacao.xlsx"))
    PATH_BASES_EXTRAIDAS = os.getenv("PATH_BASES_EXTRAIDAS", str(_home / "Downloads"))

    # --- CREDENCIAIS (Windows Env — obrigatório) ---
    USER = os.getenv("TIM_USER")
    PASS = os.getenv("ROBO_PASS")

    # --- INFRA E URLS (todas via env — obrigatório) ---
    CHROME_PATH = os.getenv("CHROME_PATH")
    CHROME_DATA_DIR = os.getenv("USER_DATA_DIR")
    URL_RADAR_START = os.getenv("URL_RADAR_START")

    # --- TIMEOUTS ---
    TIMEOUT_ABA = 60000
    WAIT_MENU_EXPAND = 10000
    WAIT_BASE_LOAD = 25000
    WAIT_GENERAL = 2000