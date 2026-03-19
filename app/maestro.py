from infra.browser_factory import BrowserFactory
from services.auth_service import AuthService
from services.radar_portal import RadarPortal
from infra.file_handler import FileHandler
from infra.audit_logger import AuditLogger
from core.distribuidor import DistribuidorRoundRobin
from config import Config


class Maestro:
    """
    Responsabilidade: Orquestrar o fluxo de negócio (End-to-End).
    Regra de Ouro: Persistência no pedido e documentação em log de auditoria.
    """

    def __init__(self):
        self.factory = BrowserFactory()
        self.arquivos = FileHandler()
        self.logger = AuditLogger()  # Nosso historiador

    def executar(self, usuario_tim, senha_tim):
        """Executa o ciclo completo da automação."""

        # 1. Inicia o motor do Navegador (Chrome via CDP)
        pw, browser, context, page = self.factory.conectar()

        try:
            # 2. Atravessa o Login (IAM Ping Identity)
            auth = AuthService(page)
            auth.realizar_login(usuario_tim, senha_tim)

            # 3. Portal e Extração Massiva (TSV disfarçado de XLS)
            portal = RadarPortal(context, page)
            portal.acessar_radar_classico()
            nome_arquivo_base = portal.baixar_base_documentacao()

            # 4. Processamento de Dados (Backlog e Planilha no Desktop)
            backlog = self.arquivos.ler_e_ordenar_backlog(nome_arquivo_base, "Data de Entrada")
            cotas = self.arquivos.ler_planilha_cotas(Config.PATH_COTAS)

            if not backlog or not cotas:
                msg_erro = "Backlog ou Planilha de Cotas não processados. Verifique os arquivos."
                print(f"Log (Maestro): {msg_erro}")
                self.logger.registrar(f"ERRO: {msg_erro}")
                return

            # 5. Configura o Distribuidor e inicia sessão de Log
            distribuidor = DistribuidorRoundRobin(cotas)
            self.logger.iniciar_sessao(len(backlog))
            portal.preparar_tela_alocacao()

            print(f"Log (Maestro): Iniciando alocação de {len(backlog)} pedidos únicos...")

            # 6. Loop de Alocação com Persistência e Auditoria
            for item in backlog:
                pedido_id = item.get('Pedido')
                sucesso_alocacao = False
                tentativas = 0
                max_tentativas = len(distribuidor.analistas)

                while not sucesso_alocacao and tentativas < max_tentativas:
                    proximo_analista = distribuidor.obter_proximo_usuario()
                    if not proximo_analista: break

                    print(f"Log (Maestro): Tentando Pedido {pedido_id} -> Analista {proximo_analista}")

                    # A função agora retorna uma string de status
                    status = portal.alocar_pedido(pedido_id, proximo_analista)

                    if status == "SUCCESS":
                        sucesso_alocacao = True
                        distribuidor.consumir_cota(proximo_analista)
                        self.logger.registrar(f"SUCESSO: Pedido {pedido_id} -> {proximo_analista}")
                        print(f"Log (Maestro): [OK] Pedido {pedido_id} finalizado.")

                    elif status == "INVALID_LOGIN":
                        # Só desativa se o Radar expressamente rejeitou o login
                        print(f"Log (Maestro): [ERRO] Login {proximo_analista} inválido. Desativando...")
                        self.logger.registrar(f"FALHA: Login {proximo_analista} inválido.")
                        distribuidor.desativar_usuario(proximo_analista)
                        tentativas += 1

                    else:  # status == "ERROR"
                        # Erro técnico ou timeout: Não desativa o usuário!
                        print(
                            f"Log (Maestro): [AVISO] Erro técnico com {proximo_analista}. Tentando próximo analista sem desativar...")
                        tentativas += 1

            self.logger.finalizar_sessao()
            print("Log (Maestro): Backlog processado com sucesso absoluto!")

        except Exception as e:
            msg_fatal = f"ERRO FATAL DURANTE A EXECUÇÃO: {str(e)}"
            print(f"Log (Maestro): {msg_fatal}")
            self.logger.registrar(msg_fatal)

        finally:
            # Encerra o navegador mas mantém o log salvo
            self.factory.encerrar()