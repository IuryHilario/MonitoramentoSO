import psutil
from datetime import datetime
from typing import Dict, Any


def formatar_relatorio(analise: Dict[str, Any]) -> str:
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        relatorio_texto = ""

        relatorio_texto += "=" * 80 + "\n"
        relatorio_texto += "RELATÓRIO DE DIAGNÓSTICO DE DESEMPENHO DO SISTEMA\n"
        relatorio_texto += "=" * 80 + "\n\n"

        relatorio_texto += f"Data e Hora: {timestamp}\n"
        relatorio_texto += f"Sistema: {_get_info_sistema()}\n\n"

        relatorio_texto += "-" * 80 + "\n"
        relatorio_texto += "STATUS GERAL DO SISTEMA\n"
        relatorio_texto += "-" * 80 + "\n"
        relatorio_texto += f"{analise.get('status_geral', 'Desconhecido')}\n\n"

        relatorio_texto += "-" * 80 + "\n"
        relatorio_texto += "MÉTRICAS DO SISTEMA OPERACIONAL\n"
        relatorio_texto += "-" * 80 + "\n"
        dados_so = analise.get('dados_so', {})
        relatorio_texto += f"CPU:                      {dados_so.get('uso_cpu', 0):.2f}%\n"
        relatorio_texto += f"Memória RAM:              {dados_so.get('uso_memoria', 0):.2f}%\n"
        relatorio_texto += f"Memória em Uso (GB):      {dados_so.get('memoria_usada_gb', 0):.2f} / {dados_so.get('memoria_total_gb', 0):.2f} GB\n"
        relatorio_texto += f"Memória de Troca (Swap):  {dados_so.get('uso_swap', 0):.2f}%\n"
        relatorio_texto += f"Disco:                    {dados_so.get('uso_disco', 0):.2f}%\n"
        relatorio_texto += f"Disco em Uso (GB):        {dados_so.get('disco_usado_gb', 0):.2f} / {dados_so.get('disco_total_gb', 0):.2f} GB\n"
        relatorio_texto += f"Latência do Disco (ms):   {dados_so.get('latencia_disco_ms', 0):.2f}\n"
        relatorio_texto += f"CPU Cores:                {dados_so.get('cpu_cores', 'N/A')}\n\n"

        relatorio_texto += "-" * 80 + "\n"
        relatorio_texto += "MÉTRICAS DO BANCO DE DADOS\n"
        relatorio_texto += "-" * 80 + "\n"
        dados_db = analise.get('dados_db', {})
        relatorio_texto += f"Status:                   {dados_db.get('status', '--')}\n"
        relatorio_texto += f"Versão:                   {dados_db.get('versao', '--')}\n"
        relatorio_texto += f"Conexões Ativas:          {dados_db.get('conexoes_ativas', 0)}\n"
        relatorio_texto += f"Tempo de Resposta (ms):   {dados_db.get('tempo_resposta', 0)}\n"
        relatorio_texto += f"Uptime:                   {_formatar_uptime(dados_db.get('uptime', 0))}\n"
        relatorio_texto += f"Tabelas:                  {dados_db.get('tabelas', 0)}\n"
        relatorio_texto += f"Tamanho do Banco:         {dados_db.get('tamanho_db', '0 MB')}\n\n"

        # Consultas Lentas
        queries_lentas = dados_db.get('queries_lentas', [])
        relatorio_texto += "-" * 80 + "\n"
        relatorio_texto += "CONSULTAS LENTAS DETECTADAS\n"
        relatorio_texto += "-" * 80 + "\n"
        if queries_lentas:
            for idx, query in enumerate(queries_lentas, 1):
                if isinstance(query, dict):
                    relatorio_texto += f"\n{idx}. Tempo: {query.get('tempo_segundos', 0)}s | Usuário: {query.get('usuario', 'N/A')}\n"
                    relatorio_texto += f"   Banco: {query.get('banco', 'N/A')} | Comando: {query.get('comando', 'N/A')}\n"
                    relatorio_texto += f"   Estado: {query.get('estado', 'N/A')}\n"
                    relatorio_texto += f"   Query: {query.get('query', 'N/A')}\n"
        else:
            relatorio_texto += "Nenhuma query lenta detectada\n\n"

        relatorio_texto += "\n" + "-" * 80 + "\n"
        relatorio_texto += "ALERTAS DETECTADOS\n"
        relatorio_texto += "-" * 80 + "\n"
        for alerta in analise.get('alertas', []):
            relatorio_texto += f"• {alerta}\n"
        relatorio_texto += "\n"

        relatorio_texto += "-" * 80 + "\n"
        relatorio_texto += "RECOMENDAÇÕES\n"
        relatorio_texto += "-" * 80 + "\n"
        for recom in analise.get('recomendacoes', []):
            relatorio_texto += f"• {recom}\n"
        relatorio_texto += "\n"

        relatorio_texto += "=" * 80 + "\n"
        relatorio_texto += "Fim do Relatório\n"
        relatorio_texto += "=" * 80 + "\n"

        return relatorio_texto

    except Exception as e:
        raise Exception(f"Erro ao formatar relatório: {str(e)}")


