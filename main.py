from app.orquestrador import Orquestrador

if __name__ == '__main__':
    # O arquivo cotas_teste.xlsx já existe na sua pasta por conta do teste anterior
    app = Orquestrador()
    app.executar_fluxo_distribuicao(arquivo_cotas='cotas_teste.xlsx')