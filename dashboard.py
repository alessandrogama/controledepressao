import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# Função para buscar dados do banco
def get_data():
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, data_hora, peso, sistolica, diastolica, pulsacao FROM medida")
    data = cursor.fetchall()
    conn.close()
    return data

# Função para buscar nomes de pacientes
def get_patient_names():
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT nome FROM medida")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

# Função para calcular médias
def calculate_averages(df):
    df['Data/Hora'] = pd.to_datetime(df['Data/Hora'])
    df.set_index('Data/Hora', inplace=True)

    # Média por dia
    daily_avg = df.resample('D').mean()

    # Limpar NaNs
    daily_avg = daily_avg.fillna(method='ffill')  # Preencher NaNs se necessário
    
    return daily_avg

# Função para exibir gráficos de todos os pacientes
def show_all_patients_graphs():
    data = get_data()
    if not data:
        messagebox.showwarning("Aviso", "Nenhuma medida encontrada.")
        return
    
    df = pd.DataFrame(data, columns=["Nome", "Data/Hora", "Peso", "Sistólica", "Diastólica", "Pulsação"])
    
    daily_avg = calculate_averages(df)

    # Criar uma nova janela para os gráficos
    graph_window = tk.Toplevel(root)
    graph_window.title("Gráficos de Evolução - Todos os Pacientes")

    # Criar figuras para os gráficos
    fig, axes = plt.subplots(3, 1, figsize=(6, 8))

    # Plotar médias
    daily_avg["Peso"].plot(ax=axes[0], marker="o", linestyle="-", label="Peso")
    axes[0].set_title("Média Diária do Peso")
    axes[0].legend()
    
    daily_avg[["Sistólica", "Diastólica"]].plot(ax=axes[1], marker="o", linestyle="-")
    axes[1].set_title("Média Diária da Pressão Arterial")
    axes[1].legend(["Sistólica", "Diastólica"])
    
    daily_avg["Pulsação"].plot(ax=axes[2], marker="o", linestyle="-", label="Pulsação")
    axes[2].set_title("Média Diária da Pulsação")
    axes[2].legend()

    plt.tight_layout()

    # Exibir os gráficos na interface Tkinter
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Função para exibir gráficos de um paciente específico
def show_patient_graphs(selected_patient):
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT data_hora, peso, sistolica, diastolica, pulsacao FROM medida WHERE nome = ?", (selected_patient,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showwarning("Aviso", "Nenhuma medida encontrada para o paciente selecionado.")
        return
    
    df = pd.DataFrame(data, columns=["Data/Hora", "Peso", "Sistólica", "Diastólica", "Pulsação"])
    
    daily_avg = calculate_averages(df)

    # Criar uma nova janela para os gráficos do paciente
    graph_window = tk.Toplevel(root)
    graph_window.title(f"Gráficos de Evolução - {selected_patient}")

    # Criar figuras para os gráficos
    fig, axes = plt.subplots(3, 1, figsize=(6, 8))

    daily_avg["Peso"].plot(ax=axes[0], marker="o", linestyle="-", label="Peso")
    axes[0].set_title("Média Diária do Peso")
    axes[0].legend()
    
    daily_avg[["Sistólica", "Diastólica"]].plot(ax=axes[1], marker="o", linestyle="-")
    axes[1].set_title("Média Diária da Pressão Arterial")
    axes[1].legend(["Sistólica", "Diastólica"])
    
    daily_avg["Pulsação"].plot(ax=axes[2], marker="o", linestyle="-", label="Pulsação")
    axes[2].set_title("Média Diária da Pulsação")
    axes[2].legend()

    plt.tight_layout()

    # Exibir os gráficos na interface Tkinter
    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Função para atualizar o gráfico ao selecionar um paciente
def on_patient_select(event):
    selected_patient = patient_combo.get()
    show_patient_graphs(selected_patient)

# Criando a interface principal
root = tk.Tk()
root.title("Dashboard de Medidas")
root.geometry("500x400")

# Botão para visualizar gráficos de todos os pacientes
btn_graficos = ttk.Button(root, text="Exibir Gráficos de Todos os Pacientes", command=show_all_patients_graphs)
btn_graficos.pack(pady=10)

# Dropdown para selecionar paciente
patient_names = get_patient_names()
patient_combo = ttk.Combobox(root, values=patient_names, state="readonly")
patient_combo.pack(pady=10)
patient_combo.bind("<<ComboboxSelected>>", on_patient_select)

# Botão de saída
btn_sair = ttk.Button(root, text="Sair", command=root.quit)
btn_sair.pack(pady=10)

root.mainloop()