def formatar_relatorio_html(analise: Dict[str, Any]) -> str:
    """
    Gera um relatório em formato HTML com estilo

    Args:
        analise: Dicionário com os dados da análise

    Returns:
        String contendo o HTML do relatório
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dados_so = analise.get('dados_so', {})
        dados_db = analise.get('dados_db', {})

        # Definir classe CSS para status
        status_classe = "status-critico" if "CRÍTICO" in analise.get('status_geral', '') else \
                       "status-aviso" if "AVISO" in analise.get('status_geral', '') else "status-ok"

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Diagnóstico de Desempenho</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .content {{
            padding: 40px;
        }}

        .status-badge {{
            display: inline-block;
            padding: 12px 20px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 20px;
        }}

        .status-ok {{
            background: #d4edda;
            color: #155724;
        }}

        .status-aviso {{
            background: #fff3cd;
            color: #856404;
        }}

        .status-critico {{
            background: #f8d7da;
            color: #721c24;
        }}

        .section {{
            margin-bottom: 40px;
        }}

        .section h2 {{
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            color: #667eea;
            font-size: 20px;
            margin-bottom: 20px;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}

        .metric-card h3 {{
            color: #667eea;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}

        .metric-value {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 8px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
            width: var(--percentage);
        }}

        .alert-item {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}

        .alert-item.critico {{
            background: #f8d7da;
            border-left-color: #dc3545;
        }}

        .recommendation-item {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 4px;
        }}

        .queries-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        .queries-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-size: 13px;
        }}

        .queries-table td {{
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}

        .queries-table tr:hover {{
            background: #f8f9fa;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ Diagnóstico de Desempenho do Sistema</h1>
            <p>Relatório gerado em {timestamp}</p>
        </div>

        <div class="content">
            <!-- Status Geral -->
            <div class="status-badge {status_classe}">
                {analise.get('status_geral', 'Desconhecido')}
            </div>

            <!-- Métricas SO -->
            <div class="section">
                <h2>📊 Métricas do Sistema Operacional</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>CPU</h3>
                        <div class="metric-value">{dados_so.get('uso_cpu', 0):.1f}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="--percentage: {min(dados_so.get('uso_cpu', 0), 100)}%"></div>
                        </div>
                    </div>

                    <div class="metric-card">
                        <h3>Memória RAM</h3>
                        <div class="metric-value">{dados_so.get('uso_memoria', 0):.1f}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="--percentage: {min(dados_so.get('uso_memoria', 0), 100)}%"></div>
                        </div>
                        <p style="font-size: 12px; margin-top: 5px;">{dados_so.get('memoria_usada_gb', 0):.2f} / {dados_so.get('memoria_total_gb', 0):.2f} GB</p>
                    </div>

                    <div class="metric-card">
                        <h3>Memória de Troca</h3>
                        <div class="metric-value">{dados_so.get('uso_swap', 0):.1f}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="--percentage: {min(dados_so.get('uso_swap', 0), 100)}%"></div>
                        </div>
                    </div>

                    <div class="metric-card">
                        <h3>Disco</h3>
                        <div class="metric-value">{dados_so.get('uso_disco', 0):.1f}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="--percentage: {min(dados_so.get('uso_disco', 0), 100)}%"></div>
                        </div>
                        <p style="font-size: 12px; margin-top: 5px;">{dados_so.get('disco_usado_gb', 0):.2f} / {dados_so.get('disco_total_gb', 0):.2f} GB</p>
                    </div>

                    <div class="metric-card">
                        <h3>Latência do Disco</h3>
                        <div class="metric-value">{dados_so.get('latencia_disco_ms', 0):.2f} ms</div>
                    </div>

                    <div class="metric-card">
                        <h3>CPU Cores</h3>
                        <div class="metric-value">{dados_so.get('cpu_cores', 'N/A')}</div>
                    </div>
                </div>
            </div>

            <!-- Métricas BD -->
            <div class="section">
                <h2>🗄️ Métricas do Banco de Dados</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Status</h3>
                        <div class="metric-value" style="font-size: 18px;">{dados_db.get('status', '--')}</div>
                    </div>

                    <div class="metric-card">
                        <h3>Versão</h3>
                        <div class="metric-value" style="font-size: 18px;">{dados_db.get('versao', '--')}</div>
                    </div>

                    <div class="metric-card">
                        <h3>Conexões Ativas</h3>
                        <div class="metric-value">{dados_db.get('conexoes_ativas', 0)}</div>
                    </div>

                    <div class="metric-card">
                        <h3>Tempo de Resposta</h3>
                        <div class="metric-value">{dados_db.get('tempo_resposta', 0)} ms</div>
                    </div>

                    <div class="metric-card">
                        <h3>Tabelas</h3>
                        <div class="metric-value">{dados_db.get('tabelas', 0)}</div>
                    </div>

                    <div class="metric-card">
                        <h3>Tamanho</h3>
                        <div class="metric-value" style="font-size: 18px;">{dados_db.get('tamanho_db', '0 MB')}</div>
                    </div>
                </div>
            </div>

            <!-- Queries Lentas -->
            <div class="section">
                <h2>⚠️ Consultas Lentas Detectadas</h2>
                {_gerar_tabela_queries_html(dados_db.get('queries_lentas', []))}
            </div>

            <!-- Alertas -->
            <div class="section">
                <h2>🔔 Alertas</h2>
                {''.join([f'<div class="alert-item{"critico" if "🔴" in alert else ""}">{alert}</div>'
                         for alert in analise.get('alertas', [])])}
            </div>

            <!-- Recomendações -->
            <div class="section">
                <h2>💡 Recomendações</h2>
                {''.join([f'<div class="recommendation-item">✓ {rec}</div>'
                         for rec in analise.get('recomendacoes', [])])}
            </div>
        </div>

        <div class="footer">
            <p>Sistema Operacional: {_get_info_sistema()}</p>
            <p>© {datetime.now().year} - Relatório de Diagnóstico de Desempenho</p>
        </div>
    </div>
</body>
</html>"""

        return html
    except Exception as e:
        raise Exception(f"Erro ao formatar relatório HTML: {str(e)}")


