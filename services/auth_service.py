from config import Config


class AuthService:
    """
    Responsabilidade: IAM
    Princípio: SRP - Lógica exclusiva de Login.
    """

    def __init__(self, page):
        self.page = page
        self.url_radar = Config.URL_RADAR_START

    def realizar_login(self, usuario, senha):
        """Gerencia o fluxo de login em duas etapas da TIM."""
        print(f"Log (AuthService): Navegando para {self.url_radar}...")
        self.page.goto(self.url_radar)

        # Espera o carregamento inicial e possíveis redirecionamentos do IAM
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(3000)

        titulo = self.page.title().lower()
        url_atual = self.page.url.lower()

        # Verifica se fomos interceptados pela tela de login
        if "login" in url_atual or "authentication" in titulo or "iam" in url_atual:
            print("Log (AuthService): Tela de login detectada. Iniciando Etapa 1 (Matrícula)...")

            # --- ETAPA 1: Identificar o usuário ---
            # Tenta localizar o botão de conta salva (aquele <li> com seu ID)
            conta_salva = self.page.locator(f'li#{usuario}')

            if conta_salva.is_visible():
                print(f"Log (AuthService): Conta {usuario} encontrada no histórico. Clicando...")
                conta_salva.click()
            else:
                print("Log (AuthService): Conta não listada. Preenchendo campo manualmente...")
                campo_id = self.page.locator('#identifierInput')
                campo_id.wait_for(state='visible')
                campo_id.fill(usuario)
                # Clica no botão 'Next' da primeira tela
                self.page.locator('a#signOnButton[title="Next"]').click()

            # --- ETAPA 2: Senha ---
            print("Log (AuthService): Aguardando campo de senha...")
            campo_senha = self.page.locator('#password')
            # Espera a animação de transição do Ping Identity
            campo_senha.wait_for(state='visible', timeout=15000)
            campo_senha.fill(senha)

            print("Log (AuthService): Submetendo credenciais...")
            self.page.locator('a#signOnButton[title="Entrar"]').click()

            # Validação: Espera o botão principal do Radar aparecer para confirmar sucesso
            self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.wait_for(state='visible',
                                                                                          timeout=30000)
            print("Log (AuthService): Login concluído com sucesso!")
        else:
            print("Log (AuthService): Sessão ativa detectada. Login pulado.")