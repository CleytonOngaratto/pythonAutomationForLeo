import os
from config import Config

class AuthService:
    """
    Responsabilidade: Orquestrar a autenticação.
    (Nota para o Junior: Em refatorações futuras, moveremos os seletores CSS
    para uma classe de Page Object para respeitar 100% o SRP e Clean Arch).
    """

    def __init__(self, page):
        self.page = page
        self.url_radar = Config.URL_RADAR_START

    def realizar_login(self, usuario, senha):
        print(f"Log (AuthService): Navegando para {self.url_radar}...")
        self.page.goto(self.url_radar)
        self.page.wait_for_load_state('networkidle')

        titulo = self.page.title().lower()
        url_atual = self.page.url.lower()

        if any(keyword in url_atual or keyword in titulo for keyword in ["login", "authentication", "iam", "ping"]):
            print("Log (AuthService): Tela de login detectada. Iniciando preenchimento resiliente...")

            try:
                # 1. VERIFICA SE A CONTA JÁ ESTÁ SALVA (Correção do Seletor CSS)
                # Usando [id="valor"] para evitar problemas com pontos/arrobas no nome de usuário
                seletor_conta = f'li[id="{usuario.upper()}"], li[id="{usuario}"]'
                conta_salva = self.page.locator(seletor_conta).first

                if conta_salva.is_visible(timeout=5000):
                    print(f"Log (AuthService): Conta {usuario} encontrada. Clicando...")
                    conta_salva.click()
                else:
                    # 2. BUSCA DINÂMICA DO CAMPO DE USUÁRIO
                    print("Log (AuthService): Conta não salva. Inserindo usuário...")
                    campo_user = self.page.locator('#username, #identifierInput').first
                    campo_user.wait_for(state='visible', timeout=15000)
                    campo_user.fill(usuario.upper()) # Playwright fill já limpa o campo

                # 3. DETECÇÃO DE FLUXO (1 Etapa vs 2 Etapas)
                campo_senha = self.page.locator('#password')

                if not campo_senha.is_visible(timeout=3000):
                    print("Log (AuthService): Avançando para tela de senha...")
                    self.page.locator('#signOnButton, .ping-button.allow').first.click()
                    campo_senha.wait_for(state='visible', timeout=15000)

                # 4. SENHA E SUBMIT
                print("Log (AuthService): Preenchendo senha...")
                campo_senha.fill(senha)
                self.page.locator('#signOnButton, .ping-button.allow').first.click()

            except Exception as e:
                print("Log (AuthService): [ERRO] Falha na tela de login.")
                if os.getenv("DEBUG_SCREENSHOTS"):
                    self.page.screenshot(path="debug_login_ping.png")
                raise e
        else:
            print("Log (AuthService): Sessão ativa detectada. Login pulado.")

        # VALIDAÇÃO DE SUCESSO
        self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.wait_for(state='visible', timeout=30000)
        print("Log (AuthService): Login concluído e acesso confirmado!")