def _gerar_tabela_queries_html(queries_lentas: list) -> str:
    """Gera tabela HTML com queries lentas"""
    if not queries_lentas:
        return '<p style="color: #666;">Nenhuma query lenta detectada</p>'

    html = '<table class="queries-table"><thead><tr>'
    html += '<th>Tempo (s)</th><th>Usuário</th><th>Banco</th><th>Comando</th><th>Estado</th><th>Query</th>'
    html += '</tr></thead><tbody>'

    for query in queries_lentas:
        if isinstance(query, dict):
            html += f'<tr>'
            html += f'<td><strong>{query.get("tempo_segundos", 0)}s</strong></td>'
            html += f'<td>{query.get("usuario", "N/A")}</td>'
            html += f'<td>{query.get("banco", "N/A")}</td>'
            html += f'<td>{query.get("comando", "N/A")}</td>'
            html += f'<td>{query.get("estado", "N/A")}</td>'
            html += f'<td style="font-size: 12px; color: #666;">{query.get("query", "N/A")}</td>'
            html += '</tr>'

    html += '</tbody></table>'
    return html


def _formatar_uptime(segundos: int) -> str:
    """Formata uptime em formato legível"""
    dias = segundos // 86400
    horas = (segundos % 86400) // 3600
    minutos = (segundos % 3600) // 60
    return f"{dias}d {horas}h {minutos}m"


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


def gerar_relatorio_html_arquivo(analise: Dict[str, Any]) -> str:
    """
    Gera e salva um relatório em formato HTML

    Args:
        analise: Dicionário com os dados da análise

    Returns:
        Nome do arquivo gerado
    """
    try:
        nome_arquivo = f"relatorio_diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        relatorio_html = formatar_relatorio_html(analise)

        with open(nome_arquivo, 'w', encoding='utf-8') as relatorio:
            relatorio.write(relatorio_html)

        print(f"✅ Relatório HTML gerado com sucesso: {nome_arquivo}")
        return nome_arquivo

    except Exception as e:
        raise Exception(f"Erro ao gerar relatório HTML: {str(e)}")


def _get_info_sistema() -> str:
    try:
        import platform
        sistema = platform.system()
        versao = platform.release()
        processador = platform.processor()
        return f"{sistema} {versao} ({processador})"
    except:
        return "Sistema desconhecido"