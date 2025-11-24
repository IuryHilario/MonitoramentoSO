import mysql.connector
from typing import Dict, Any, Optional
import time


def conectar_banco(host: str, usuario: str, senha: str, banco: str = "mysql") -> Optional[mysql.connector.MySQLConnection]:
    """
    Conecta ao banco de dados MySQL

    Args:
        host: Nome ou IP do servidor
        usuario: Usuário do banco
        senha: Senha do usuário
        banco: Nome do banco de dados

    Returns:
        Conexão com o banco ou None se falhar
    """
    try:
        conexao = mysql.connector.connect(
            host=host,
            user=usuario,
            password=senha,
            database=banco,
            autocommit=True,
            use_pure=True
        )
        return conexao
    except Exception as e:
        raise Exception(f"Erro ao conectar ao banco de dados: {str(e)}")


def coletar_metricas_db(conexao: Optional[mysql.connector.MySQLConnection] = None) -> Dict[str, Any]:
    """
    Coleta métricas do banco de dados MySQL

    Args:
        conexao: Conexão ativa com o banco de dados

    Returns:
        Dicionário com as métricas coletadas
    """
    try:
        if conexao is None or not conexao.is_connected():
            return {
                'status': 'Desconectado',
                'conexoes_ativas': 0,
                'tempo_resposta': 0,
                'queries_lentas': [],
                'versao': 'N/A',
                'uptime': 0,
                'tabelas': 0,
                'tamanho_db': '0 MB'
            }

        conexoes_ativas = 0
        versao = 'N/A'
        uptime = 0
        tabelas = 0
        tamanho_db = '0 MB'
        tempo_resposta = 0
        queries_lentas = []

        try:
            cursor = conexao.cursor(dictionary=True)

            # Medir latência de resposta do BD
            inicio = time.time()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            tempo_resposta = round((time.time() - inicio) * 1000, 2)  # Converter para ms
            cursor.fetchall()

            # Obter status do servidor
            cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
            resultado = cursor.fetchone()
            conexoes_ativas = int(resultado['Value']) if resultado else 0
            cursor.fetchall()

            # Obter versão do MySQL
            cursor.execute("SELECT VERSION() as versao")
            resultado = cursor.fetchone()
            versao = resultado['versao'] if resultado else 'N/A'
            cursor.fetchall()

            # Obter uptime
            cursor.execute("SHOW STATUS LIKE 'Uptime'")
            resultado = cursor.fetchone()
            uptime = int(resultado['Value']) if resultado else 0
            cursor.fetchall()

            # Contar tabelas
            cursor.execute("SELECT COUNT(*) as total FROM information_schema.tables WHERE table_schema != 'information_schema' AND table_schema != 'mysql' AND table_schema != 'performance_schema' AND table_schema != 'sys'")
            resultado = cursor.fetchone()
            tabelas = resultado['total'] if resultado else 0
            cursor.fetchall()

            # Obter tamanho do banco
            cursor.execute("""
                SELECT ROUND(COALESCE(SUM(data_length + index_length), 0) / 1024 / 1024, 2) as tamanho
                FROM information_schema.tables
                WHERE table_schema != 'information_schema' AND table_schema != 'mysql' AND table_schema != 'performance_schema' AND table_schema != 'sys'
            """)
            resultado = cursor.fetchone()
            tamanho_db = f"{resultado['tamanho']} MB" if resultado and resultado['tamanho'] else '0 MB'
            cursor.fetchall()

            # Coletar queries lentas (PROCESSLIST)
            queries_lentas = _coletar_queries_lentas(cursor)

            cursor.close()

        except Exception as e:
            raise Exception(f"Erro ao executar queries: {str(e)}")

        metricas_db = {
            'status': 'Conectado',
            'conexoes_ativas': conexoes_ativas,
            'tempo_resposta': tempo_resposta,
            'queries_lentas': queries_lentas,
            'versao': versao,
            'uptime': uptime,
            'tabelas': tabelas,
            'tamanho_db': tamanho_db
        }

        return metricas_db

    except Exception as e:
        raise Exception(f"Erro ao coletar métricas do banco de dados: {str(e)}")


def _coletar_queries_lentas(cursor) -> list:
    """
    Coleta queries ativas e identifica as que estão demorando

    Args:
        cursor: Cursor da conexão MySQL

    Returns:
        Lista de dicionários com info de queries lentas
    """
    try:
        queries_lentas = []

        # Verificar se performance_schema está habilitado
        cursor.execute("SHOW STATUS LIKE 'performance_schema'")
        resultado = cursor.fetchone()
        cursor.fetchall()

        # Obter queries ativas com tempo de execução
        cursor.execute("""
            SELECT
                ID,
                USER,
                HOST,
                DB,
                COMMAND,
                TIME,
                STATE,
                INFO
            FROM INFORMATION_SCHEMA.PROCESSLIST
            WHERE COMMAND != 'Sleep' AND TIME > 0
            ORDER BY TIME DESC
            LIMIT 10
        """)

        resultados = cursor.fetchall()
        cursor.fetchall()

        for row in resultados:
            tempo_execucao = int(row.get('TIME', 0))

            # Considerar como "lenta" se tempo > 5 segundos
            if tempo_execucao > 5:
                queries_lentas.append({
                    'id': row.get('ID'),
                    'usuario': row.get('USER', 'desconhecido'),
                    'banco': row.get('DB', 'N/A'),
                    'comando': row.get('COMMAND', 'N/A'),
                    'tempo_segundos': tempo_execucao,
                    'estado': row.get('STATE', 'N/A'),
                    'query': (row.get('INFO', 'N/A')[:100] + '...') if len(str(row.get('INFO', ''))) > 100 else row.get('INFO', 'N/A')
                })

        return queries_lentas if queries_lentas else []

    except Exception as e:
        # Se a query falhar, retornar lista vazia ao invés de lançar erro
        return []