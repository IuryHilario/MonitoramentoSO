import psutil
from datetime import datetime
from typing import Dict, Any


def formatar_relatorio(analise: Dict[str, Any]) -> str:
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relatorio_texto = ""

        relatorio_texto += "=" * 70 + "\n"
        relatorio_texto += "RELATÓRIO DE DIAGNÓSTICO DE DESEMPENHO DO SISTEMA\n"
        relatorio_texto += "=" * 70 + "\n\n"

        relatorio_texto += f"Data e Hora: {timestamp}\n"
        relatorio_texto += f"Sistema: {_get_info_sistema()}\n\n"

        relatorio_texto += "-" * 70 + "\n"
        relatorio_texto += "STATUS GERAL DO SISTEMA\n"
        relatorio_texto += "-" * 70 + "\n"
        relatorio_texto += f"{analise.get('status_geral', 'Desconhecido')}\n\n"

        relatorio_texto += "-" * 70 + "\n"
        relatorio_texto += "MÉTRICAS DO SISTEMA OPERACIONAL\n"
        relatorio_texto += "-" * 70 + "\n"
        dados_so = analise.get('dados_so', {})
        relatorio_texto += f"CPU:     {dados_so.get('uso_cpu', 0):.2f}%\n"
        relatorio_texto += f"Memória: {dados_so.get('uso_memoria', 0):.2f}%\n"
        relatorio_texto += f"Disco:   {dados_so.get('uso_disco', 0):.2f}%\n\n"

        relatorio_texto += "-" * 70 + "\n"
        relatorio_texto += "ALERTAS DETECTADOS\n"
        relatorio_texto += "-" * 70 + "\n"
        for alerta in analise.get('alertas', []):
            relatorio_texto += f"• {alerta}\n"
        relatorio_texto += "\n"

        relatorio_texto += "-" * 70 + "\n"
        relatorio_texto += "RECOMENDAÇÕES\n"
        relatorio_texto += "-" * 70 + "\n"
        for recom in analise.get('recomendacoes', []):
            relatorio_texto += f"• {recom}\n"
        relatorio_texto += "\n"

        relatorio_texto += "=" * 70 + "\n"
        relatorio_texto += "Fim do Relatório\n"
        relatorio_texto += "=" * 70 + "\n"

        return relatorio_texto

    except Exception as e:
        raise Exception(f"Erro ao formatar relatório: {str(e)}")


def gerar_relatorio_arquivo(analise: Dict[str, Any]) -> str:
    try:
        nome_arquivo = f"relatorio_diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        relatorio_texto = formatar_relatorio(analise)

        with open(nome_arquivo, 'w', encoding='utf-8') as relatorio:
            relatorio.write(relatorio_texto)

        print(f"✅ Relatório gerado com sucesso: {nome_arquivo}")
        return nome_arquivo

    except Exception as e:
        raise Exception(f"Erro ao gerar relatório: {str(e)}")


def _get_info_sistema() -> str:
    try:
        import platform
        sistema = platform.system()
        versao = platform.release()
        processador = platform.processor()
        return f"{sistema} {versao} ({processador})"
    except:
        return "Sistema desconhecido"