from app.orquestrador import Orquestrador

if __name__ == '__main__':
    # Cria o maestro e manda ele executar a extração e leitura
    app = Orquestrador()
    app.executar_fluxo_distribuicao(arquivo_cotas='cotas_teste.xlsx')
