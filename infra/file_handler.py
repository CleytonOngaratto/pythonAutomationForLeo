import pandas as pd
import os


class FileHandler:
    def ler_planilha_cotas(self, caminho: str):
        try:
            df = pd.read_excel(caminho, engine='openpyxl')
            cotas_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            return cotas_dict
        except Exception as e:
            print(f"Log (FileHandler): Erro ao ler cotas: {e}")
            return None

    def ler_e_ordenar_backlog(self, nome_arquivo: str, coluna_data: str):
        caminho_completo = os.path.join(os.getcwd(), nome_arquivo)
        print(f"Log (FileHandler): Inspecionando o arquivo {nome_arquivo}...")

        try:
            # O MISTÉRIO REVELADO: Lendo diretamente como texto tabulado (TSV) em UTF-16
            print("Log (FileHandler): Lendo arquivo TSV disfarçado de Excel...")
            df = pd.read_csv(caminho_completo, sep='\t', encoding='utf-16', decimal=',', thousands='.')

            if coluna_data not in df.columns:
                print(f"Log (FileHandler): Coluna '{coluna_data}' não encontrada! Colunas: {list(df.columns)}")
                return None

            print("Log (FileHandler): Limpando e Ordenando pedidos...")

            # Força a coluna 'Pedido' a ser número. Linhas vazias viram nulo.
            df['Pedido'] = pd.to_numeric(df['Pedido'], errors='coerce')
            df = df.dropna(subset=['Pedido'])

            # Converte a data (Ajustado para o formato exato da TIM com segundos)
            df[coluna_data] = pd.to_datetime(df[coluna_data], format='%d/%m/%Y %H:%M:%S', errors='coerce')

            # Ordena do mais velho para o mais novo
            df = df.sort_values(by=coluna_data, ascending=True)

            print(f"Log (FileHandler): Backlog processado com sucesso! Total de pedidos reais válidos: {len(df)}")
            return df.to_dict('records')

        except Exception as e:
            print(f"Log (FileHandler): Erro ao processar backlog '{nome_arquivo}'. Detalhe: {e}")
            return None