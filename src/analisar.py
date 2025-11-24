import psutil
from typing import Dict, Any


def analisar_dados(dados_so: Dict[str, float], dados_db: Dict[str, Any]) -> Dict[str, Any]:
    try:
        alertas = []
        recomendacoes = []

        # ====== ANÁLISE DE CPU ======
        if dados_so.get('uso_cpu', 0) > 80:
            alertas.append("🔴 CRÍTICO: Uso de CPU muito alto (>80%)")
            recomendacoes.append("Verifique processos em execução e encerre desnecessários")
        elif dados_so.get('uso_cpu', 0) > 60:
            alertas.append("🟡 ALERTA: Uso de CPU alto (>60%)")
            recomendacoes.append("Monitore a atividade da CPU para evitar picos")

        # ====== ANÁLISE DE MEMÓRIA RAM ======
        if dados_so.get('uso_memoria', 0) > 85:
            alertas.append("🔴 CRÍTICO: Uso de Memória RAM crítico (>85%)")
            recomendacoes.append("Libere memória encerrando programas desnecessários ou aumente a RAM")
        elif dados_so.get('uso_memoria', 0) > 70:
            alertas.append("🟡 ALERTA: Uso de Memória RAM alto (>70%)")
            recomendacoes.append("Considere aumentar a memória RAM para evitar travamentos")

        # ====== ANÁLISE DE SWAP ======
        if dados_so.get('uso_swap', 0) > 50:
            alertas.append("🔴 CRÍTICO: Uso de Memória de Troca muito alto (>50%)")
            recomendacoes.append("Aumente a RAM do sistema urgentemente - o disco está sendo usado como memória")
        elif dados_so.get('uso_swap', 0) > 10:
            alertas.append("🟡 ALERTA: Uso de Memória de Troca detectado (>10%)")
            recomendacoes.append("Sistema está usando disco como memória - esto degradará performance")

        # ====== ANÁLISE DE DISCO ======
        if dados_so.get('uso_disco', 0) > 90:
            alertas.append("🔴 CRÍTICO: Espaço em Disco crítico (>90%)")
            recomendacoes.append("Libere espaço em disco imediatamente para evitar falhas de sistema")
        elif dados_so.get('uso_disco', 0) > 80:
            alertas.append("🟡 ALERTA: Espaço em Disco baixo (>80%)")
            recomendacoes.append("Limpe arquivos temporários e desnecessários para liberar espaço")

        # ====== ANÁLISE DE LATÊNCIA DO DISCO ======
        latencia_disco = dados_so.get('latencia_disco_ms', 0)
        if latencia_disco > 20:
            alertas.append(f"🔴 CRÍTICO: Latência do Disco muito alta ({latencia_disco:.2f}ms)")
            recomendacoes.append("Disco com problemas de I/O - considere verificar saúde do disco ou substituir")
        elif latencia_disco > 10:
            alertas.append(f"🟡 ALERTA: Latência do Disco elevada ({latencia_disco:.2f}ms)")
            recomendacoes.append("Disco apresenta atraso na leitura/escrita - monitore performance")

        # ====== ANÁLISE DO BANCO DE DADOS ======
        # Status da Conexão
        if dados_db.get('status', '') == 'Desconectado':
            alertas.append("🔴 CRÍTICO: Banco de Dados Desconectado")
            recomendacoes.append("Reconecte ao banco de dados para monitoramento")

        # Tempo de Resposta do BD
        tempo_resposta_bd = dados_db.get('tempo_resposta', 0)
        if tempo_resposta_bd > 100:
            alertas.append(f"🔴 CRÍTICO: Tempo de resposta do BD muito alto ({tempo_resposta_bd}ms)")
            recomendacoes.append("Banco de dados está lento - verifique queries ativas e índices")
        elif tempo_resposta_bd > 50:
            alertas.append(f"🟡 ALERTA: Tempo de resposta do BD elevado ({tempo_resposta_bd}ms)")
            recomendacoes.append("Monitore a performance do banco de dados")

        # Conexões Ativas
        conexoes = dados_db.get('conexoes_ativas', 0)
        if conexoes > 80:
            alertas.append(f"🟡 ALERTA: Muitas conexões ativas ({conexoes})")
            recomendacoes.append("Verifique se há muitos clientes conectados simultaneamente")

        # Queries Lentas
        queries_lentas = dados_db.get('queries_lentas', [])
        if queries_lentas and len(queries_lentas) > 0:
            alertas.append(f"🔴 CRÍTICO: {len(queries_lentas)} query(s) lenta(s) detectada(s)")
            recomendacoes.append("Otimize as queries lentas - adicione índices ou reescreva as consultas")

        # ====== DETERMINAÇÃO DO STATUS GERAL ======
        status_geral = "🟢 OK - Sistema operando normalmente"

        alertas_criticos = [a for a in alertas if "🔴" in a]
        alertas_avisos = [a for a in alertas if "🟡" in a]

        if alertas_criticos:
            status_geral = "🔴 CRÍTICO - Intervenção imediata necessária!"
        elif alertas_avisos:
            status_geral = "🟡 ALERTA - Atenção recomendada"

        analise = {
            'alertas': alertas if alertas else ["🟢 Nenhum alerta detectado"],
            'status_geral': status_geral,
            'recomendacoes': recomendacoes if recomendacoes else ["✓ Sistema operando normalmente"],
            'dados_so': dados_so,
            'dados_db': dados_db
        }

        return analise
    except Exception as e:
        raise Exception(f"Erro ao analisar dados: {str(e)}")