import psutil
from typing import Dict, Any


def analisar_dados(dados_so: Dict[str, float], dados_db: Dict[str, Any]) -> Dict[str, Any]:
    try:
        alertas = []
        recomendacoes = []

        # Analisar CPU
        if dados_so.get('uso_cpu', 0) > 80:
            alertas.append("🔴 Uso de CPU crítico (>80%)")
            recomendacoes.append("Verifique processos em execução e encerre desnecessários")
        elif dados_so.get('uso_cpu', 0) > 60:
            alertas.append("🟡 Uso de CPU alto (>60%)")
            recomendacoes.append("Monitore a atividade da CPU")

        # Analisar Memória
        if dados_so.get('uso_memoria', 0) > 85:
            alertas.append("🔴 Uso de Memória crítico (>85%)")
            recomendacoes.append("Libere memória encerrando programas desnecessários")
        elif dados_so.get('uso_memoria', 0) > 70:
            alertas.append("🟡 Uso de Memória alto (>70%)")
            recomendacoes.append("Considere aumentar a memória RAM")

        # Analisar Disco
        if dados_so.get('uso_disco', 0) > 90:
            alertas.append("🔴 Espaço em Disco crítico (>90%)")
            recomendacoes.append("Libere espaço em disco imediatamente")
        elif dados_so.get('uso_disco', 0) > 80:
            alertas.append("🟡 Espaço em Disco baixo (>80%)")
            recomendacoes.append("Limpe arquivos temporários e desnecessários")

        # Determinar status geral
        status_geral = "🟢 OK"
        if len([a for a in alertas if "🔴" in a]) > 0:
            status_geral = "🔴 CRÍTICO"
        elif len(alertas) > 0:
            status_geral = "🟡 AVISO"

        analise = {
            'alertas': alertas if alertas else ["Nenhum alerta detectado"],
            'status_geral': status_geral,
            'recomendacoes': recomendacoes if recomendacoes else ["Sistema operando normalmente"],
            'dados_so': dados_so,
            'dados_db': dados_db
        }

        return analise
    except Exception as e:
        raise Exception(f"Erro ao analisar dados: {str(e)}")