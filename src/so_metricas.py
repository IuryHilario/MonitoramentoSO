import psutil
from typing import Dict


def coletar_metricas_so() -> Dict[str, float]:
    try:
        uso_cpu = psutil.cpu_percent(interval=1)
        uso_memoria = psutil.virtual_memory().percent
        uso_disco = psutil.disk_usage('/').percent

        metricas = {
            'uso_cpu': uso_cpu,
            'uso_memoria': uso_memoria,
            'uso_disco': uso_disco
        }

        return metricas
    except Exception as e:
        raise Exception(f"Erro ao coletar métricas do SO: {str(e)}")