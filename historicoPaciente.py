from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import database

def _parse_date(date_str):
    """Função otimizada para realizar o parsing de strings de data para datetime."""
    if not date_str:
        return None
    date_str = date_str.strip()
    try:
        # Tenta fatiar os milissegundos se existirem para acelerar o strptime padrão
        if "." in date_str:
            return datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Fallback rápido usando fromisoformat
        try:
            return datetime.fromisoformat(date_str)
        except Exception:
            return None

def historico_paciente(paciente_id):
    """Exibe o histórico de medidas de um paciente específico."""
    historico_window = Toplevel()
    historico_window.title("Histórico de Paciente")
    historico_window.geometry("1208x800")

    # Lista para rastrear figuras do Matplotlib criadas
    figuras = []

    # Frame da Tabela
    frame_table = Frame(historico_window)
    frame_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("data_hora", "peso", "sistolica", "diastolica", "pulsacao", "temperatura")
    tree = ttk.Treeview(frame_table, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor=CENTER)

    tree.pack(fill=BOTH, expand=True)

    # Conectar ao banco via modulo database
    try:
        medidas = database.obter_medidas_paciente(paciente_id)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao recuperar histórico: {e}")
        medidas = []

    # Preencher tabela
    for medida in medidas:
        tree.insert("", "end", values=medida)

    # Preparar dados para os gráficos
    datas = []
    pesos = []
    sistolica = []
    diastolica = []

    for medida in medidas:
        data_raw = medida[0]
        peso = medida[1]
        sist = medida[2]
        diast = medida[3]

        data_formatada = _parse_date(data_raw)
        if data_formatada:
            datas.append(data_formatada)
            pesos.append(peso)
            sistolica.append(sist)
            diastolica.append(diast)
        else:
            pass  # Data inválida: ignora o ponto sem expor dados ao console

    # Função auxiliar para criar gráficos
    def criar_grafico(titulo, dados_y, label_y):
        frame_grafico = Frame(historico_window)
        frame_grafico.pack(fill=BOTH, expand=False, padx=10, pady=10)

        fig = Figure(figsize=(10, 3), dpi=100)
        figuras.append(fig) # Rastreia a figura para liberação posterior
        
        ax = fig.add_subplot(111)
        ax.plot(datas, dados_y, marker='o', linestyle='-', color='blue')
        ax.set_title(titulo)
        ax.set_xlabel("Data")
        ax.set_ylabel(label_y)
        ax.grid(True)
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)

    # Gerar gráficos
    if datas:
        if any(pesos):
            criar_grafico("Evolução do Peso", pesos, "Peso (kg)")
        if any(sistolica):
            criar_grafico("Evolução da Pressão Sistólica", sistolica, "Sistólica (mmHg)")
        if any(diastolica):
            criar_grafico("Evolução da Pressão Diastólica", diastolica, "Diastólica (mmHg)")
    else:
        print("[INFO] Nenhum dado válido para gerar gráficos.")

    def on_close():
        """Função chamada no fechamento da janela para liberar memória do Matplotlib."""
        for fig in figuras:
            try:
                fig.clear()
            except Exception:
                pass
        historico_window.destroy()

    # Vincula o evento de fechar a janela ao método de limpeza
    historico_window.protocol("WM_DELETE_WINDOW", on_close)
