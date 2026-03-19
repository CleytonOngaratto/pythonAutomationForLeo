import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # --- CAMINHOS FIXOS ---
    PATH_COTAS = r"C:\Users\LEO_USER\Desktop\cotas_teste.xlsx"
    PATH_BASES_EXTRAIDAS = r"C:\Users\LEO_USER\Downloads"

    # --- CREDENCIAIS (Windows Env) ---
    USER = os.getenv("TIM_USER")
    PASS = os.getenv("ROBO_PASS")

    # --- INFRA E URLS ---
    CHROME_PATH = os.getenv("CHROME_PATH")
    CHROME_DATA_DIR = os.getenv("USER_DATA_DIR")
    URL_RADAR_START = "https://INTERNAL_RADAR_URL"

    # --- TIMEOUTS ---
    TIMEOUT_ABA = 60000
    WAIT_MENU_EXPAND = 10000
    WAIT_BASE_LOAD = 25000
    WAIT_GENERAL = 2000