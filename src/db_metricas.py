import psutil
from typing import Dict, Any


def coletar_metricas_db() -> Dict[str, Any]:
    try:
        metricas_db = {
            'conexoes_ativas': 0,
            'tempo_resposta': 0,
            'queries_lentas': 0,
            'status': 'Sem conexão ao banco de dados'
        }
        return metricas_db
    except Exception as e:
        raise Exception(f"Erro ao coletar métricas do banco de dados: {str(e)}")