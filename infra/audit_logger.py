import os
from pathlib import Path
from datetime import datetime


class AuditLogger:
    """
    Responsabilidade: Registrar o histórico de alocações em arquivo físico no Desktop.
    Modo 'a' (append) garante que o histórico antigo nunca seja apagado.
    """

    def __init__(self):
        _padrao = str(Path.home() / "Desktop" / "relatorio_alocacao.txt")
        self.caminho_log = os.getenv("PATH_LOG_ALOCACAO", _padrao)

    def registrar(self, mensagem: str):
        """Escreve uma linha de log com a data e hora exata da ação."""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        linha = f"[{timestamp}] {mensagem}\n"

        try:
            # O parâmetro "a" (append) é a mágica que NÃO APAGA o que já estava lá!
            with open(self.caminho_log, "a", encoding="utf-8") as arquivo:
                arquivo.write(linha)
        except Exception as e:
            print(f"Log (AuditLogger): Erro ao escrever no arquivo de log: {e}")

    def iniciar_sessao(self, total_pedidos):
        """Cria um cabeçalho de destaque com a DATA para separar cada rodada do robô."""
        data_atual = datetime.now().strftime("%d/%m/%Y")
        hora_atual = datetime.now().strftime("%H:%M:%S")

        cabecalho = (
            f"\n{'=' * 75}\n"
            f" NOVA SESSÃO DE ALOCAÇÃO - DATA: {data_atual} | HORA: {hora_atual} \n"
            f" TOTAL DE PEDIDOS NA FILA PARA PROCESSAR: {total_pedidos} \n"
            f"{'=' * 75}\n"
        )

        try:
            with open(self.caminho_log, "a", encoding="utf-8") as arquivo:
                arquivo.write(cabecalho)
        except Exception as e:
            print(f"Log (AuditLogger): Erro ao iniciar sessão no log: {e}")

    def finalizar_sessao(self):
        """Marca o fim da rodada."""
        data_final = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        rodape = (
            f"{'-' * 75}\n"
            f" SESSÃO FINALIZADA EM: {data_final}\n"
            f"{'=' * 75}\n\n"
        )
        try:
            with open(self.caminho_log, "a", encoding="utf-8") as arquivo:
                arquivo.write(rodape)
        except Exception as e:
            pass