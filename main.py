import sys
from app.maestro import Maestro
from config import Config


def iniciar_automacao():

    print("Log (Main): Iniciando motor de automação...")

    # Validação de variáveis de ambiente obrigatórias
    obrigatorias = {
        "TIM_USER": Config.USER,
        "ROBO_PASS": Config.PASS,
        "URL_RADAR_START": Config.URL_RADAR_START,
        "CHROME_PATH": Config.CHROME_PATH,
        "USER_DATA_DIR": Config.CHROME_DATA_DIR,
    }
    ausentes = [nome for nome, valor in obrigatorias.items() if not valor]
    if ausentes:
        print(f"Log (Main): ERRO - Variáveis de ambiente não definidas: {', '.join(ausentes)}")
        print("Log (Main): Configure as variáveis no Windows antes de executar.")
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