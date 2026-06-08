import sys
from tkinter import *
from tkinter import ttk, messagebox
import database
from cadastropaciente import CadastroPacienteWindow
from medidor import RegistroMedidasWindow

# ---------------------- Banco de Dados ----------------------
def conectar_bd():
    """Cria a tabela paciente caso não exista."""
    database.inicializar_banco()

# ---------------------- Funções ----------------------
def listar_pacientes():
    """Atualiza a tabela do dashboard com os pacientes cadastrados."""
    for item in tree.get_children():
        tree.delete(item)

    pacientes = database.listar_pacientes()

    for paciente in pacientes:
        tree.insert("", "end", values=(paciente[0], paciente[1], paciente[2], "Medir", "Editar", "Historico"))

def abrir_medidor(paciente_id, nome_paciente):
    try: 
        RegistroMedidasWindow(root, paciente_id, nome_paciente)
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao tentar abrir o medidor: {e}")

def abrir_cadastro():
    try:
        CadastroPacienteWindow(root, callback_on_success=listar_pacientes)
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

if __name__ == "__main__":
    # Inicializa o banco de dados e carrega a tabela
    conectar_bd()
    listar_pacientes()

    root.mainloop()