import sqlite3
import sys
import subprocess
from tkinter import *
from tkinter import ttk, messagebox

# ---------------------- Banco de Dados ----------------------
def conectar_bd():
    """Cria a tabela paciente caso não exista."""
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS paciente (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_nascimento DATE NOT NULL,
        cpf TEXT UNIQUE,
        cartao_sus TEXT UNIQUE NOT NULL,
        telefone TEXT,
        email TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS endereco (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER UNIQUE NOT NULL,
        cep TEXT NOT NULL,
        rua TEXT NOT NULL,
        numero TEXT NOT NULL,
        bairro TEXT NOT NULL,
        cidade TEXT NOT NULL,
        estado TEXT NOT NULL,
        complemento TEXT,
        FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS medida (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER NOT NULL,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        peso REAL,
        sistolica INTEGER,
        diastolica INTEGER,
        pulsacao INTEGER,
        temperatura REAL,
        FOREIGN KEY (paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()

# ---------------------- Funções ----------------------
def listar_pacientes():
    """Atualiza a tabela do dashboard com os pacientes cadastrados."""
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cartao_sus FROM paciente")
    pacientes = cursor.fetchall()
    conn.close()

    for paciente in pacientes:
        tree.insert("", "end", values=(paciente[0], paciente[1], paciente[2], "Medir", "Editar", "Historico"))

def abrir_medidor(paciente_id, nome_paciente):
    try: 
        python_path = sys.executable 

        import os
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        medidor_script_path = os.path.join(current_script_dir, "medidor.py")

        if not os.path.exists(medidor_script_path):
            messagebox.showerror("Erro", f"Arquivo 'medidor.py' não encontrado em: {medidor_script_path}")
            return

        command = [python_path, medidor_script_path, str(paciente_id), nome_paciente]
        subprocess.Popen(command)

    except FileNotFoundError:
        messagebox.showerror("Erro", "O interpretador Python ou o script 'medidor.py' não foram encontrados.")
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao tentar abrir o medidor: {e}")

def abrir_cadastro():
    try:
        subprocess.Popen(["python", "cadastropaciente.py"])
    except FileNotFoundError:
        messagebox.showerror("Erro", "Arquivo 'cadastropaciente.py' não encontrado!")
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao tentar abrir o cadastro: {e}")

def historico_paciente(paciente_id):
    """Exibe o histórico de medidas de um paciente específico."""
    try:
        import historicoPaciente
        historicoPaciente.historico_paciente(paciente_id)
    except ImportError:
        messagebox.showerror("Erro", "Arquivo 'historicoPaciente.py' não encontrado!")
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao tentar abrir o histórico: {e}")

# ---------------------- Interface Tkinter ----------------------
root = Tk()
root.title("Dashboard - Monitoramento de Pacientes")
root.geometry("1200x500")

frame_top = Frame(root, height=100, bg="#329542")
frame_top.pack(fill=X)

frame_main = Frame(root)
frame_main.pack(fill=BOTH, expand=True)

Label(frame_top, text="Dashboard de Pacientes", font=("Arial", 18), bg="#329542", fg="white").pack(pady=20)

# Botões de navegação
btn_frame = Frame(frame_main)
btn_frame.pack(pady=10)

Button(btn_frame, text="Novo Paciente", command=abrir_cadastro, bg="#329542", fg="white").pack(side=LEFT, padx=5)
Button(btn_frame, text="Atualizar Lista", command=listar_pacientes, bg="#329542", fg="white").pack(side=LEFT, padx=5)
# Tabela de pacientes
columns = ("ID", "Nome", "Cartão SUS", "Medir", "Editar","Historico")
tree = ttk.Treeview(frame_main, columns=columns, show="headings")
tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

# Função para lidar com cliques na Treeview
def on_treeview_click(event):
    """Função chamada ao clicar na Treeview."""
    region = tree.identify_region(event.x, event.y)  # Identifica a região clicada
    if region == "cell":  # Verifica se o clique foi em uma célula
        column = tree.identify_column(event.x)  # Identifica a coluna clicada
        item = tree.identify_row(event.y)  # Obtém o item clicado

        if item:  # Verifica se um item foi clicado
            if column == "#4":  # Coluna "Medir"
                paciente_id = tree.item(item, "values")[0]  # Obtém o ID do paciente
                nome_paciente = tree.item(item, "values")[1]  # Obtém o nome do paciente
                #abrir_cadastro()
                #print(f"Clicou em 'Medir' para ID: {paciente_id}, Nome: {nome_paciente}") # Para depuração
                abrir_medidor(paciente_id, nome_paciente)
            elif column == "#5":  # Coluna "Editar"
                messagebox.showinfo("Editar", "Funcionalidade de edição ainda não implementada.")
            elif column == "#6":  # Coluna "Historico"
                paciente_id = tree.item(item, "values")[0]  # Obtém o ID do paciente
                historico_paciente(paciente_id)  # Chama a função para exibir o histórico do paciente

# Vincula o evento de clique à Treeview
tree.bind("<Button-1>", on_treeview_click)

# Inicializa o banco de dados e carrega a tabela
conectar_bd()
listar_pacientes()

root.mainloop()