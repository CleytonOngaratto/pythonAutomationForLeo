import sys
from app.maestro import Maestro
from config import Config


def iniciar_automacao():

    print("Log (Main): Iniciando motor de automação...")

    # Validação básica de segurança
    if not Config.USER or not Config.PASS:
        print("Log (Main): ERRO - Usuário ou Senha não encontrados.")
        return

    try:
        # Instancia o Maestro (O capitão do robô)
        robo = Maestro()

        # Executa o ciclo completo
        robo.executar(Config.USER, Config.PASS)

    except KeyboardInterrupt:
        print("\nLog (Main): Automação interrompida manualmente pelo usuário.")
    except Exception as e:
        print(f"Log (Main): Ocorreu um erro inesperado: {e}")
    finally:
        print("Log (Main): Encerrando aplicação.")


if __name__ == "__main__":
    iniciar_automacao()