import pandas as pd
import os
from typing import List, Dict


class FileHandler:
    def __init__(self, pasta_trabalho: str = None):
        """
        Define onde o FileHandler vai procurar ou salvar arquivos.
        Se não passar nada, ele usa a pasta atual de execução.
        """
        self.pasta_trabalho = pasta_trabalho or os.getcwd()

    def ler_planilha_cotas(self, nome_arquivo: str) -> dict:
        """
        Lê uma planilha simples contendo duas colunas (ex: 'Usuario' e 'Cota').
        Retorna um dicionário que o Distribuidor consiga entender.
        Ex: {'T1234': 13, 'T5678': 15}
        """
        caminho_completo = os.path.join(self.pasta_trabalho, nome_arquivo)

        try:
            # Lê o Excel e transforma em um DataFrame do Pandas
            df = pd.read_excel(caminho_completo)

            # Remove linhas vazias
            df = df.dropna(subset=[df.columns[0], df.columns[1]])

            # Cria o dicionário: a primeira coluna vira a chave, a segunda vira o valor
            cotas = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

            # Garante que os valores das cotas sejam números inteiros
            cotas = {str(k).strip(): int(v) for k, v in cotas.items()}
            return cotas

        except Exception as e:
            print(f"Log (FileHandler): Erro ao ler planilha de cotas '{nome_arquivo}'. Detalhe: {e}")
            return {}

    def ler_e_ordenar_backlog(self, nome_arquivo: str, coluna_data: str = 'Data de Entrada') -> List[Dict]:
        """
        Lê o arquivo de exportação baixado, ordena os pedidos do mais antigo para o mais novo
        e retorna uma lista de dicionários pronta para o Orquestrador iterar.
        """
        caminho_completo = os.path.join(self.pasta_trabalho, nome_arquivo)

        try:
            df = pd.read_excel(caminho_completo)

            # Verifica se a coluna de data existe para evitar erros
            if coluna_data not in df.columns:
                print(f"Log (FileHandler): Aviso! A coluna '{coluna_data}' não foi encontrada.")
                # Opcional: imprimir quais colunas existem para ajudar no debug
                print(f"Colunas disponíveis: {list(df.columns)}")
                return []

            # Converte a coluna para o tipo Data (datetime) para garantir que a ordenação seja real e não alfabética
            df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')

            # Remove linhas onde a data é inválida ou nula
            df = df.dropna(subset=[coluna_data])

            # Ordena do mais antigo para o mais novo (ascending=True)
            df = df.sort_values(by=coluna_data, ascending=True)

            # Converte o DataFrame para uma lista de dicionários (cada linha vira um dict)
            # Ex: [{'Pedido': 101, 'Data de Entrada': '2026-01-01'}, {'Pedido': 102, ...}]
            lista_pedidos = df.to_dict(orient='records')

            return lista_pedidos

        except Exception as e:
            print(f"Log (FileHandler): Erro ao processar backlog '{nome_arquivo}'. Detalhe: {e}")
            return []