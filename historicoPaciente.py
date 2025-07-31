import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def historico_paciente(paciente_id):
    """Exibe o histórico de medidas de um paciente específico."""
    historico_window = Toplevel()
    historico_window.title("Histórico de Paciente")
    historico_window.geometry("1208x800")

    # Frame da Tabela
    frame_table = Frame(historico_window)
    frame_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    columns = ("data_hora", "peso", "sistolica", "diastolica", "pulsacao", "temperatura")
    tree = ttk.Treeview(frame_table, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor=CENTER)

    tree.pack(fill=BOTH, expand=True)

    # Conectar ao banco
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data_hora, peso, sistolica, diastolica, pulsacao, temperatura
        FROM medida
        WHERE paciente_id=?
    """, (paciente_id,))
    medidas = cursor.fetchall()
    conn.close()

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

        try:
            if data_raw:
                try:
                    data_formatada = datetime.strptime(data_raw.strip(), "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    data_formatada = datetime.strptime(data_raw.strip(), "%Y-%m-%d %H:%M:%S")

                datas.append(data_formatada)
                pesos.append(peso)
                sistolica.append(sist)
                diastolica.append(diast)
        except Exception as e:
            print(f"[ERRO] Conversão de data falhou para '{data_raw}': {e}")

    # Função auxiliar para criar gráficos
    def criar_grafico(titulo, dados_y, label_y):
        frame_grafico = Frame(historico_window)
        frame_grafico.pack(fill=BOTH, expand=False, padx=10, pady=10)

        fig = Figure(figsize=(10, 3), dpi=100)
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
