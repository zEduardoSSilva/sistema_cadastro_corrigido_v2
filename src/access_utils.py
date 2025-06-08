import pyodbc

def get_access_tables(db_path):
    """
    Função auxiliar para listar todas as tabelas em um banco de dados Access.
    
    Args:
        db_path (str): Caminho completo para o arquivo de banco de dados Access (.accdb ou .mdb)
        
    Returns:
        list: Lista de nomes de tabelas encontradas no banco de dados
    """
    try:
        # Determinar o driver correto com base na extensão do arquivo
        if db_path.endswith('.accdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};'
        elif db_path.endswith('.mdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={db_path};'
        else:
            return []
        
        # Conectar ao banco de dados
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Obter lista de tabelas (excluindo tabelas do sistema)
        tables = []
        for row in cursor.tables():
            if row.table_type == 'TABLE' and not row.table_name.startswith('MSys'):
                tables.append(row.table_name)
        
        cursor.close()
        conn.close()
        
        return tables
    except Exception as e:
        print(f"Erro ao listar tabelas: {str(e)}")
        return []

def get_table_columns(db_path, table_name):
    """
    Função auxiliar para obter os nomes e tipos das colunas de uma tabela Access.
    
    Args:
        db_path (str): Caminho completo para o arquivo de banco de dados Access
        table_name (str): Nome da tabela para obter as colunas
        
    Returns:
        list: Lista de dicionários com informações das colunas (nome, tipo, etc.)
    """
    try:
        # Determinar o driver correto com base na extensão do arquivo
        if db_path.endswith('.accdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};'
        elif db_path.endswith('.mdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={db_path};'
        else:
            return []
        
        # Conectar ao banco de dados
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Obter informações das colunas
        columns = []
        for row in cursor.columns(table=table_name):
            column_info = {
                'name': row.column_name,
                'type': row.type_name,
                'nullable': row.nullable == 1,
                'size': row.column_size
            }
            columns.append(column_info)
        
        cursor.close()
        conn.close()
        
        return columns
    except Exception as e:
        print(f"Erro ao obter colunas: {str(e)}")
        return []

def execute_query(db_path, query, params=None, fetch=True):
    """
    Função auxiliar para executar consultas SQL em um banco de dados Access.
    
    Args:
        db_path (str): Caminho completo para o arquivo de banco de dados Access
        query (str): Consulta SQL a ser executada
        params (tuple, optional): Parâmetros para a consulta. Defaults to None.
        fetch (bool, optional): Se deve retornar resultados. Defaults to True.
        
    Returns:
        list/bool: Resultados da consulta ou True se bem-sucedido (para INSERT/UPDATE/DELETE)
    """
    try:
        # Determinar o driver correto com base na extensão do arquivo
        if db_path.endswith('.accdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};'
        elif db_path.endswith('.mdb'):
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={db_path};'
        else:
            return None
        
        # Conectar ao banco de dados
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Executar a consulta
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Retornar resultados ou confirmar execução
        if fetch:
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        print(f"Erro ao executar consulta: {str(e)}")
        return None
