import pandas as pd
import os
from config import Config


class FileHandler:
    """
    Responsabilidade: Tratamento e limpeza de dados (Excel e TSV).
    SOLID: SRP - Lógica exclusiva de manipulação de arquivos.
    """

    def ler_planilha_cotas(self, caminho: str):
        """Lê a planilha de analistas e transforma em um dicionário de trabalho."""
        try:
            # Planilha de cotas costuma ser .xlsx real (criada por nós)
            df = pd.read_excel(caminho, engine='openpyxl')

            # Cria o dicionário { 'T3763660': 10, 'T1234': 5 }
            cotas_dict = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))
            return cotas_dict
        except Exception as e:
            print(f"Log (FileHandler): Erro ao ler planilha de cotas: {e}")
            return None

    def ler_e_ordenar_backlog(self, nome_arquivo: str, coluna_data: str):
        """Lê o export do Radar dentro da pasta de bases extraídas."""
        caminho_completo = os.path.join(Config.PATH_BASES_EXTRAIDAS, nome_arquivo)

        print(f"Log (FileHandler): Inspecionando o arquivo {caminho_completo}...")

        try:
            # 1. Leitura do TSV da TIM (UTF-16)
            df = pd.read_csv(caminho_completo, sep='\t', encoding='utf-16', decimal=',', thousands='.')

            # 2. DEDUPLICAÇÃO: Garante que cada pedido apareça apenas uma vez
            # O Radar exporta uma linha por acesso, aqui filtramos para o pedido único
            total_antes = len(df)
            df = df.drop_duplicates(subset=['Pedido'])
            total_depois = len(df)

            if total_antes != total_depois:
                print(f"Log (FileHandler): Removidos {total_antes - total_depois} registros duplicados/acessos.")

            # 3. AJUSTE DINÂMICO DE COLUNA: Resolve 'Data Entrada' vs 'Data de Entrada'
            if coluna_data not in df.columns:
                colunas_possiveis = [c for c in df.columns if 'Data' in c and 'Entrada' in c]
                if colunas_possiveis:
                    coluna_data = colunas_possiveis[0]
                else:
                    print(f"Log (FileHandler): Erro - Coluna de data não encontrada. Colunas: {list(df.columns)}")
                    return None

            # 4. FILTRO 'USUÁRIO TRATANDO': Pega apenas o que está livre (NaN ou Vazio)
            if 'Usuario Tratando' in df.columns:
                print("Log (FileHandler): Filtrando apenas pedidos sem operador...")
                df = df[df['Usuario Tratando'].isna() | (df['Usuario Tratando'].astype(str).str.strip() == '')]

            # 5. LIMPEZA E CONVERSÃO: Garante que 'Pedido' seja número e remove lixo
            df['Pedido'] = pd.to_numeric(df['Pedido'], errors='coerce')
            df = df.dropna(subset=['Pedido'])

            # 6. ORDENAÇÃO FIFO: Do mais antigo para o mais novo
            # 'dayfirst=True' é vital para o formato brasileiro DD/MM/AAAA
            df[coluna_data] = pd.to_datetime(df[coluna_data], dayfirst=True, errors='coerce')
            df = df.sort_values(by=coluna_data, ascending=True)

            print(f"Log (FileHandler): Backlog finalizado! {len(df)} pedidos ÚNICOS prontos para alocação.")
            return df.to_dict('records')

        except Exception as e:
            print(f"Log (FileHandler): Erro crítico no processamento: {e}")
            return None