import os
from config import Config


class RadarPortal:
    def __init__(self, context, page):
        self.context = context
        self.page = page
        self.aba_classico = None
        self.erro_login = False
        self.sucesso_confirmado = False

    def acessar_radar_classico(self):
        print(f"Log (RadarPortal): Abrindo Radar Clássico (Timeout {Config.TIMEOUT_ABA / 1000}s)...")
        try:
            with self.context.expect_page(timeout=Config.TIMEOUT_ABA) as nova_aba_info:
                self.page.locator('a.titulomodulo', has_text='Radar Clássico').first.click()
            self.aba_classico = nova_aba_info.value
            self.aba_classico.wait_for_load_state('load')
            print("Log (RadarPortal): Aba carregada com sucesso.")
        except Exception as e:
            raise Exception(f"Erro ao abrir aba do Radar Clássico. {e}")

    # --- SEPARAMOS A NAVEGAÇÃO DA AÇÃO DE BAIXAR ---
    def acessar_tela_documentacao(self):
        """Apenas navega até a tela de Documentação."""
        f_menu = self.aba_classico.frame(name="tree_middle")
        print("Log (RadarPortal): Expandindo BOC...")
        f_menu.locator('a.node:visible', has_text='BOC').first.click()
        self.aba_classico.wait_for_timeout(Config.WAIT_MENU_EXPAND)

        print("Log (RadarPortal): Selecionando DOCUMENTAÇÃO...")
        f_menu.locator('#sd24').click()
        self.aba_classico.wait_for_timeout(Config.WAIT_BASE_LOAD)

    def baixar_base_documentacao(self):
        """Usa a tela de Documentação para exportar."""
        self.acessar_tela_documentacao()
        f_direito = self.aba_classico.frame(name="right")

        if not os.path.exists(Config.PATH_BASES_EXTRAIDAS):
            os.makedirs(Config.PATH_BASES_EXTRAIDAS)

        print("Log (RadarPortal): Solicitando Exportação...")
        with self.aba_classico.expect_download(timeout=180000) as download_info:
            f_direito.locator('text="Exportar"').first.click(force=True)

        download = download_info.value
        caminho_final = os.path.join(Config.PATH_BASES_EXTRAIDAS, download.suggested_filename)
        download.save_as(caminho_final)
        print(f"Log (RadarPortal): Base salva em: {caminho_final}")
        return download.suggested_filename

    # --- FUNÇÃO DE EXPURGO/LIMPEZA ---
    def desalocar_pedidos_usuario(self, usuario):
        f_direito = self.aba_classico.frame(name="right")
        total_removidos = 0

        # Proteção contra Pop-ups invisíveis do sistema
        def handle_dialog_limpeza(dialog):
            dialog.accept()

        self.aba_classico.on("dialog", handle_dialog_limpeza)

        try:
            while True:
                # Garante que os campos de busca já renderizaram (crucial para o 1º usuário)
                f_direito.locator('#field').wait_for(state='visible', timeout=15000)

                f_direito.locator('#field').select_option(value="a.usuario_tratando")

                # Injeta a matrícula exatamente como ela foi extraída do Excel
                f_direito.locator('#query').fill(usuario)
                f_direito.locator('#btnSubmit').click()

                # --- A ESPERA INTELIGENTE ---
                # Em vez de esperar 4s cegamente, o robô fica vigiando a tela por até 12 segundos
                # esperando a tabela de pedidos aparecer.
                links_solta = f_direito.locator('a[href*="javascript:solta"]')

                try:
                    # Fica olhando para a tela até o primeiro ícone de destravar aparecer
                    links_solta.first.wait_for(state='visible', timeout=12000)
                except Exception:
                    # Se bater 12 segundos sem resultado, a fila está limpa
                    print(f"Log (RadarPortal): Nenhum pedido restante para {usuario}. Fila limpa!")
                    break

                qtd_links = links_solta.count()
                print(f"Log (RadarPortal): Encontrados {qtd_links} pedidos na tela. Limpando...")

                # Metralha o botão "soltar" um a um
                for _ in range(qtd_links):
                    try:
                        links_solta.first.click(force=True)
                        self.aba_classico.wait_for_timeout(1500)  # Tempo pro JS agir
                        total_removidos += 1
                    except Exception as e:
                        pass  # Ignora pequenas falhas de animação da tela e segue pro próximo
        finally:
            self.aba_classico.remove_listener("dialog", handle_dialog_limpeza)

        return total_removidos

    def preparar_tela_alocacao(self):
        print("Log (RadarPortal): Acessando tela de Capturar Pedido...")
        f_menu = self.aba_classico.frame(name="tree_middle")
        f_menu.locator('a.node:visible', has_text='Ferramentas Administrativas').first.click()
        self.aba_classico.wait_for_timeout(1500)
        f_menu.locator('a[href*="setUsuario.asp"]:visible').first.click()
        self.aba_classico.wait_for_timeout(Config.WAIT_GENERAL)

    def alocar_pedido(self, nr_pedido, matricula_destino):
        f_direito = self.aba_classico.frame(name="right")
        self.erro_login = False
        self.sucesso_confirmado = False

        def handle_dialog(dialog):
            msg = dialog.message.lower()
            if "inválido" in msg or "bloqueado" in msg or "inexistente" in msg:
                self.erro_login = True
            elif "sucesso" in msg or "realizada" in msg:
                self.sucesso_confirmado = True
            dialog.accept()

        self.aba_classico.on("dialog", handle_dialog)

        try:
            f_direito.locator('#nr_pedido').fill("")
            f_direito.locator('#nr_pedido').fill(str(nr_pedido))
            f_direito.locator('input[value="exibir"]').click()

            icone = f_direito.locator(f'img[onclick*="trocarUsuario({nr_pedido})"]')
            icone.wait_for(state='visible', timeout=7000)
            icone.click()

            campo = f_direito.locator('#nm_login2')
            campo.wait_for(state='visible', timeout=5000)
            campo.fill(matricula_destino)
            campo.press("Enter")

            self.aba_classico.wait_for_timeout(2000)

            if not self.erro_login and not self.sucesso_confirmado:
                icone.click()
                self.aba_classico.wait_for_timeout(2000)

            if self.sucesso_confirmado:
                return "SUCCESS"
            elif self.erro_login:
                return "INVALID_LOGIN"
            else:
                return "ERROR"
        except Exception as e:
            return "SUCCESS" if self.sucesso_confirmado else "ERROR"
        finally:
            self.aba_classico.remove_listener("dialog", handle_dialog)