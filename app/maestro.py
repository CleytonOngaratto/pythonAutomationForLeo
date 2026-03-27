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

            # 4. Processamento de Dados (Backlog e Matriz no Desktop)
            backlog = self.arquivos.ler_e_ordenar_backlog(nome_arquivo_base, "Data de Entrada")
            cotas = self.arquivos.ler_planilha_cotas(Config.PATH_COTAS)

            # O Maestro aborta se o FileHandler encontrou qualquer erro na planilha
            if not backlog or not cotas:
                msg_erro = "Processo abortado ACT. Verifique os alertas do FileHandler acima."
                print(f"Log (Maestro): {msg_erro}")
                self.logger.registrar(f"ERRO: {msg_erro}")
                return

            # --- CALCULANDO A META TOTAL DA EQUIPE ---
            total_cotas = sum(info['cota'] for info in cotas.values())
            alocacoes_realizadas = 0

            # 5. Configura o Distribuidor Roteador e inicia sessão de Log
            distribuidor = DistribuidorRoundRobin(cotas)
            self.logger.iniciar_sessao(total_cotas)
            portal.preparar_tela_alocacao()

            print(
                f"Log (Maestro): Iniciando rodada. Meta da equipe: {total_cotas} pedidos. (Backlog total disponível: {len(backlog)}).")

            # 6. Loop de Alocação com foco na META [X/Y]
            for item in backlog:

                # --- A TRAVA INTELIGENTE ---
                # Se não há mais ninguém na matriz com cota ou a meta foi batida, encerra!
                if not distribuidor.analistas or alocacoes_realizadas >= total_cotas:
                    print(f"\nLog (Maestro): Meta atingida ou todas as cotas esgotadas! Encerrando a rodada mais cedo.")
                    break

                pedido_id = item.get('Pedido')
                is_meta = item.get('IsMeta', False)

                sucesso_alocacao = False
                tentativas = 0
                max_tentativas = len(distribuidor.analistas)

                while not sucesso_alocacao and tentativas < max_tentativas:
                    proximo_analista = distribuidor.obter_proximo_usuario(is_meta)

                    if not proximo_analista:
                        # Tiramos o print de "ignorado" para não poluir a tela
                        break

                    # Exibe a próxima alocação pretendida e a meta
                    print(
                        f"Log (Maestro): [{alocacoes_realizadas + 1}/{total_cotas}] Tentando Pedido {pedido_id} -> Analista {proximo_analista}")

                    status = portal.alocar_pedido(pedido_id, proximo_analista)

                    if status == "SUCCESS":
                        sucesso_alocacao = True
                        distribuidor.consumir_cota(proximo_analista)

                        alocacoes_realizadas += 1  # Computa o sucesso

                        self.logger.registrar(f"SUCESSO: Pedido {pedido_id} -> {proximo_analista}")
                        print(
                            f"Log (Maestro): [{alocacoes_realizadas}/{total_cotas}] [OK] Pedido {pedido_id} finalizado.")

                    elif status == "INVALID_LOGIN":
                        print(
                            f"Log (Maestro): [{alocacoes_realizadas + 1}/{total_cotas}] [ERRO] Login {proximo_analista} invalido. Desativando...")
                        self.logger.registrar(f"FALHA: Login {proximo_analista} invalido para o pedido {pedido_id}.")
                        distribuidor.desativar_usuario(proximo_analista)
                        tentativas += 1

                    else:  # status == "ERROR"
                        print(
                            f"Log (Maestro): [{alocacoes_realizadas + 1}/{total_cotas}] [AVISO] Erro tecnico com {proximo_analista}. Tentando proximo analista...")
                        tentativas += 1

            self.logger.finalizar_sessao()
            print("Log (Maestro): Backlog ACT processado com sucesso absoluto!")

        except Exception as e:
            msg_fatal = f"ERRO FATAL DURANTE A EXECUÇÃO: {str(e)}"
            print(f"Log (Maestro): {msg_fatal}")
            self.logger.registrar(msg_fatal)

        finally:
            # Encerra o navegador mas mantém o log salvo
            self.factory.encerrar()