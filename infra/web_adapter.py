def acessar_tela_captura(self):
    """Navega pelo menu lateral até a tela de Capturar Pedido."""
    print("Log (WebAdapter): Navegando para a tela de Capturar Pedido...")

    # Como o menu já está carregado da etapa anterior, apenas pegamos o frame
    nova_aba = self.context.pages[-1]  # Pega a última aba aberta
    frame_menu = nova_aba.frame(name="tree_middle")

    # Expande Ferramentas Administrativas (usando :visible para ignorar lixo oculto)
    frame_menu.locator('a.node:visible', has_text='Ferramentas Administrativas').first.click()
    nova_aba.wait_for_timeout(1500)

    # Clica em Capturar Pedido (Manual) usando a URL 
    frame_menu.locator('a[href*="setUsuario.asp"]:visible').first.click()

    # Dá tempo para o frame direito carregar a nova tela
    nova_aba.wait_for_timeout(2000)


def alocar_pedido(self, numero_pedido: str, usuario_destino: str):
    """Preenche o pedido, clica em exibir e aciona a troca de usuário."""
    nova_aba = self.context.pages[-1]
    frame_direito = nova_aba.frame(name="right")

    # 1. Preenche o número do pedido
    campo_pedido = frame_direito.locator('input#nr_pedido')
    campo_pedido.fill(numero_pedido)

    # 2. Clica no botão exibir
    frame_direito.locator('input[type="button"][value="exibir"]').click()

    # 3. Aguarda a tabela renderizar e clica no ícone de trocar usuário (43.png)
    # Usamos o atributo value que contém o número do pedido para ser exato
    botao_trocar = frame_direito.locator(f'a[value="{numero_pedido}"] img[src*="43.png"]')
    botao_trocar.wait_for(state='visible')
    botao_trocar.click()

    # PAUSA ESTRATÉGICA: O que acontece a partir daqui?
    nova_aba.wait_for_timeout(1000)

    # TODO: Implementar a inserção da matrícula (usuario_destino) e confirmação.