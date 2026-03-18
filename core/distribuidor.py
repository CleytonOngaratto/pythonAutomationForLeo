class DistribuidorRoundRobin:
    def __init__(self, cotas_usuarios: dict):
        """
        Recebe um dicionário com os usuários e suas cotas.
        Exemplo: {'T1234': 13, 'T5678': 15, 'T3763660': 10}
        """
        # Filtra apenas os usuários que têm cota maior que zero
        self.cotas_restantes = {usr: cota for usr, cota in cotas_usuarios.items() if cota > 0}
        self.usuarios_ativos = list(self.cotas_restantes.keys())
        self.indice_atual = 0

    def obter_proximo_usuario(self) -> str:
        """
        Retorna o próximo usuário da fila circular.
        Remove o usuário se a cota dele acabar.
        Retorna None se todas as cotas já tiverem sido preenchidas.
        """
        if not self.usuarios_ativos:
            return None

        # Pega o usuário da vez
        usuario_da_vez = self.usuarios_ativos[self.indice_atual]

        # Desconta 1 da cota deste usuário
        self.cotas_restantes[usuario_da_vez] -= 1

        # Verifica se o usuário bateu a meta
        if self.cotas_restantes[usuario_da_vez] == 0:
            # Remove da lista de ativos
            self.usuarios_ativos.pop(self.indice_atual)
        else:
            # Passa para o próximo índice
            self.indice_atual += 1

        # Garante que o índice volte para o começo (fazendo o círculo)
        if self.usuarios_ativos:
            self.indice_atual = self.indice_atual % len(self.usuarios_ativos)

        return usuario_da_vez

    def status_cotas(self) -> dict:
        return self.cotas_restantes