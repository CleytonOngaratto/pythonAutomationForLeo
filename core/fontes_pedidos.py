from config import Config


class FontePortal:
    """Strategy: baixa a base do portal e filtra o backlog (comportamento padrão)."""

    def __init__(self, radar_portal, file_handler):
        self.radar_portal = radar_portal
        self.file_handler = file_handler

    def obter_pedidos(self):
        filename = self.radar_portal.baixar_base_documentacao()
        return self.file_handler.ler_e_ordenar_backlog(filename, 'Data de Entrada')


class FonteListaFixa:
    """Strategy: lê números de pedido da aba 'Pedidos' do Excel de cotas."""

    def __init__(self, file_handler):
        self.file_handler = file_handler

    def obter_pedidos(self):
        return self.file_handler.ler_lista_pedidos(Config.PATH_COTAS)
