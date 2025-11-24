import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import threading

from src.so_metricas import coletar_metricas_so
from src.db_metricas import coletar_metricas_db, conectar_banco
from src.analisar import analisar_dados
from src.relatorio import formatar_relatorio, gerar_relatorio_arquivo, gerar_relatorio_html_arquivo

class MonitoramentoApp:
    """Aplicação de monitoramento de desempenho do SO e Banco de Dados"""

    # Paleta de cores moderna
    CORES = {
        'primaria': '#0078D7',
        'secundaria': '#00A4EF',
        'fundo': '#f5f5f5',
        'fundo_claro': '#ffffff',
        'texto': '#1f1f1f',
        'texto_claro': '#666666',
        'sucesso': '#28a745',
        'aviso': '#ffc107',
        'erro': '#dc3545',
        'borda': '#e0e0e0'
    }

    def __init__(self, master):
        self.master = master
        self.master.title("🖥️ Monitoramento de Desempenho")
        self.master.geometry("1100x900")
        self.master.resizable(True, True)
        self.master.config(bg=self.CORES['fundo'])

        self.ultima_analise = None
        self.conexao_db = None  # Armazenar conexão ativa com banco de dados

        self._criar_header()

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(padx=0, pady=0, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=("Segoe UI", 10))

        self.aba_metricas = tk.Frame(self.notebook, bg=self.CORES['fundo'])
        self.notebook.add(self.aba_metricas, text="📊 Métricas")
        self._criar_aba_metricas()

        self.aba_banco_dados = tk.Frame(self.notebook, bg=self.CORES['fundo'])
        self.notebook.add(self.aba_banco_dados, text="🗄️ Banco de Dados")
        self._criar_aba_banco_dados()

        self.aba_relatorio = tk.Frame(self.notebook, bg=self.CORES['fundo'])
        self.notebook.add(self.aba_relatorio, text="📋 Relatório")
        self._criar_aba_relatorio()

        self._criar_footer()

    def _criar_header(self):
        header_frame = tk.Frame(self.master, bg=self.CORES['primaria'], height=90)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🖥️ Diagnóstico de Desempenho do Sistema",
            font=("Segoe UI", 20, "bold"),
            bg=self.CORES['primaria'],
            fg="white"
        )
        title_label.pack(pady=12)

        subtitle_label = tk.Label(
            header_frame,
            text="Monitore CPU, Memória, Disco e Banco de Dados em Tempo Real",
            font=("Segoe UI", 9),
            bg=self.CORES['primaria'],
            fg="#e8f4f8"
        )
        subtitle_label.pack(pady=2)

    def _criar_aba_metricas(self):
        content_frame = tk.Frame(self.aba_metricas, bg=self.CORES['fundo'])
        content_frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Caixa de informações
        descricao = (
            "Este programa analisa em tempo real:\n"
            "✓ Uso de CPU, Memória e Disco\n"
            "✓ Consultas lentas no banco de dados\n"
            "✓ Status do sistema operacional"
        )
        info_frame = tk.Frame(content_frame, bg=self.CORES['fundo_claro'], relief="flat", bd=1)
        info_frame.pack(pady=15, fill="x", padx=5)
        tk.Label(
            info_frame,
            text=descricao,
            justify="left",
            bg=self.CORES['fundo_claro'],
            font=("Segoe UI", 10),
            fg=self.CORES['texto_claro'],
            padx=15,
            pady=10
        ).pack(anchor="w", padx=10, pady=8)

        self.metrics_frame = tk.LabelFrame(
            content_frame,
            text="📊 Métricas do Sistema Operacional",
            font=("Segoe UI", 12, "bold"),
            padx=15,
            pady=15,
            bg=self.CORES['fundo_claro'],
            fg=self.CORES['primaria'],
            borderwidth=2,
            relief="flat"
        )
        self.metrics_frame.pack(padx=0, pady=10, fill="both", expand=True)

        # CPU
        cpu_subframe = tk.Frame(self.metrics_frame, bg=self.CORES['fundo_claro'])
        cpu_subframe.pack(fill="x", pady=10)
        tk.Label(cpu_subframe, text="💻 CPU:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=12, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.cpu_label = tk.Label(cpu_subframe, text="-- %", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.cpu_label.pack(side="left", padx=10)
        self.cpu_progress = tk.Label(cpu_subframe, text="", font=("Courier", 9), bg=self.CORES['fundo_claro'], fg="#666")
        self.cpu_progress.pack(side="left", padx=5)

        # Memória
        memoria_subframe = tk.Frame(self.metrics_frame, bg=self.CORES['fundo_claro'])
        memoria_subframe.pack(fill="x", pady=10)
        tk.Label(memoria_subframe, text="🧠 Memória:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=12, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.memoria_label = tk.Label(memoria_subframe, text="-- %", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.memoria_label.pack(side="left", padx=10)
        self.memoria_progress = tk.Label(memoria_subframe, text="", font=("Courier", 9), bg=self.CORES['fundo_claro'], fg="#666")
        self.memoria_progress.pack(side="left", padx=5)

        # Disco
        disco_subframe = tk.Frame(self.metrics_frame, bg=self.CORES['fundo_claro'])
        disco_subframe.pack(fill="x", pady=10)
        tk.Label(disco_subframe, text="💾 Disco:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=12, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.disco_label = tk.Label(disco_subframe, text="-- %", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.disco_label.pack(side="left", padx=10)
        self.disco_progress = tk.Label(disco_subframe, text="", font=("Courier", 9), bg=self.CORES['fundo_claro'], fg="#666")
        self.disco_progress.pack(side="left", padx=5)

        # Memória de Troca (Swap)
        swap_subframe = tk.Frame(self.metrics_frame, bg=self.CORES['fundo_claro'])
        swap_subframe.pack(fill="x", pady=10)
        tk.Label(swap_subframe, text="🔄 Swap:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=12, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.swap_label = tk.Label(swap_subframe, text="-- %", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.swap_label.pack(side="left", padx=10)
        self.swap_progress = tk.Label(swap_subframe, text="", font=("Courier", 9), bg=self.CORES['fundo_claro'], fg="#666")
        self.swap_progress.pack(side="left", padx=5)

        # Latência do Disco
        latencia_subframe = tk.Frame(self.metrics_frame, bg=self.CORES['fundo_claro'])
        latencia_subframe.pack(fill="x", pady=10)
        tk.Label(latencia_subframe, text="⚡ Latência:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=12, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.latencia_label = tk.Label(latencia_subframe, text="-- ms", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.latencia_label.pack(side="left", padx=10)

        # Botão para monitorar SO
        monitor_so_frame = tk.Frame(self.aba_metricas, bg=self.CORES['fundo'])
        monitor_so_frame.pack(fill="x", pady=10, padx=20)

        self.btn_monitorar_so = tk.Button(
            monitor_so_frame,
            text="▶️  Monitorar Sistema Operacional",
            font=("Segoe UI", 12, "bold"),
            bg=self.CORES['sucesso'],
            fg="white",
            padx=40,
            pady=12,
            command=self.monitorar_sistema_operacional,
            cursor="hand2",
            activebackground="#1e7e34",
            relief="flat",
            bd=0
        )
        self.btn_monitorar_so.pack(side="left", padx=5)

        # Botão para executar diagnóstico completo
        self.btn_diagnostico_metricas = tk.Button(
            monitor_so_frame,
            text="▶️  Executar Diagnóstico Completo",
            font=("Segoe UI", 12, "bold"),
            bg=self.CORES['primaria'],
            fg="white",
            padx=40,
            pady=12,
            command=self.executar_diagnostico,
            cursor="hand2",
            activebackground=self.CORES['secundaria'],
            relief="flat",
            bd=0
        )
        self.btn_diagnostico_metricas.pack(side="left", padx=5)

    def _criar_aba_banco_dados(self):
        content_frame = tk.Frame(self.aba_banco_dados, bg=self.CORES['fundo'])
        content_frame.pack(padx=20, pady=15, fill="both", expand=True)

        # Seção de Configuração de Conexão
        config_frame = tk.LabelFrame(
            content_frame,
            text="🔌 Configuração de Conexão",
            font=("Segoe UI", 12, "bold"),
            padx=15,
            pady=15,
            bg=self.CORES['fundo_claro'],
            fg=self.CORES['primaria'],
            borderwidth=2,
            relief="flat"
        )
        config_frame.pack(padx=0, pady=10, fill="x")

        # Campos de entrada organizados em grid
        input_frame = tk.Frame(config_frame, bg=self.CORES['fundo_claro'])
        input_frame.pack(fill="x", pady=10)

        # Host
        tk.Label(input_frame, text="Host/IP:", font=("Segoe UI", 10, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['texto']).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.entry_host = tk.Entry(input_frame, font=("Segoe UI", 10), width=30, relief="solid", bd=1)
        self.entry_host.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Usuário
        tk.Label(input_frame, text="Usuário:", font=("Segoe UI", 10, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['texto']).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.entry_usuario = tk.Entry(input_frame, font=("Segoe UI", 10), width=30, relief="solid", bd=1)
        self.entry_usuario.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Senha
        tk.Label(input_frame, text="Senha:", font=("Segoe UI", 10, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['texto']).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.entry_senha = tk.Entry(input_frame, font=("Segoe UI", 10), width=30, relief="solid", bd=1, show="•")
        self.entry_senha.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Banco de Dados
        tk.Label(input_frame, text="Banco de Dados:", font=("Segoe UI", 10, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['texto']).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.entry_banco = tk.Entry(input_frame, font=("Segoe UI", 10), width=30, relief="solid", bd=1)
        self.entry_banco.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        input_frame.grid_columnconfigure(1, weight=1)

        # Botão de Conexão
        button_frame = tk.Frame(config_frame, bg=self.CORES['fundo_claro'])
        button_frame.pack(fill="x", pady=10)

        self.btn_conectar = tk.Button(
            button_frame,
            text="🔗 Conectar ao Banco",
            font=("Segoe UI", 11, "bold"),
            bg=self.CORES['primaria'],
            fg="white",
            padx=20,
            pady=10,
            command=self.conectar_banco_dados,
            cursor="hand2",
            activebackground=self.CORES['secundaria'],
            relief="flat",
            bd=0
        )
        self.btn_conectar.pack(side="left", padx=10)

        self.btn_desconectar = tk.Button(
            button_frame,
            text="🔓 Desconectar",
            font=("Segoe UI", 11, "bold"),
            bg=self.CORES['erro'],
            fg="white",
            padx=20,
            pady=10,
            command=self.desconectar_banco_dados,
            cursor="hand2",
            activebackground="#c82333",
            relief="flat",
            bd=0,
            state="disabled"
        )
        self.btn_desconectar.pack(side="left", padx=10)

        # Status de Conexão
        self.status_conexao_label = tk.Label(
            button_frame,
            text="🔴 Desconectado",
            font=("Segoe UI", 10, "bold"),
            bg=self.CORES['fundo_claro'],
            fg=self.CORES['erro']
        )
        self.status_conexao_label.pack(side="right", padx=10)

        # Seção de Métricas do Banco de Dados
        metricas_frame = tk.LabelFrame(
            content_frame,
            text="📊 Métricas do Banco de Dados",
            font=("Segoe UI", 12, "bold"),
            padx=15,
            pady=15,
            bg=self.CORES['fundo_claro'],
            fg=self.CORES['primaria'],
            borderwidth=2,
            relief="flat"
        )
        metricas_frame.pack(padx=0, pady=10, fill="both", expand=True)

        # Métricas organizadas em grid
        metrics_grid_frame = tk.Frame(metricas_frame, bg=self.CORES['fundo_claro'])
        metrics_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Status
        status_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        status_subframe.pack(fill="x", pady=8)
        tk.Label(status_subframe, text="📡 Status:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_status_label = tk.Label(status_subframe, text="--", font=("Segoe UI", 11), bg=self.CORES['fundo_claro'], fg=self.CORES['erro'])
        self.db_status_label.pack(side="left", padx=10)

        # Versão
        versao_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        versao_subframe.pack(fill="x", pady=8)
        tk.Label(versao_subframe, text="📌 Versão MySQL:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_versao_label = tk.Label(versao_subframe, text="--", font=("Segoe UI", 11), bg=self.CORES['fundo_claro'], fg=self.CORES['texto_claro'])
        self.db_versao_label.pack(side="left", padx=10)

        # Conexões Ativas
        conexoes_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        conexoes_subframe.pack(fill="x", pady=8)
        tk.Label(conexoes_subframe, text="🔗 Conexões Ativas:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_conexoes_label = tk.Label(conexoes_subframe, text="--", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.db_conexoes_label.pack(side="left", padx=10)

        # Tempo de Resposta
        resposta_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        resposta_subframe.pack(fill="x", pady=8)
        tk.Label(resposta_subframe, text="⏱️  Tempo de Resposta:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_resposta_label = tk.Label(resposta_subframe, text="-- ms", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['sucesso'])
        self.db_resposta_label.pack(side="left", padx=10)

        # Tabelas
        tabelas_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        tabelas_subframe.pack(fill="x", pady=8)
        tk.Label(tabelas_subframe, text="📋 Tabelas:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_tabelas_label = tk.Label(tabelas_subframe, text="--", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.db_tabelas_label.pack(side="left", padx=10)

        # Tamanho do Banco
        tamanho_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        tamanho_subframe.pack(fill="x", pady=8)
        tk.Label(tamanho_subframe, text="💾 Tamanho do Banco:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_tamanho_label = tk.Label(tamanho_subframe, text="-- MB", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], fg=self.CORES['primaria'])
        self.db_tamanho_label.pack(side="left", padx=10)

        # Uptime
        uptime_subframe = tk.Frame(metrics_grid_frame, bg=self.CORES['fundo_claro'])
        uptime_subframe.pack(fill="x", pady=8)
        tk.Label(uptime_subframe, text="⏰ Uptime:", font=("Segoe UI", 11, "bold"), bg=self.CORES['fundo_claro'], width=20, anchor="w", fg=self.CORES['texto']).pack(side="left")
        self.db_uptime_label = tk.Label(uptime_subframe, text="--", font=("Segoe UI", 11), bg=self.CORES['fundo_claro'], fg=self.CORES['texto_claro'])
        self.db_uptime_label.pack(side="left", padx=10)

        # Botão para monitorar banco de dados
        monitor_button_frame = tk.Frame(content_frame, bg=self.CORES['fundo'])
        monitor_button_frame.pack(fill="x", pady=10)

        self.btn_monitorar_db = tk.Button(
            monitor_button_frame,
            text="▶️  Monitorar Banco de Dados",
            font=("Segoe UI", 12, "bold"),
            bg=self.CORES['sucesso'],
            fg="white",
            padx=40,
            pady=12,
            command=self.monitorar_banco_dados,
            cursor="hand2",
            activebackground="#1e7e34",
            relief="flat",
            bd=0,
            state="disabled"
        )
        self.btn_monitorar_db.pack(side="left", padx=5)

    def conectar_banco_dados(self):
        """Conecta ao banco de dados com as credenciais fornecidas"""
        try:
            host = self.entry_host.get().strip()
            usuario = self.entry_usuario.get().strip()
            senha = self.entry_senha.get()
            banco = self.entry_banco.get().strip()

            if not host or not usuario or not banco:
                messagebox.showwarning("⚠️ Aviso", "Por favor, preencha todos os campos obrigatórios:\n- Host/IP\n- Usuário\n- Banco de Dados")
                return

            self.status_conexao_label.config(text="⏳ Conectando...", fg=self.CORES['aviso'])
            self.master.update_idletasks()

            # Tentar conectar
            self.conexao_db = conectar_banco(host, usuario, senha, banco)

            # Se conectou com sucesso, coletar métricas iniciais
            metricas = coletar_metricas_db(self.conexao_db)
            self._atualizar_metricas_db(metricas)

            self.status_conexao_label.config(text="🟢 Conectado", fg=self.CORES['sucesso'])
            self.btn_conectar.config(state="disabled")
            self.btn_desconectar.config(state="normal")
            self.btn_monitorar_db.config(state="normal")
            self.entry_host.config(state="readonly")
            self.entry_usuario.config(state="readonly")
            self.entry_banco.config(state="readonly")

            messagebox.showinfo("✅ Sucesso", f"Conectado com sucesso ao banco de dados '{banco}'!")

        except Exception as e:
            messagebox.showerror("❌ Erro de Conexão", f"Não foi possível conectar:\n\n{str(e)}")
            self.status_conexao_label.config(text="🔴 Desconectado", fg=self.CORES['erro'])
            self.conexao_db = None

    def desconectar_banco_dados(self):
        """Desconecta do banco de dados"""
        try:
            if self.conexao_db and self.conexao_db.is_connected():
                self.conexao_db.close()
                self.conexao_db = None

            # Resetar interface
            self.status_conexao_label.config(text="🔴 Desconectado", fg=self.CORES['erro'])
            self.btn_conectar.config(state="normal")
            self.btn_desconectar.config(state="disabled")
            self.btn_monitorar_db.config(state="disabled")
            self.entry_host.config(state="normal")
            self.entry_usuario.config(state="normal")
            self.entry_banco.config(state="normal")

            # Limpar rótulos de métricas
            self.db_status_label.config(text="--", fg=self.CORES['erro'])
            self.db_versao_label.config(text="--")
            self.db_conexoes_label.config(text="--")
            self.db_resposta_label.config(text="-- ms")
            self.db_tabelas_label.config(text="--")
            self.db_tamanho_label.config(text="-- MB")
            self.db_uptime_label.config(text="--")

            messagebox.showinfo("✅ Desconectado", "Desconectado com sucesso do banco de dados.")

        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao desconectar:\n\n{str(e)}")

    def _atualizar_metricas_db(self, metricas: dict):
        """Atualiza os rótulos com as métricas do banco de dados"""
        self.db_status_label.config(
            text=metricas.get('status', '--'),
            fg=self.CORES['sucesso'] if metricas.get('status') == 'Conectado' else self.CORES['erro']
        )
        self.db_versao_label.config(text=metricas.get('versao', '--'))
        self.db_conexoes_label.config(text=str(metricas.get('conexoes_ativas', '--')))
        self.db_resposta_label.config(text=f"{metricas.get('tempo_resposta', '--')} ms")
        self.db_tabelas_label.config(text=str(metricas.get('tabelas', '--')))
        self.db_tamanho_label.config(text=metricas.get('tamanho_db', '-- MB'))

        # Formatar uptime
        uptime_segundos = metricas.get('uptime', 0)
        dias = uptime_segundos // 86400
        horas = (uptime_segundos % 86400) // 3600
        minutos = (uptime_segundos % 3600) // 60
        uptime_formatado = f"{dias}d {horas}h {minutos}m"
        self.db_uptime_label.config(text=uptime_formatado)

    def monitorar_sistema_operacional(self):
        """Monitora as métricas do SO em thread separada"""
        thread = threading.Thread(target=self._monitorar_sistema_operacional_thread, daemon=True)
        thread.start()

    def _monitorar_sistema_operacional_thread(self):
        """Thread para monitorar sistema operacional"""
        try:
            self.btn_monitorar_so.config(state="disabled")
            self.status_label.config(text="⏳ Monitorando SO...", fg=self.CORES['primaria'])
            self.master.update_idletasks()

            # Coletar métricas do SO
            dados_so = coletar_metricas_so()

            # Atualizar labels com as métricas e barras visuais
            cpu_val = dados_so['uso_cpu']
            self.cpu_label.config(text=f"{cpu_val:.1f} %")
            self.cpu_progress.config(text=self._criar_barra(cpu_val), fg=self._cor_para_valor(cpu_val))

            memoria_val = dados_so['uso_memoria']
            self.memoria_label.config(text=f"{memoria_val:.1f} %")
            self.memoria_progress.config(text=self._criar_barra(memoria_val), fg=self._cor_para_valor(memoria_val))

            disco_val = dados_so['uso_disco']
            self.disco_label.config(text=f"{disco_val:.1f} %")
            self.disco_progress.config(text=self._criar_barra(disco_val), fg=self._cor_para_valor(disco_val))

            # Atualizar Swap e Latência
            swap_val = dados_so.get('uso_swap', 0)
            self.swap_label.config(text=f"{swap_val:.1f} %")
            self.swap_progress.config(text=self._criar_barra(swap_val), fg=self._cor_para_valor(swap_val))

            latencia_val = dados_so.get('latencia_disco_ms', 0)
            self.latencia_label.config(text=f"{latencia_val:.2f} ms")

            self.status_label.config(text="✅ Monitoramento do SO concluído!", fg=self.CORES['sucesso'])
            messagebox.showinfo("✅ Monitoramento Completo", "Métricas do SO atualizadas com sucesso!")

        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao monitorar SO:\n\n{str(e)}")
            self.status_label.config(text="❌ Falha no monitoramento.", fg=self.CORES['erro'])

        finally:
            self.btn_monitorar_so.config(state="normal")

    def monitorar_banco_dados(self):
        """Monitora as métricas do banco de dados em thread separada"""
        if not self.conexao_db or not self.conexao_db.is_connected():
            messagebox.showwarning("⚠️ Aviso", "Você precisa estar conectado ao banco de dados.")
            return

        thread = threading.Thread(target=self._monitorar_banco_dados_thread, daemon=True)
        thread.start()

    def _monitorar_banco_dados_thread(self):
        """Thread para monitorar banco de dados"""
        try:
            self.btn_monitorar_db.config(state="disabled")
            self.status_conexao_label.config(text="⏳ Monitorando...", fg=self.CORES['aviso'])
            self.master.update_idletasks()

            # Coletar e atualizar métricas
            metricas = coletar_metricas_db(self.conexao_db)
            self._atualizar_metricas_db(metricas)

            self.status_conexao_label.config(text="🟢 Conectado", fg=self.CORES['sucesso'])
            messagebox.showinfo("✅ Monitoramento Completo", "Métricas atualizadas com sucesso!")

        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao monitorar banco de dados:\n\n{str(e)}")
            self.status_conexao_label.config(text="🔴 Desconectado", fg=self.CORES['erro'])

        finally:
            self.btn_monitorar_db.config(state="normal")

    def _criar_aba_relatorio(self):
        # Frame com scroll
        frame_scroll = tk.Frame(self.aba_relatorio, bg=self.CORES['fundo'])
        frame_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Barra de scroll
        scrollbar = tk.Scrollbar(frame_scroll)
        scrollbar.pack(side="right", fill="y")

        # Text widget para exibir relatório
        self.relatorio_text = tk.Text(
            frame_scroll,
            bg=self.CORES['fundo_claro'],
            fg=self.CORES['texto'],
            font=("Courier", 9),
            wrap="word",
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )
        self.relatorio_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.relatorio_text.yview)

        # Mensagem inicial
        self.relatorio_text.insert("1.0", "Clique em 'Executar Diagnóstico' para gerar o relatório.\n"
                                          "\nO relatório completo será exibido aqui automaticamente "
                                          "após a análise.")
        self.relatorio_text.config(state="disabled")

    def _criar_footer(self):
        """Cria o footer com botões e status"""
        button_frame = tk.Frame(self.master, bg=self.CORES['fundo'])
        button_frame.pack(pady=10)

        self.btn_executar = tk.Button(
            button_frame,
            text="▶️  Executar Diagnóstico Completo",
            font=("Segoe UI", 12, "bold"),
            bg=self.CORES['primaria'],
            fg="white",
            padx=40,
            pady=12,
            command=self.executar_diagnostico,
            cursor="hand2",
            activebackground=self.CORES['secundaria'],
            relief="flat",
            bd=0
        )
        self.btn_executar.pack(side="left", padx=5)

        self.btn_salvar = tk.Button(
            button_frame,
            text="💾 Salvar Relatório",
            font=("Segoe UI", 12, "bold"),
            bg=self.CORES['sucesso'],
            fg="white",
            padx=30,
            pady=12,
            command=self.salvar_relatorio,
            cursor="hand2",
            activebackground="#1e7e34",
            relief="flat",
            bd=0,
            state="disabled"
        )
        self.btn_salvar.pack(side="left", padx=5)

        self.btn_salvar_html = tk.Button(
            button_frame,
            text="🌐 Salvar como HTML",
            font=("Segoe UI", 12, "bold"),
            bg="#17a2b8",
            fg="white",
            padx=30,
            pady=12,
            command=self.salvar_relatorio_html,
            cursor="hand2",
            activebackground="#138496",
            relief="flat",
            bd=0,
            state="disabled"
        )
        self.btn_salvar_html.pack(side="left", padx=5)

        # Status label
        self.status_label = tk.Label(
            self.master,
            text="🟢 Aguardando execução...",
            fg=self.CORES['texto_claro'],
            bg=self.CORES['fundo'],
            font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=5)

    def executar_diagnostico(self):
        thread = threading.Thread(target=self._executar_diagnostico_thread, daemon=True)
        thread.start()

    def _executar_diagnostico_thread(self):
        try:
            # Desabilitar botões durante execução
            self.btn_executar.config(state="disabled")
            self.btn_diagnostico_metricas.config(state="disabled")
            self.btn_salvar.config(state="disabled")

            self.status_label.config(text="⏳ Coletando métricas do SO...", fg=self.CORES['primaria'])
            self.master.update_idletasks()

            # Coletar métricas do SO
            dados_so = coletar_metricas_so()

            # Atualizar labels com as métricas e barras visuais
            cpu_val = dados_so['uso_cpu']
            self.cpu_label.config(text=f"{cpu_val:.1f} %")
            self.cpu_progress.config(text=self._criar_barra(cpu_val), fg=self._cor_para_valor(cpu_val))

            memoria_val = dados_so['uso_memoria']
            self.memoria_label.config(text=f"{memoria_val:.1f} %")
            self.memoria_progress.config(text=self._criar_barra(memoria_val), fg=self._cor_para_valor(memoria_val))

            disco_val = dados_so['uso_disco']
            self.disco_label.config(text=f"{disco_val:.1f} %")
            self.disco_progress.config(text=self._criar_barra(disco_val), fg=self._cor_para_valor(disco_val))

            self.master.update_idletasks()

            self.status_label.config(text="⏳ Coletando métricas do banco de dados...", fg=self.CORES['primaria'])
            self.master.update_idletasks()

            dados_db = coletar_metricas_db(self.conexao_db)
            analise = analisar_dados(dados_so, dados_db)

            self.ultima_analise = analise

            relatorio_formatado = formatar_relatorio(analise)
            self._atualizar_relatorio(relatorio_formatado)

            self.status_label.config(text="✅ Diagnóstico concluído com sucesso!", fg=self.CORES['sucesso'])

            self.notebook.select(2)

            messagebox.showinfo("✅ Sucesso", "Diagnóstico executado com sucesso!\n\nO relatório está disponível na aba 'Relatório'.")

        except Exception as e:
            messagebox.showerror("❌ Erro", f"Ocorreu um erro durante a execução:\n\n{str(e)}")
            self.status_label.config(text="❌ Falha na execução.", fg=self.CORES['erro'])

        finally:
            self.btn_executar.config(state="normal")
            self.btn_diagnostico_metricas.config(state="normal")
            if self.ultima_analise is not None:
                self.btn_salvar.config(state="normal")
                self.btn_salvar_html.config(state="normal")

    def _atualizar_relatorio(self, relatorio_texto: str):
        self.relatorio_text.config(state="normal")
        self.relatorio_text.delete("1.0", "end")
        self.relatorio_text.insert("1.0", relatorio_texto)
        self.relatorio_text.config(state="disabled")

    def salvar_relatorio(self):
        if self.ultima_analise is None:
            messagebox.showwarning("⚠️ Aviso", "Nenhum diagnóstico foi executado ainda.")
            return

        try:
            nome_arquivo = gerar_relatorio_arquivo(self.ultima_analise)
            messagebox.showinfo("✅ Salvo", f"Relatório salvo com sucesso!\n\n{nome_arquivo}")
        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao salvar relatório:\n\n{str(e)}")

    def salvar_relatorio_html(self):
        if self.ultima_analise is None:
            messagebox.showwarning("⚠️ Aviso", "Nenhum diagnóstico foi executado ainda.")
            return

        try:
            nome_arquivo = gerar_relatorio_html_arquivo(self.ultima_analise)
            messagebox.showinfo("✅ Salvo", f"Relatório HTML salvo com sucesso!\n\n{nome_arquivo}")
        except Exception as e:
            messagebox.showerror("❌ Erro", f"Erro ao salvar relatório HTML:\n\n{str(e)}")

    def _criar_barra(self, valor):
        barra_tamanho = 20
        preenchido = int((valor / 100) * barra_tamanho)
        barra = "█" * preenchido + "░" * (barra_tamanho - preenchido)
        return f"[{barra}]"

    def _cor_para_valor(self, valor):
        """Retorna uma cor baseada no valor do percentual"""
        if valor < 50:
            return self.CORES['sucesso']
        elif valor < 75:
            return self.CORES['aviso']
        else:
            return self.CORES['erro']


# Início da aplicação
if __name__ == "__main__":
    root = tk.Tk()

    app = MonitoramentoApp(root)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Iniciar loop principal
    root.mainloop()
