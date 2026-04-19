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

        if "login" in url_atual or "authentication" in titulo or "iam" in url_atual or "ping" in url_atual:
            print("Log (AuthService): Tela de login detectada. Iniciando preenchimento resiliente...")

            try:
                # --- 1. BUSCA DINÂMICA DO CAMPO DE USUÁRIO ---
                # O robô procura o ID novo (#identifierInput) ou o antigo (#username)
                campo_user = self.page.locator('#username, #identifierInput').first
                campo_user.wait_for(state='visible', timeout=15000)

                print(f"Log (AuthService): Preenchendo usuário {usuario}...")
                campo_user.click()
                campo_user.fill("")
                campo_user.type(usuario.upper(), delay=50)

                # --- 2. DETECÇÃO DE FLUXO (1 Etapa vs 2 Etapas) ---
                # Verifica se o campo de senha já está visível na tela
                campo_senha = self.page.locator('#password')

                if not campo_senha.is_visible():
                    print("Log (AuthService): Fluxo de 2 etapas detectado. Clicando em 'Next'...")
                    # Clica no botão para avançar para a tela de senha
                    self.page.locator('#signOnButton').first.click()
                    # Aguarda a animação da página trazer o campo de senha
                    campo_senha.wait_for(state='visible', timeout=15000)

                # --- 3. SENHA E SUBMIT FINAL ---
                print("Log (AuthService): Preenchendo senha...")
                campo_senha.fill(senha)

                print("Log (AuthService): Clicando no botão Entrar...")
                # Procura o botão de submit usando ID ou classe genérica do Ping
                botao_entrar = self.page.locator('#signOnButton, .ping-button.allow').first
                botao_entrar.click()

            except Exception as e:
                print(f"Log (AuthService): [ERRO] Falha na tela de login. Salvando evidência...")
                self.page.screenshot(path="debug_login_ping.png")
                raise e
        else:
            print("Log (AuthService): Sessão ativa detectada. Login pulado.")

        # --- VALIDAÇÃO DE SUCESSO ---
        print("Log (AuthService): Aguardando carregamento da interface do Radar...")
        self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.wait_for(state='visible', timeout=30000)
        print("Log (AuthService): Login concluído e acesso confirmado!")