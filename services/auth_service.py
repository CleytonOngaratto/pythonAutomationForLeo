from config import Config


class AuthService:
    """
    Responsabilidade: IAM (Identity and Access Management)
    Princípio: SRP - Lógica exclusiva de Login da TIM.
    """

    def __init__(self, page):
        self.page = page
        self.url_radar = Config.URL_RADAR_START

    def realizar_login(self, usuario, senha):
        """Gerencia o fluxo de login no Ping Identity ou aproveita sessão ativa."""
        print(f"Log (AuthService): Navegando para {self.url_radar}...")
        self.page.goto(self.url_radar)

        # Espera o carregamento inicial e os redirecionamentos do sistema
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(3000)

        titulo = self.page.title().lower()
        url_atual = self.page.url.lower()

        # --- A INTELIGÊNCIA RESTAURADA ---
        # Verifica se fomos interceptados pela tela de login ou se já estamos logados
        if "login" in url_atual or "authentication" in titulo or "iam" in url_atual or "ping" in url_atual:
            print("Log (AuthService): Tela de login detectada. Iniciando preenchimento...")

            try:
                # --- FLUXO PING IDENTITY ATUALIZADO ---
                print("Log (AuthService): Aguardando campos do Ping Identity...")

                # Garante que o campo de usuário está pronto na tela
                campo_user = self.page.locator('#username')
                campo_user.wait_for(state='visible', timeout=15000)

                print(f"Log (AuthService): Preenchendo usuário {usuario}...")
                campo_user.click()
                campo_user.fill("")
                # Usamos o type para acionar os scripts JS do Ping Identity (como o uppercase automático)
                campo_user.type(usuario.upper(), delay=50)

                print("Log (AuthService): Preenchendo senha...")
                self.page.fill('#password', senha)

                print("Log (AuthService): Clicando no botão Entrar...")
                # Clique físico exigido pela nova versão do sistema
                self.page.click('#signOnButton')

            except Exception as e:
                print(f"Log (AuthService): [ERRO] Falha na tela de login. Salvando evidência...")
                self.page.screenshot(path="debug_login_ping.png")
                raise e
        else:
            # Se o cache do Chrome (USER_DATA_DIR) manteve a sessão viva, poupamos tempo!
            print("Log (AuthService): Sessão ativa detectada. Login pulado.")

        # --- VALIDAÇÃO DE SUCESSO ---
        print("Log (AuthService): Aguardando carregamento da interface do Radar...")
        self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.wait_for(state='visible', timeout=30000)
        print("Log (AuthService): Login concluído e acesso confirmado!")