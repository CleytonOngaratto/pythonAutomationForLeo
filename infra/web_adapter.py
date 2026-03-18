from playwright.sync_api import sync_playwright
import subprocess
import time
import os


class WebAdapter:
    def __init__(self, porta_cdp: int = 9222):
        self.porta_cdp = porta_cdp
        self.cdp_url = f"http://localhost:{porta_cdp}"

        self.caminho_chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.user_data_dir = r"C:\temp\chrome_automacao"
        self.url_inicial = "https://INTERNAL_RADAR_URL"

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _abrir_chrome_via_terminal(self):
        print("Log (WebAdapter): Iniciando o Chrome automaticamente...")
        comando = [
            self.caminho_chrome,
            f"--remote-debugging-port={self.porta_cdp}",
            f"--user-data-dir={self.user_data_dir}"
        ]
        subprocess.Popen(comando)
        print("Log (WebAdapter): Aguardando o navegador renderizar...")
        time.sleep(4)

    def _realizar_login_se_necessario(self):
        """Força a ida para o sistema e faz o login caso o IAM intercepte."""
        print(f"Log (WebAdapter): Navegando obrigatoriamente para {self.url_inicial}...")
        self.page.goto(self.url_inicial)
        self.page.wait_for_load_state('load')

        # Pausa para o Ping Identity terminar de animar a tela
        self.page.wait_for_timeout(3000)

        titulo_pagina = self.page.title().lower()
        url_atual = self.page.url.lower()

        if "authentication" in titulo_pagina or "login" in titulo_pagina or "iam" in url_atual:
            print("Log (WebAdapter): Bloqueio do IAM (Ping Identity) detectado. Iniciando login...")

            # ------------------------------------------------------------------
            # ATENÇÃO: Coloque sua matrícula e senha reais aqui embaixo
            # ------------------------------------------------------------------
            seu_usuario = "T3763660"
            sua_senha = "senha"

            # --- ETAPA 1: MATRÍCULA (BIFURCAÇÃO INTELIGENTE) ---
            # Verifica se o botão com a sua matrícula salva está visível
            conta_salva = self.page.locator(f'li#{seu_usuario}')

            if conta_salva.is_visible():
                print(f"Log (WebAdapter): Conta {seu_usuario} lembrada pelo sistema! Clicando nela...")
                conta_salva.click()
            else:
                print("Log (WebAdapter): Conta não lembrada. Preenchendo matrícula do zero...")
                campo_usuario = self.page.locator('#identifierInput')
                campo_usuario.wait_for(state='visible')
                campo_usuario.fill(seu_usuario)

                print("Log (WebAdapter): Clicando em 'Next'...")
                self.page.locator('a#signOnButton[title="Next"]').click()

            # --- ETAPA 2: SENHA ---
            print("Log (WebAdapter): Aguardando campo de senha...")
            campo_senha = self.page.locator('#password')
            campo_senha.wait_for(state='visible', timeout=15000)

            print("Log (WebAdapter): Preenchendo senha...")
            campo_senha.fill(sua_senha)

            print("Log (WebAdapter): Clicando em 'Entrar'...")
            self.page.locator('a#signOnButton[title="Entrar"]').click()

            # --- ETAPA 3: VALIDAÇÃO ---
            print("Log (WebAdapter): Aguardando redirecionamento para o Radar Blue...")
            self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.wait_for(state='visible',
                                                                                          timeout=30000)
            print("Log (WebAdapter): Login executado com sucesso! Estamos dentro.")
        else:
            print("Log (WebAdapter): Sessão já estava ativa! Passamos direto pelo IAM.")

    def conectar(self):
        self._abrir_chrome_via_terminal()

        print(f"Log (WebAdapter): Conectando o Playwright na porta {self.cdp_url}...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(self.cdp_url)

        self.context = self.browser.contexts[0]
        self.page = self.context.pages[0]
        self.page.bring_to_front()

        self._realizar_login_se_necessario()

    def desconectar(self):
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()
        print("Log (WebAdapter): Desconectado do navegador.")

    def baixar_base_documentacao(self) -> str:
        print("Log (WebAdapter): Iniciando navegação para extração da base...")
        botao_radar = self.page.locator('a.titulomodulo', has_text='Radar Clássico').first

        with self.context.expect_page() as nova_aba_info:
            botao_radar.click()

        nova_aba = nova_aba_info.value
        nova_aba.wait_for_load_state('load')

        print("Log (WebAdapter): Aguardando o servidor montar os frames internos...")
        frame_menu = None
        frame_direito = None

        for tentativa in range(15):
            for f in nova_aba.frames:
                if f.name == "tree_middle":
                    frame_menu = f
                elif f.name == "right":
                    frame_direito = f
            if frame_menu and frame_direito: break
            nova_aba.wait_for_timeout(1000)

        if not frame_menu or not frame_direito:
            raise Exception("O sistema demorou demais para carregar os frames do menu.")

        print("Log (WebAdapter): Frames localizados! Expandindo a pasta BOC...")
        frame_menu.locator('a.node:visible', has_text='BOC').first.click()
        nova_aba.wait_for_timeout(1500)

        print("Log (WebAdapter): Clicando na fila DOCUMENTAÇÃO...")
        frame_menu.locator('a[href*="cod_fila=2"]:visible').first.click()

        print("Log (WebAdapter): Aguardando botão de Exportar...")
        botao_exportar = frame_direito.locator('text="Exportar"').first
        botao_exportar.wait_for(state='visible')

        print("Log (WebAdapter): Interceptando o Excel...")
        with nova_aba.expect_download() as download_info:
            botao_exportar.click()

        download = download_info.value
        nome_arquivo = download.suggested_filename
        caminho_completo = os.path.join(os.getcwd(), nome_arquivo)
        download.save_as(caminho_completo)
        print(f"Log (WebAdapter): SUCESSO ABSOLUTO! Arquivo salvo em: {caminho_completo}")
        nova_aba.close()
        return nome_arquivo

    def acessar_tela_captura(self):
        print("Log (WebAdapter): Navegando para a tela de Capturar Pedido...")
        nova_aba = self.context.pages[-1]
        frame_menu = nova_aba.frame(name="tree_middle")
        frame_menu.locator('a.node:visible', has_text='Ferramentas Administrativas').first.click()
        nova_aba.wait_for_timeout(1500)
        frame_menu.locator('a[href*="setUsuario.asp"]:visible').first.click()
        nova_aba.wait_for_timeout(2000)

    def alocar_pedido(self, numero_pedido: str, usuario_destino: str):
        nova_aba = self.context.pages[-1]
        frame_direito = nova_aba.frame(name="right")
        campo_pedido = frame_direito.locator('input#nr_pedido')
        campo_pedido.fill(numero_pedido)
        frame_direito.locator('input[type="button"][value="exibir"]').click()
        botao_trocar = frame_direito.locator(f'a[value="{numero_pedido}"] img[src*="43.png"]')
        botao_trocar.wait_for(state='visible')
        botao_trocar.click()
        nova_aba.wait_for_timeout(1000)