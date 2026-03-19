class DistribuidorRoundRobin:
    """
    Responsabilidade: Gerenciar a fila circular de analistas e suas cotas.
    SOLID: SRP - Lógica de distribuição isolada.
    """

    def __init__(self, cotas):
        # Transforma o dicionário em uma lista de objetos para fácil iteração
        self.analistas = [{"login": k, "cota": v} for k, v in cotas.items() if v > 0]
        self.ponteiro = 0

    def obter_proximo_usuario(self):
        """
        Retorna o próximo analista da fila que ainda tenha cota.
        O ponteiro avança a cada chamada para garantir o rodízio.
        """
        if not self.analistas:
            return None

        # Tenta encontrar alguém com cota, dando no máximo uma volta completa na lista
        for _ in range(len(self.analistas)):
            analista = self.analistas[self.ponteiro]

            # Avança o ponteiro para a PRÓXIMA chamada (mesmo se esta falhar depois)
            self.ponteiro = (self.ponteiro + 1) % len(self.analistas)

            if analista["cota"] > 0:
                return analista["login"]

        return None

    def consumir_cota(self, login):
        """
        Decrementa a cota apenas após a confirmação de sucesso no sistema.
        """
        for a in self.analistas:
            if a["login"] == login:
                a["cota"] -= 1
                if a["cota"] <= 0:
                    print(f"Log (Distribuidor): Cota de {login} esgotada.")
                break

    def desativar_usuario(self, login):
        """Zera a cota de um usuário que apresentou erro crítico de acesso."""
        for a in self.analistas:
            if a["login"] == login:
                a["cota"] = 0
                print(f"Log (Distribuidor): !!! USUÁRIO {login} REMOVIDO DA FILA (Acesso Inválido) !!!")
                break