class DistribuidorRoundRobin:
    """
    Responsabilidade: Gerenciar a fila circular e aplicar regras de Skill-Based Routing.
    """

    def __init__(self, cotas_dict):
        # Recebe o novo dicionário aninhado do FileHandler
        self.cotas = cotas_dict
        self.analistas = list(self.cotas.keys())
        self.indice_atual = 0

    def obter_proximo_usuario(self, pedido_is_meta: bool):
        """Busca o próximo analista na roda que seja ELEGÍVEL para o tipo de pedido."""
        if not self.analistas:
            return None

        tentativas = 0
        total_analistas = len(self.analistas)

        while tentativas < total_analistas:
            analista = self.analistas[self.indice_atual]
            self.indice_atual = (self.indice_atual + 1) % len(self.analistas)

            filtro_analista = self.cotas[analista]['filtro']
            cota_restante = self.cotas[analista]['cota']

            # Regra de negócio: Analista aceita esse pedido?
            elegivel = False
            if filtro_analista == 'tudo':
                elegivel = True
            elif filtro_analista == 'meta' and pedido_is_meta:
                elegivel = True

            if cota_restante > 0 and elegivel:
                return analista

            tentativas += 1

        return None

    def consumir_cota(self, usuario):
        if usuario in self.cotas and self.cotas[usuario]['cota'] > 0:
            self.cotas[usuario]['cota'] -= 1
            if self.cotas[usuario]['cota'] <= 0:
                print(f"Log (Distribuidor): Cota de {usuario} esgotada.")
                self.desativar_usuario(usuario)

    def desativar_usuario(self, usuario):
        if usuario in self.analistas:
            print(f"Log (Distribuidor): !!! USUÁRIO {usuario} REMOVIDO DA FILA !!!")
            self.analistas.remove(usuario)
            if self.indice_atual >= len(self.analistas) and len(self.analistas) > 0:
                self.indice_atual = 0