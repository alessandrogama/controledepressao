import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime

# ---------------------- Funções ----------------------
def registrar_medida():
    """Registra uma nova medida no banco de dados."""
    paciente_id = paciente_id_entry.get().strip()
    nome_paciente = nome_paciente_entry.get().strip()
    pressao = pressao_entry.get().strip()
    batimentos = batimentos_entry.get().strip()
    temperatura = temperatura_entry.get().strip()
    observacao = observacao_entry.get("1.0", END).strip()

    if not paciente_id or not pressao or not batimentos or not temperatura:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios, exceto Observação.")
        return

    try:
        conn = sqlite3.connect("medidor.sqlite")
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO medida (paciente_id, pressao, batimentos, temperatura, data_hora, observacao)
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       (paciente_id, pressao, batimentos, temperatura, datetime.now(), observacao))

        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Medida registrada com sucesso!")
        limpar_campos()
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar no banco de dados: {e}")

def limpar_campos():
    """Limpa os campos de entrada."""
    pressao_entry.delete(0, END)
    batimentos_entry.delete(0, END)
    temperatura_entry.delete(0, END)
    observacao_entry.delete("1.0", END)

# ---------------------- Interface Tkinter ----------------------
def abrir_tela_registro(paciente_id, nome_paciente):
    """Abre a tela de registro de medidas com os dados do paciente."""
    root = Tk()
    root.title("Registro de Medidas")
    root.geometry("500x550")
    root.resizable(False, False)

    # Imagem de fundo
    bg_image = Image.open("icon/logo.png")  # Substitua pelo caminho correto da sua imagem
    bg_image = bg_image.resize((500, 550), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)

    # Frame principal
    frame = Frame(root, bg="white", bd=2, relief="ridge")
    frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=400, height=450)

    # Título
    Label(frame, text="Registro de Medidas", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

    # Campos de entrada
    Label(frame, text="ID do Paciente:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    paciente_id_entry = Entry(frame, font=("Arial", 12))
    paciente_id_entry.pack(fill=X, padx=20, pady=2)
    paciente_id_entry.insert(0, paciente_id)  # Preenche o ID do paciente
    paciente_id_entry.config(state="readonly")  # Torna o campo somente leitura

    Label(frame, text="Nome do Paciente:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    nome_paciente_entry = Entry(frame, font=("Arial", 12))
    nome_paciente_entry.pack(fill=X, padx=20, pady=2)
    nome_paciente_entry.insert(0, nome_paciente)  # Preenche o nome do paciente
    nome_paciente_entry.config(state="readonly")  # Torna o campo somente leitura

    Label(frame, text="Pressão Arterial:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    pressao_entry = Entry(frame, font=("Arial", 12))
    pressao_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Batimentos Cardíacos:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    batimentos_entry = Entry(frame, font=("Arial", 12))
    batimentos_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Temperatura (°C):", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    temperatura_entry = Entry(frame, font=("Arial", 12))
    temperatura_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Observação:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    observacao_entry = Text(frame, font=("Arial", 12), height=3)
    observacao_entry.pack(fill=X, padx=20, pady=2)

    # Botões
    btn_frame = Frame(frame, bg="white")
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Registrar", command=registrar_medida, bg="#329542", fg="white", font=("Arial", 12), width=12).pack(side=LEFT, padx=5)
    Button(btn_frame, text="Limpar", command=limpar_campos, bg="#B22222", fg="white", font=("Arial", 12), width=12).pack(side=LEFT, padx=5)

    root.mainloop()

# # Exemplo de uso (para testar diretamente o medidor.py)
# if __name__ == "__main__":
#     abrir_tela_registro("1", "João Silva")