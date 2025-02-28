import sqlite3
from tkinter import *
from tkinter import ttk, messagebox

# ---------------------- Banco de Dados ----------------------

# ---------------------- Funções ----------------------
def cadastrar_paciente():
    nome = nome_entry.get()
    data_nascimento = nascimento_entry.get()
    cpf = cpf_entry.get()
    cartao_sus = sus_entry.get()
    telefone = telefone_entry.get()
    email = email_entry.get()
    
    if nome == "" or cartao_sus == "":
        messagebox.showerror("Erro", "Nome e Cartão do SUS são obrigatórios!")
        return
    
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    
    cursor.execute("""INSERT INTO paciente (nome, data_nascimento, cpf, cartao_sus, telefone, email) 
                      VALUES (?, ?, ?, ?, ?, ?)""", (nome, data_nascimento, cpf, cartao_sus, telefone, email))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")
    listar_pacientes()

def listar_pacientes():
    for item in tree.get_children():
        tree.delete(item)
    
    conn = sqlite3.connect("medidor.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cartao_sus FROM paciente")
    pacientes = cursor.fetchall()
    conn.close()
    
    for paciente in pacientes:
        tree.insert("", "end", values=paciente)

# ---------------------- Interface Tkinter ----------------------
root = Tk()
root.title("Sistema de Monitoramento de Pacientes")
root.geometry("800x500")

# Frame superior (título)
frame_top = Frame(root, height=100, bg="#329542")
frame_top.pack(fill=X)

Label(frame_top, text="Cadastro de Pacientes", font=("Arial", 18), bg="#329542", fg="white").pack(pady=20)

# Frame principal (campos de entrada e tabela)
frame_main = Frame(root)
frame_main.pack(fill=BOTH, expand=True, padx=20, pady=10)

# Frame para os campos de entrada
frame_inputs = Frame(frame_main)
frame_inputs.grid(row=0, column=0, sticky="nsew", pady=10)

# Campos de entrada
Label(frame_inputs, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
nome_entry = Entry(frame_inputs, width=40)
nome_entry.grid(row=0, column=1, padx=5, pady=5)

Label(frame_inputs, text="Data de Nascimento:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
nascimento_entry = Entry(frame_inputs, width=40)
nascimento_entry.grid(row=1, column=1, padx=5, pady=5)

Label(frame_inputs, text="CPF:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
cpf_entry = Entry(frame_inputs, width=40)
cpf_entry.grid(row=2, column=1, padx=5, pady=5)

Label(frame_inputs, text="Cartão SUS:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
sus_entry = Entry(frame_inputs, width=40)
sus_entry.grid(row=3, column=1, padx=5, pady=5)

Label(frame_inputs, text="Telefone:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
telefone_entry = Entry(frame_inputs, width=40)
telefone_entry.grid(row=4, column=1, padx=5, pady=5)

Label(frame_inputs, text="E-mail:").grid(row=5, column=0, padx=5, pady=5, sticky=W)
email_entry = Entry(frame_inputs, width=40)
email_entry.grid(row=5, column=1, padx=5, pady=5)

Button(frame_inputs, text="Cadastrar", command=cadastrar_paciente, bg="#329542", fg="white").grid(row=6, columnspan=2, pady=10)

# Frame para a tabela
frame_tabela = Frame(frame_main)
frame_tabela.grid(row=1, column=0, sticky="nsew", pady=10)

# Adicionando barras de rolagem
scrollbar_y = Scrollbar(frame_tabela, orient=VERTICAL)
scrollbar_x = Scrollbar(frame_tabela, orient=HORIZONTAL)

# Tabela de pacientes
columns = ("ID", "Nome", "Cartão SUS")
tree = ttk.Treeview(frame_tabela, columns=columns, show="headings", yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
tree.grid(row=0, column=0, sticky="nsew")

scrollbar_y.config(command=tree.yview)
scrollbar_x.config(command=tree.xview)

scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x.grid(row=1, column=0, sticky="ew")

# Configurando as colunas da tabela
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor=CENTER)

# Configurando o grid para expandir a tabela
frame_main.grid_rowconfigure(1, weight=1)
frame_main.grid_columnconfigure(0, weight=1)

listar_pacientes()
root.mainloop()