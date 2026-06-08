import database
import sys
import re
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime

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
        Label(self.frame_inputs, text="Nome (Obrigatório):").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        self.nome_entry = Entry(self.frame_inputs, width=40)
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5)
        
        Label(self.frame_inputs, text="Data de Nascimento (DD/MM/AAAA):").grid(row=1, column=0, padx=5, pady=5, sticky=W)
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
        
        # Vincular eventos de digitação em tempo real para as máscaras
        self.nascimento_entry.bind("<KeyRelease>", self.formatar_data)
        self.cpf_entry.bind("<KeyRelease>", self.formatar_cpf)
        
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

    def formatar_data(self, event):
        # Ignora teclas de navegação/controle
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Shift_L", "Shift_R"):
            return
        text = self.nascimento_entry.get()
        digits = "".join([c for c in text if c.isdigit()])[:8]
        
        formatted = ""
        for i, d in enumerate(digits):
            if i == 2 or i == 4:
                formatted += "/"
            formatted += d
            
        self.nascimento_entry.delete(0, END)
        self.nascimento_entry.insert(0, formatted)

    def formatar_cpf(self, event):
        # Ignora teclas de navegação/controle
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Shift_L", "Shift_R"):
            return
        text = self.cpf_entry.get()
        digits = "".join([c for c in text if c.isdigit()])[:11]
        
        formatted = ""
        for i, d in enumerate(digits):
            if i == 3 or i == 6:
                formatted += "."
            elif i == 9:
                formatted += "-"
            formatted += d
            
        self.cpf_entry.delete(0, END)
        self.cpf_entry.insert(0, formatted)

    def validar_cpf(self, cpf_str):
        # Remove pontos e traços
        cpf = "".join([c for c in cpf_str if c.isdigit()])
        if len(cpf) != 11:
            return False
        # CPFs com todos os dígitos iguais são inválidos
        if cpf == cpf[0] * 11:
            return False
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[9]):
            return False
        # Calcula segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = (soma * 10) % 11
        if resto == 10:
            resto = 0
        if resto != int(cpf[10]):
            return False
        return True

    def cadastrar_paciente(self):
        nome = self.nome_entry.get().strip()
        data_nascimento = self.nascimento_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        cartao_sus = self.sus_entry.get().strip()
        telefone = self.telefone_entry.get().strip()
        email = self.email_entry.get().strip()
        
        # Apenas o Nome é obrigatório agora
        if nome == "":
            messagebox.showerror("Erro de Validação", "O campo Nome é obrigatório!")
            return
        
        # Validação semântica de Data de Nascimento (Formato DD/MM/AAAA)
        if data_nascimento:
            try:
                dt = datetime.strptime(data_nascimento, "%d/%m/%Y")
                ano_atual = datetime.now().year
                if dt.year < 1900 or dt.year > ano_atual:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro de Validação", "Data de Nascimento inválida! Use o formato DD/MM/AAAA com valores reais entre 1900 e o ano atual.")
                return
        else:
            messagebox.showerror("Erro de Validação", "O campo Data de Nascimento é obrigatório!")
            return

        # Validação de CPF se preenchido
        if cpf:
            if not self.validar_cpf(cpf):
                messagebox.showerror("Erro de Validação", "O CPF informado é inválido!")
                return
                
        # Validação de E-mail se preenchido
        if email:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                messagebox.showerror("Erro de Validação", "O E-mail informado possui formato inválido!")
                return
        
        try:
            # Cadastra o paciente (o módulo database já converte strings vazias em None)
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
                # Exibe "N/A" na tabela para o Cartão SUS caso seja None ou vazio
                sus_display = paciente[2] if paciente[2] else "N/A"
                self.tree.insert("", "end", values=(paciente[0], paciente[1], sus_display))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar pacientes: {e}")

if __name__ == "__main__":
    root = Tk()
    root.withdraw() # Oculta a janela root padrão para usar Toplevel
    app = CadastroPacienteWindow(root)
    app.window.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), sys.exit()))
    root.mainloop()