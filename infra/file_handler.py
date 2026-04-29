import pandas as pd
import os
from config import Config


class FileHandler:

    def ler_planilha_cotas(self, caminho: str):
        try:
            df = pd.read_excel(caminho, engine='openpyxl')
            df.columns = df.columns.str.lower().str.strip()

            if 'usuario' not in df.columns or 'cota' not in df.columns or 'filtro' not in df.columns:
                print("Log (FileHandler): [ERRO FATAL] As colunas devem se chamar: 'Usuario', 'Cota' e 'Filtro'.")
                return None

            # Apaga da memória do robô qualquer linha onde a coluna "usuario" esteja vazia (Legendas)
            df = df.dropna(subset=['usuario'])

            if df['filtro'].isnull().any():
                print("Log (FileHandler): [ERRO FATAL] Existem analistas com a coluna 'Filtro' em branco.")
                return None

            df['filtro'] = df['filtro'].astype(str).str.lower().str.strip()
            df['cota'] = pd.to_numeric(df['cota'], errors='coerce').fillna(0).astype(int)

            valores_invalidos = df[~df['filtro'].isin(['meta', 'tudo', 'limpar', 'lista'])]
            if not valores_invalidos.empty:
                errados = valores_invalidos['filtro'].unique()
                print(
                    f"Log (FileHandler): [ERRO FATAL] Filtro inválido: {errados}. Use apenas 'meta', 'tudo', 'limpar' ou 'lista'.")
                return None

            # --- LÓGICA: Retorna uma lista na ordem exata do Excel ---
            cotas_lista = []
            for index, row in df.iterrows():
                cotas_lista.append({
                    'usuario': str(row['usuario']).strip(),  # Mantém a formatação exata da planilha
                    'cota': int(row['cota']),
                    'filtro': row['filtro']
                })
            return cotas_lista

        except Exception as e:
            print(f"Log (FileHandler): Erro ao ler a planilha: {e}")
            return None

    def ler_e_ordenar_backlog(self, nome_arquivo: str, coluna_data: str):
        caminho_completo = os.path.join(Config.PATH_BASES_EXTRAIDAS, nome_arquivo)
        print(f"Log (FileHandler): Inspecionando o arquivo {caminho_completo}...")
        try:
            df = pd.read_csv(caminho_completo, sep='\t', encoding='utf-16', decimal=',', thousands='.')
            df = df.drop_duplicates(subset=['Pedido'])

            if 'Usuario Tratando' in df.columns:
                df = df[df['Usuario Tratando'].isna() | (df['Usuario Tratando'].astype(str).str.strip() == '')]

            coluna_tipo = 'Tipo de Contratação'
            tipos_meta = ['Novo', 'Renegociação + Aditivo', 'Aditivo']

            if coluna_tipo in df.columns:
                df[coluna_tipo] = df[coluna_tipo].astype(str).str.strip()
                df['IsMeta'] = df[coluna_tipo].isin(tipos_meta)
            else:
                df['IsMeta'] = False

            df['Pedido'] = pd.to_numeric(df['Pedido'], errors='coerce')
            df = df.dropna(subset=['Pedido'])

            colunas_possiveis = [c for c in df.columns if 'Data' in c and 'Entrada' in c]
            coluna_data_real = colunas_possiveis[0] if colunas_possiveis else coluna_data

            df[coluna_data_real] = pd.to_datetime(df[coluna_data_real], dayfirst=True, errors='coerce')
            df = df.sort_values(by=coluna_data_real, ascending=True)

            print(f"Log (FileHandler): Backlog finalizado! {len(df)} pedidos prontos.")
            return df.to_dict('records')

        except Exception as e:
            print(f"Log (FileHandler): Erro crítico no processamento: {e}")
            return None

    def ler_lista_pedidos(self, caminho: str):
        try:
            df = pd.read_excel(caminho, sheet_name='ListaPedidos', engine='openpyxl')
            df.columns = df.columns.str.lower().str.strip()

            if 'pedido' not in df.columns:
                print("Log (FileHandler): [ERRO FATAL] Aba 'Pedidos' não tem coluna 'Pedido'.")
                return None

            pedidos_validos = pd.to_numeric(df['pedido'], errors='coerce').dropna()

            if pedidos_validos.empty:
                print("Log (FileHandler): [ERRO FATAL] Aba 'Pedidos' não contém nenhum número válido.")
                return None

            print(f"Log (FileHandler): Lista de pedidos carregada! {len(pedidos_validos)} pedidos.")
            return [{'Pedido': int(p), 'IsMeta': True} for p in pedidos_validos]

        except ValueError:
            print("Log (FileHandler): [ERRO FATAL] Aba 'ListaPedidos' não encontrada no Excel.")
            return None
        except Exception as e:
            print(f"Log (FileHandler): Erro ao ler lista de pedidos: {e}")
            return None