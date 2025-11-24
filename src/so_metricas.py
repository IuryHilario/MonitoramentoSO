import psutil
from typing import Dict
import platform
import time


def coletar_metricas_so() -> Dict[str, float]:
    try:
        # Métricas básicas
        uso_cpu = psutil.cpu_percent(interval=1)
        memoria = psutil.virtual_memory()
        uso_memoria = memoria.percent

        # Determinar raiz do disco baseado no SO
        disco_raiz = '\\' if platform.system() == 'Windows' else '/'
        uso_disco = psutil.disk_usage(disco_raiz).percent

        # Memória de troca (Swap)
        swap = psutil.swap_memory()
        uso_swap = swap.percent

        # Métricas de I/O do disco
        latencia_disco = _calcular_latencia_disco()

        metricas = {
            'uso_cpu': uso_cpu,
            'uso_memoria': uso_memoria,
            'uso_disco': uso_disco,
            'uso_swap': uso_swap,
            'latencia_disco_ms': latencia_disco,
            'cpu_cores': psutil.cpu_count(),
            'memoria_total_gb': round(memoria.total / (1024 ** 3), 2),
            'memoria_usada_gb': round(memoria.used / (1024 ** 3), 2),
            'disco_total_gb': round(psutil.disk_usage(disco_raiz).total / (1024 ** 3), 2),
            'disco_usado_gb': round(psutil.disk_usage(disco_raiz).used / (1024 ** 3), 2),
        }

        return metricas
    except Exception as e:
        raise Exception(f"Erro ao coletar métricas do SO: {str(e)}")


def _calcular_latencia_disco() -> float:
    """
    Calcula latência do disco através de duas leituras de I/O counters
    A diferença entre as duas leituras simula a latência real do disco
    """
    try:
        # Primeira leitura
        io1 = psutil.disk_io_counters()
        if not io1:
            return 0.0

        # Espera pequeno
        time.sleep(0.1)

        # Segunda leitura
        io2 = psutil.disk_io_counters()
        if not io2:
            return 0.0

        # Calcula diferenças
        read_count_delta = io2.read_count - io1.read_count
        read_time_delta = io2.read_time - io1.read_time
        write_count_delta = io2.write_count - io1.write_count
        write_time_delta = io2.write_time - io1.write_time

        total_operations = read_count_delta + write_count_delta
        total_time = read_time_delta + write_time_delta

        # Se houve operações, calcula latência média
        if total_operations > 0 and total_time > 0:
            latencia = total_time / total_operations
            return round(latencia, 2)

        # Fallback: tenta com dados cumulativos
        total_ops = io2.read_count + io2.write_count
        total_tm = io2.read_time + io2.write_time

        if total_ops > 0 and total_tm > 0:
            latencia = total_tm / total_ops
            return round(latencia, 2)

        return 0.0
    except Exception as e:
        return 0.0