import subprocess
import time
from playwright.sync_api import sync_playwright

from config import Config


class BrowserFactory:
    """
    Responsabilidade: Gerenciar o ciclo de vida do navegador (Chrome).
    Princípio: Single Responsibility (SRP) - Apenas Infraestrutura.
    """

    def __init__(self, porta: int = 9222):
        self.caminho_chrome = Config.CHROME_PATH
        self.user_data_dir = Config.CHROME_DATA_DIR
        self.porta = porta
        self.playwright = None
        self.browser = None

    def _abrir_processo_windows(self):
        """Inicia o processo do Chrome no Windows com CDP habilitado."""
        print(f"Log (BrowserFactory): Abrindo Chrome na porta {self.porta}...")
        comando = [
            self.caminho_chrome,
            f"--remote-debugging-port={self.porta}",
            f"--user-data-dir={self.user_data_dir}"
        ]
        # Abre o Chrome de forma independente
        subprocess.Popen(comando)
        # Tempo de respiro para o Chrome carregar o perfil e abrir a porta
        time.sleep(5)

    def conectar(self):
        """Conecta o Playwright ao Chrome já aberto e retorna os objetos de controle."""
        self._abrir_processo_windows()

        print("Log (BrowserFactory): Conectando Playwright via CDP...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{self.porta}")

        context = self.browser.contexts[0]

        # Cria uma nova aba em branco, fugindo do redirecionamento da Microsoft/SharePoint
        page = context.new_page()
        page.bring_to_front()

        return self.playwright, self.browser, context, page

    def encerrar(self):
        """Finaliza a conexão e para o motor do Playwright."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("Log (BrowserFactory): Navegador desconectado.")