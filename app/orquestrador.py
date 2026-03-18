from infra.web_adapter import WebAdapter
from infra.file_handler import FileHandler
from core.distribuidor import DistribuidorRoundRobin


class Orquestrador:
    def __init__(self):
        self.web = WebAdapter()
        self.arquivos = FileHandler()

    def executar_fluxo_distribuicao(self, arquivo_cotas: str):
        print("\n" + "=" * 50)
        print("INICIANDO ORQUESTRAÇÃO DO ROBÔ DE DISTRIBUIÇÃO")
        print("=" * 50)

        try:
            print("\n[Passo 1] Lendo planilha de cotas...")
            cotas = self.arquivos.ler_planilha_cotas(arquivo_cotas)
            if not cotas: return

            print("\n[Passo 2] Extraindo backlog atualizado do sistema...")
            self.web.conectar()
            nome_arquivo_baixado = self.web.baixar_base_documentacao()

            print(f"\n[Passo 3] Lendo e ordenando arquivo ({nome_arquivo_baixado})...")
            # Atualizado para o nome real da coluna no Excel
            backlog = self.arquivos.ler_e_ordenar_backlog(nome_arquivo_baixado, coluna_data='Data Entrada')
            if not backlog: return

            print("\n[Passo 4] Calculando distribuição e alocando no sistema...")
            distribuidor = DistribuidorRoundRobin(cotas)

            # Navega uma única vez para a tela de alocação antes de iniciar o loop
            self.web.acessar_tela_captura()

            for pedido in backlog:
                analista = distribuidor.obter_proximo_usuario()
                if not analista:
                    print("-> Aviso: Todas as cotas foram esgotadas!")
                    break

                numero_pedido = str(pedido['Pedido'])
                print(f" -> Alocando pedido: {numero_pedido} para a matrícula: {analista}")

                # Executa a ação na tela
                self.web.alocar_pedido(numero_pedido, analista)

            print("\nDistribuição concluída com sucesso!")

        except Exception as e:
            print(f"\nERRO FATAL NA ORQUESTRAÇÃO: {e}")

        finally:
            self.web.desconectar()