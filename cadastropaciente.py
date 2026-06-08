import database
import sys
from tkinter import *
from tkinter import ttk, messagebox

class CadastroPacienteWindow:
    def __init__(self, master, callback_on_success=None):
        self.master = master
        self.callback_on_success = callback_on_success
        
        # Cria a janela Toplevel vinculada ao master
        self.window = Toplevel(master)
        self.window.title("Sistema de Monitoramento de Pacientes")
        self.window.geometry("800x500")
        
        # Frame superior (título)
        self.frame_top = Frame(self.window, height=100, bg="#329542")
        self.frame_top.pack(fill=X)
        
        Label(self.frame_top, text="Cadastro de Pacientes", font=("Arial", 18), bg="#329542", fg="white").pack(pady=20)
        
        # Frame principal (campos de entrada e tabela)
        self.frame_main = Frame(self.window)
        self.frame_main.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # Frame para os campos de entrada
        self.frame_inputs = Frame(self.frame_main)
        self.frame_inputs.grid(row=0, column=0, sticky="nsew", pady=10)
        
        # Campos de entrada
        Label(self.frame_inputs, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.nome_entry = Entry(self.frame_inputs, width=40)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(self.frame_inputs, text="Data de Nascimento:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        self.nascimento_entry = Entry(self.frame_inputs, width=40)
        self.nascimento_entry.grid(row=1, column=1, padx=5, pady=5)
        
        Label(self.frame_inputs, text="CPF:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.cpf_entry = Entry(self.frame_inputs, width=40)
        self.cpf_entry.grid(row=2, column=1, padx=5, pady=5)
        
        Label(self.frame_inputs, text="Cartão SUS:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.sus_entry = Entry(self.frame_inputs, width=40)
        self.sus_entry.grid(row=3, column=1, padx=5, pady=5)
        
        Label(self.frame_inputs, text="Telefone:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.telefone_entry = Entry(self.frame_inputs, width=40)
        self.telefone_entry.grid(row=4, column=1, padx=5, pady=5)
        
        Label(self.frame_inputs, text="E-mail:").grid(row=5, column=0, padx=5, pady=5, sticky=W)
        self.email_entry = Entry(self.frame_inputs, width=40)
        self.email_entry.grid(row=5, column=1, padx=5, pady=5)
        
        Button(self.frame_inputs, text="Cadastrar", command=self.cadastrar_paciente, bg="#329542", fg="white").grid(row=6, columnspan=2, pady=10)
        
        # Frame para a tabela
        self.frame_tabela = Frame(self.frame_main)
        self.frame_tabela.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Adicionando barras de rolagem
        self.scrollbar_y = Scrollbar(self.frame_tabela, orient=VERTICAL)
        self.scrollbar_x = Scrollbar(self.frame_tabela, orient=HORIZONTAL)
        
        # Tabela de pacientes
        self.columns = ("ID", "Nome", "Cartão SUS")
        self.tree = ttk.Treeview(self.frame_tabela, columns=self.columns, show="headings", yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar_y.config(command=self.tree.yview)
        self.scrollbar_x.config(command=self.tree.xview)
        
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Configurando as colunas da tabela
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=CENTER)
        
        # Configurando o grid para expandir a tabela
        self.frame_main.grid_rowconfigure(1, weight=1)
        self.frame_main.grid_columnconfigure(0, weight=1)
        
        self.listar_pacientes()

    def cadastrar_paciente(self):
        nome = self.nome_entry.get()
        data_nascimento = self.nascimento_entry.get()
        cpf = self.cpf_entry.get()
        cartao_sus = self.sus_entry.get()
        telefone = self.telefone_entry.get()
        email = self.email_entry.get()
        
        if nome == "" or cartao_sus == "":
            messagebox.showerror("Erro", "Nome e Cartão do SUS são obrigatórios!")
            return
        
        try:
            database.cadastrar_paciente(nome, data_nascimento, cpf, cartao_sus, telefone, email)
            messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")
            self.listar_pacientes()
            
            # Limpa os campos após o cadastro
            self.nome_entry.delete(0, END)
            self.nascimento_entry.delete(0, END)
            self.cpf_entry.delete(0, END)
            self.sus_entry.delete(0, END)
            self.telefone_entry.delete(0, END)
            self.email_entry.delete(0, END)

            if self.callback_on_success:
                self.callback_on_success()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar paciente: {e}")

    def listar_pacientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            pacientes = database.listar_pacientes()
            for paciente in pacientes:
                self.tree.insert("", "end", values=paciente)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar pacientes: {e}")

if __name__ == "__main__":
    root = Tk()
    root.withdraw() # Oculta a janela root padrão para usar Toplevel
    app = CadastroPacienteWindow(root)
    # Fecha o app inteiro quando a janela for fechada no modo standalone
    app.window.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), sys.exit()))
    root.mainloop()