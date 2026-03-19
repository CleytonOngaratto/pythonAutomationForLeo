import os
from config import Config


class RadarPortal:
    """
    Responsabilidade: Navegar no Radar Blue e Clássico.
    SOLID: SRP - Lógica exclusiva de interface com o sistema legado.
    """

    def __init__(self, context, page):
        self.context = context
        self.page = page
        self.aba_classico = None
        self.erro_login = False  # Bandeira para capturar erro de matrícula

    def acessar_radar_classico(self):
        """Abre o módulo Radar Clássico e captura a nova aba."""
        print(f"Log (RadarPortal): Abrindo Radar Clássico (Timeout {Config.TIMEOUT_ABA / 1000}s)...")
        try:
            with self.context.expect_page(timeout=Config.TIMEOUT_ABA) as nova_aba_info:
                self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.click()

            self.aba_classico = nova_aba_info.value
            self.aba_classico.wait_for_load_state('load')
            print("Log (RadarPortal): Aba carregada com sucesso.")
        except Exception as e:
            raise Exception(f"Erro: O sistema não abriu a aba do Radar Clássico a tempo. {e}")

    def baixar_base_documentacao(self):
        """Navega para DOCUMENTAÇÃO e exporta a base total para a pasta específica."""
        f_menu = self.aba_classico.frame(name="tree_middle")
        f_direito = self.aba_classico.frame(name="right")

        # Garante que a pasta de destino existe
        if not os.path.exists(Config.PATH_BASES_EXTRAIDAS):
            os.makedirs(Config.PATH_BASES_EXTRAIDAS)

        print("Log (RadarPortal): Expandindo BOC...")
        f_menu.locator('a.node:visible', has_text='BOC').first.click()
        self.aba_classico.wait_for_timeout(Config.WAIT_MENU_EXPAND)

        print("Log (RadarPortal): Selecionando DOCUMENTAÇÃO...")
        f_menu.locator('#sd24').click()
        self.aba_classico.wait_for_timeout(Config.WAIT_BASE_LOAD)

        print("Log (RadarPortal): Solicitando Exportação...")
        with self.aba_classico.expect_download(timeout=180000) as download_info:
            f_direito.locator('text="Exportar"').first.click(force=True)

        download = download_info.value
        # Salva na pasta configurada no Downloads
        caminho_final = os.path.join(Config.PATH_BASES_EXTRAIDAS, download.suggested_filename)
        download.save_as(caminho_final)

        print(f"Log (RadarPortal): Base salva em: {caminho_final}")
        return download.suggested_filename  # Retorna apenas o nome do arquivo

    def preparar_tela_alocacao(self):
        """Navega para Ferramentas Administrativas > Capturar Pedido."""
        print("Log (RadarPortal): Acessando tela de Capturar Pedido...")
        f_menu = self.aba_classico.frame(name="tree_middle")

        f_menu.locator('a.node:visible', has_text='Ferramentas Administrativas').first.click()
        self.aba_classico.wait_for_timeout(1500)

        f_menu.locator('a[href*="setUsuario.asp"]:visible').first.click()
        self.aba_classico.wait_for_timeout(Config.WAIT_GENERAL)

    def alocar_pedido(self, nr_pedido, matricula_destino):
        """
        Retorna:
        - "SUCCESS" (Alocação confirmada)
        - "INVALID_LOGIN" (Radar rejeitou a matrícula)
        - "ERROR" (Erro técnico/timeout - NÃO deve desativar o analista)
        """
        f_direito = self.aba_classico.frame(name="right")
        self.erro_login = False
        self.sucesso_confirmado = False  # Nova bandeira de sucesso

        # Garante que a matrícula é sempre string (Evita o erro do '899')
        matricula_destino = str(matricula_destino).strip()

        def handle_dialog(dialog):
            msg = dialog.message.lower()
            print(f"Log (RadarPortal): Alerta detectado: {dialog.message}")

            if "inválido" in msg or "bloqueado" in msg or "inexistente" in msg:
                self.erro_login = True
            elif "sucesso" in msg or "realizada" in msg:
                self.sucesso_confirmado = True

            dialog.accept()

        self.aba_classico.on("dialog", handle_dialog)

        try:
            # 1. Pesquisa o pedido
            f_direito.locator('#nr_pedido').fill("")
            f_direito.locator('#nr_pedido').fill(str(nr_pedido))
            f_direito.locator('input[value="exibir"]').click()

            icone = f_direito.locator(f'img[onclick*="trocarUsuario({nr_pedido})"]')
            icone.wait_for(state='visible', timeout=7000)

            # 2. Inicia a troca
            icone.click()

            # 3. Preenche a matrícula
            campo = f_direito.locator('#nm_login2')
            campo.wait_for(state='visible', timeout=5000)
            campo.fill(matricula_destino)
            campo.press("Enter")

            self.aba_classico.wait_for_timeout(2000)

            # 4. Finalização INTELIGENTE:
            # Se o Radar já deu o OK no pop-up anterior, não precisamos clicar de novo
            if not self.erro_login and not self.sucesso_confirmado:
                print("Log (RadarPortal): Solicitando confirmação final...")
                icone.click()
                self.aba_classico.wait_for_timeout(2000)

            # Retorno de Status
            if self.sucesso_confirmado:
                return "SUCCESS"
            elif self.erro_login:
                return "INVALID_LOGIN"
            else:
                return "ERROR"

        except Exception as e:
            print(f"Log (Portal): Erro técnico no pedido {nr_pedido}: {e}")
            # Se já detectou sucesso antes do erro de timeout, retorna sucesso!
            return "SUCCESS" if self.sucesso_confirmado else "ERROR"

        finally:
            self.aba_classico.remove_listener("dialog", handle_dialog)