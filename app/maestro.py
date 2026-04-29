from infra.browser_factory import BrowserFactory
from services.auth_service import AuthService
from services.radar_portal import RadarPortal
from infra.file_handler import FileHandler
from infra.audit_logger import AuditLogger
from core.distribuidor import DistribuidorRoundRobin
from core.fontes_pedidos import FontePortal, FonteListaFixa
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

            # 3. Portal
            portal = RadarPortal(context, page)
            portal.acessar_radar_classico()

            # Lemos a planilha bruta antes de tudo (Agora ela é uma lista mantendo a ordem exata do Excel)
            cotas_brutas = self.arquivos.ler_planilha_cotas(Config.PATH_COTAS)
            if not cotas_brutas:
                msg_erro = "Processo abortado ACT. Verifique os alertas do FileHandler."
                print(f"Log (Maestro): {msg_erro}")
                self.logger.registrar(f"ERRO: {msg_erro}")
                return

            # ==========================================================
            # --- DETECTOR DE MODO DE OPERAÇÃO E FILTRAGEM ---
            # ==========================================================
            # A "Regra de Ouro": A primeira linha do Excel define o jogo da rodada!
            primeira_linha = cotas_brutas[0]
            is_modo_limpeza = (primeira_linha['filtro'] == 'limpar')

            cotas_validas = {}
            usuarios_ignorados = []

            # Lê de cima para baixo. Quem obedecer à primeira linha entra, quem divergir (ou for duplicado) é ignorado.
            for linha in cotas_brutas:
                usr = linha['usuario']
                filtro = linha['filtro']
                cota = linha['cota']

                if is_modo_limpeza:
                    if filtro == 'limpar' and usr not in cotas_validas:
                        cotas_validas[usr] = {'cota': cota, 'filtro': filtro}
                    else:
                        usuarios_ignorados.append(f"{usr} ({filtro})")
                else: # Modo Alocação (meta, tudo ou lista)
                    if filtro in ['meta', 'tudo', 'lista'] and usr not in cotas_validas:
                        cotas_validas[usr] = {'cota': cota, 'filtro': filtro}
                    else:
                        usuarios_ignorados.append(f"{usr} ({filtro})")

            # Proteção caso TODOS os usuários tenham sido ignorados e não sobre ninguém para trabalhar
            if not cotas_validas:
                msg_erro = "Nenhum usuário válido sobrou para a operação após a filtragem. Abortando."
                print(f"Log (Maestro): {msg_erro}")
                self.logger.registrar(f"ERRO: {msg_erro}")
                return

            # ==========================================================
            # --- CAMINHO A: MODO LIMPEZA / EXPURGO ---
            # ==========================================================
            if is_modo_limpeza:
                print("\n========================================================")
                print("Log (Maestro): --- MODO LIMPEZA ATIVADO ---")
                print("========================================================\n")
                self.logger.iniciar_sessao("MÚLTIPLOS (MODO EXPURGO)")

                # Vai direto para Documentação (Sem baixar base e sem RoundRobin)
                portal.acessar_tela_documentacao()

                for analista in cotas_validas.keys():
                    print(f"Log (Maestro): Iniciando varredura para {analista}...")
                    removidos = portal.desalocar_pedidos_usuario(analista)

                    self.logger.registrar(f"LIMPEZA: {removidos} pedidos removidos de {analista}.")
                    print(f"Log (Maestro): [OK] Analista {analista} limpo! Total destravado: {removidos}.\n")

                # AVISO DE EXCEÇÃO NO FINAL
                if usuarios_ignorados:
                    alerta = f"AVISO: A rodada iniciou no modo EXPURGO. Analistas com filtro divergente ou duplicados foram ignorados: {', '.join(usuarios_ignorados)}"
                    print(f"Log (Maestro): {alerta}")
                    self.logger.registrar(alerta)

                self.logger.finalizar_sessao()
                print("Log (Maestro): Operação de Limpeza concluída com sucesso absoluto!")
                return  # Interrompe a execução, pois a limpeza terminou.

            # ==========================================================
            # --- CAMINHO B: MODO ALOCAÇÃO PADRÃO ---
            # ==========================================================
            is_modo_lista = (primeira_linha['filtro'] == 'lista')
            modo_label = "LISTA FIXA" if is_modo_lista else "ALOCAÇÃO"
            print("\n========================================================")
            print(f"Log (Maestro): --- MODO {modo_label} ATIVADO ---")
            print("========================================================\n")

            if is_modo_lista:
                fonte = FonteListaFixa(self.arquivos)
            else:
                fonte = FontePortal(portal, self.arquivos)

            backlog = fonte.obter_pedidos()

            if not backlog:
                print("Log (Maestro): Backlog vazio ou com erro. Abortando.")
                return

            total_cotas = sum(info['cota'] for info in cotas_validas.values())
            alocacoes_realizadas = 0

            distribuidor = DistribuidorRoundRobin(cotas_validas)
            self.logger.iniciar_sessao(total_cotas)
            portal.preparar_tela_alocacao()

            print(
                f"Log (Maestro): Iniciando rodada. Meta da equipe: {total_cotas} pedidos. (Backlog disponível: {len(backlog)}).")

            for item in backlog:
                if not distribuidor.analistas or alocacoes_realizadas >= total_cotas:
                    print(f"\nLog (Maestro): Meta atingida ou todas as cotas esgotadas! Encerrando.")
                    break

                pedido_id = item.get('Pedido')
                is_meta = item.get('IsMeta', False)

                sucesso_alocacao = False
                tentativas = 0
                max_tentativas = len(distribuidor.analistas)

                while not sucesso_alocacao and tentativas < max_tentativas:
                    proximo_analista = distribuidor.obter_proximo_usuario(is_meta)

                    if not proximo_analista:
                        break

                    print(
                        f"Log (Maestro): [{alocacoes_realizadas + 1}/{total_cotas}] Tentando Pedido {pedido_id} -> Analista {proximo_analista}")
                    status = portal.alocar_pedido(pedido_id, proximo_analista)

                    if status == "SUCCESS":
                        sucesso_alocacao = True
                        distribuidor.consumir_cota(proximo_analista)
                        alocacoes_realizadas += 1
                        self.logger.registrar(f"SUCESSO: Pedido {pedido_id} -> {proximo_analista}")
                        print(
                            f"Log (Maestro): [{alocacoes_realizadas}/{total_cotas}] [OK] Pedido {pedido_id} finalizado.")

                    elif status == "INVALID_LOGIN":
                        print(
                            f"Log (Maestro): [{alocacoes_realizadas + 1}/{total_cotas}] [ERRO] Login {proximo_analista} invalido.")
                        self.logger.registrar(f"FALHA: Login {proximo_analista} invalido para o pedido {pedido_id}.")
                        distribuidor.desativar_usuario(proximo_analista)
                        tentativas += 1

                    else:
                        print(
                            f"Log (Maestro): [{alocacoes_realizadas + 1}/{total_cotas}] [AVISO] Erro tecnico com {proximo_analista}.")
                        tentativas += 1

            # AVISO: pedidos da lista que sobraram sem ser alocados
            if is_modo_lista:
                pendentes = len(backlog) - alocacoes_realizadas
                if pendentes > 0:
                    aviso_lista = f"AVISO: {pendentes} pedido(s) da lista não foram alocados. Revise as cotas ou a disponibilidade dos analistas."
                    print(f"\nLog (Maestro): {aviso_lista}")
                    self.logger.registrar(aviso_lista)

            # AVISO DE EXCEÇÃO NO FINAL
            if usuarios_ignorados:
                alerta = f"AVISO: A rodada iniciou no modo {modo_label}. Analistas com filtro divergente ou duplicados foram ignorados: {', '.join(usuarios_ignorados)}"
                print(f"\nLog (Maestro): {alerta}")
                self.logger.registrar(alerta)

            self.logger.finalizar_sessao()
            print("Log (Maestro): Backlog ACT processado com sucesso absoluto!")

        except Exception as e:
            msg_fatal = f"ERRO FATAL DURANTE A EXECUÇÃO: {str(e)}"
            print(f"Log (Maestro): {msg_fatal}")
            self.logger.registrar(msg_fatal)

        finally:
            self.factory.encerrar()