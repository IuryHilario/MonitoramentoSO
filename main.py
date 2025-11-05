import tkinter as tk
from tkinter import messagebox

from src.so_metricas import coletar_metricas_so
from src.db_metricas import coletar_metricas_db
from src.analisar import analisar_dados
from src.relatorio import gerar_relatorio

class MonitoramentoApp:
    def __init__(self, master):
        self.master = master
        master.title("Monitoramento de SO e Banco de Dados")
        master.geometry("420x300")
        master.resizable(False, False)

        tk.Label(master, text="Diagnóstico de Desempenho", font=("Segoe UI", 14, "bold")).pack(pady=10)

        descricao = (
            "Este programa analisa o uso de CPU, memória, disco\n"
            "e consultas lentas no banco de dados MySQL.\n"
            "Clique abaixo para iniciar o diagnóstico."
        )
        tk.Label(master, text=descricao, justify="center").pack(pady=10)

        self.btn_executar = tk.Button(
            master, text="Executar Diagnóstico", font=("Segoe UI", 11, "bold"),
            bg="#0078D7", fg="white", padx=20, pady=5,
            command=self.executar_diagnostico
        )
        self.btn_executar.pack(pady=15)

        self.status_label = tk.Label(master, text="Aguardando execução...", fg="gray")
        self.status_label.pack(pady=5)

        tk.Label(master, text="Versão 1.0 — Projeto N2", fg="gray", font=("Segoe UI", 8)).pack(side="bottom", pady=5)

    # Função Provisória
    def executar_diagnostico(self):
        try:
            self.status_label.config(text="Executando diagnóstico...")
            self.master.update_idletasks()

            dados_so = coletar_metricas_so()
            dados_db = coletar_metricas_db()
            analise = analisar_dados(dados_so, dados_db)
            gerar_relatorio(analise)

            self.status_label.config(text="✅ Diagnóstico concluído!")
            messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!\nSalvo em 'relatorio_diagnostico.txt'")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
            self.status_label.config(text="❌ Falha na execução.")

        
# Início da aplicação
if __name__ == "__main__":
    root = tk.Tk()
    app = MonitoramentoApp(root)
    root.mainloop()
