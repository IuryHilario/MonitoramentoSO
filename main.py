import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import threading

from src.so_metricas import coletar_metricas_so
from src.db_metricas import coletar_metricas_db
from src.analisar import analisar_dados
from src.relatorio import formatar_relatorio, gerar_relatorio_arquivo

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
        self.master.geometry("900x750")
        self.master.resizable(False, False)
        self.master.config(bg=self.CORES['fundo'])

        self.ultima_analise = None

        self._criar_header()

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(padx=0, pady=0, fill="both", expand=True)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', font=("Segoe UI", 10))

        self.aba_metricas = tk.Frame(self.notebook, bg=self.CORES['fundo'])
        self.notebook.add(self.aba_metricas, text="📊 Métricas")
        self._criar_aba_metricas()

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

        # Status label
        self.status_label = tk.Label(
            self.master,
            text="🟢 Aguardando execução...",
            fg=self.CORES['texto_claro'],
            bg=self.CORES['fundo'],
            font=("Segoe UI", 10)
        )
        self.status_label.pack(pady=5)

        # Footer
        footer_frame = tk.Frame(self.master, bg="#e8e8e8", height=40)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)

    def executar_diagnostico(self):
        thread = threading.Thread(target=self._executar_diagnostico_thread, daemon=True)
        thread.start()

    def _executar_diagnostico_thread(self):
        try:
            # Desabilitar botão durante execução
            self.btn_executar.config(state="disabled")
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

            dados_db = coletar_metricas_db()
            analise = analisar_dados(dados_so, dados_db)

            self.ultima_analise = analise

            relatorio_formatado = formatar_relatorio(analise)
            self._atualizar_relatorio(relatorio_formatado)

            self.status_label.config(text="✅ Diagnóstico concluído com sucesso!", fg=self.CORES['sucesso'])

            self.notebook.select(1)

            messagebox.showinfo("✅ Sucesso", "Diagnóstico executado com sucesso!\n\nO relatório está disponível na aba 'Relatório'.")

        except Exception as e:
            messagebox.showerror("❌ Erro", f"Ocorreu um erro durante a execução:\n\n{str(e)}")
            self.status_label.config(text="❌ Falha na execução.", fg=self.CORES['erro'])

        finally:
            self.btn_executar.config(state="normal")
            if self.ultima_analise is not None:
                self.btn_salvar.config(state="normal")

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
