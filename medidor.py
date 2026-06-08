import sys 
import os # Necessário para o log de erro e caminho
import traceback
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import database

# Caminho absoluto resolvido no momento do import para evitar ambiguidade quando
# o módulo é importado a partir de outro diretório de trabalho.
_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medidor_error_log.txt")

def log_error(message):
    """Função auxiliar para logar erros em um arquivo. Nunca exibe detalhes internos ao usuário."""
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n--- ERRO [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---\n")
            f.write(message)
            f.write("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Erro ao tentar gravar no log de erros: {e}")

class RegistroMedidasWindow:
    def __init__(self, master, paciente_id, nome_paciente, callback_on_success=None):
        self.master = master
        self.paciente_id = paciente_id
        self.nome_paciente = nome_paciente
        self.callback_on_success = callback_on_success
        
        self.window = Toplevel(master)
        self.window.title(f"Registro de Medidas para {nome_paciente}")
        self.window.geometry("500x550")
        self.window.resizable(False, False)
        
        try:
            bg_image = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon", "logo.png"))
            bg_image = bg_image.resize((500, 550), Image.LANCZOS)
            bg_photo = ImageTk.PhotoImage(bg_image)

            bg_label = Label(self.window, image=bg_photo)
            bg_label.place(relwidth=1, relheight=1)
            bg_label.image = bg_photo 
        except FileNotFoundError:
            messagebox.showwarning("Aviso", "Imagem de fundo 'logo.png' não encontrada na pasta 'icon'.")
            bg_label = Label(self.window, bg="lightgray") 
            bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            messagebox.showwarning("Aviso", f"Erro ao carregar imagem de fundo: {e}")
            bg_label = Label(self.window, bg="lightgray")
            bg_label.place(relwidth=1, relheight=1)
            log_error(f"Erro ao carregar imagem de fundo: {e}\n{traceback.format_exc()}")
            
        # Frame principal
        self.frame = Frame(self.window, bg="white", bd=2, relief="ridge")
        self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=400, height=550)

        # Título
        Label(self.frame, text="Registro de Medidas", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        # Campos de entrada
        Label(self.frame, text="ID do Paciente:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.paciente_id_entry = Entry(self.frame, font=("Arial", 12))
        self.paciente_id_entry.pack(fill=X, padx=20, pady=2)
        self.paciente_id_entry.insert(0, paciente_id if paciente_id else "")  
        self.paciente_id_entry.config(state="readonly")  

        Label(self.frame, text="Nome do Paciente:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.nome_paciente_entry = Entry(self.frame, font=("Arial", 12))
        self.nome_paciente_entry.pack(fill=X, padx=20, pady=2)
        self.nome_paciente_entry.insert(0, nome_paciente)  
        self.nome_paciente_entry.config(state="readonly")  

        Label(self.frame, text="Pressão Arterial Sistolica:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.pressaoSistolica_entry = Entry(self.frame, font=("Arial", 12))
        self.pressaoSistolica_entry.pack(fill=X, padx=20, pady=2)

        Label(self.frame, text="Pressão Arterial Diastolica:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.pressaoDiastolica_entry = Entry(self.frame, font=("Arial", 12))
        self.pressaoDiastolica_entry.pack(fill=X, padx=20, pady=2)

        Label(self.frame, text="Batimentos Cardíacos:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.batimentos_entry = Entry(self.frame, font=("Arial", 12))
        self.batimentos_entry.pack(fill=X, padx=20, pady=2)

        Label(self.frame, text="Peso (kg):", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.peso_entry = Entry(self.frame, font=("Arial", 12))
        self.peso_entry.pack(fill=X, padx=20, pady=2)

        Label(self.frame, text="Temperatura (°C):", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.temperatura_entry = Entry(self.frame, font=("Arial", 12))
        self.temperatura_entry.pack(fill=X, padx=20, pady=2)

        Label(self.frame, text="Observação:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
        self.observacao_entry = Text(self.frame, font=("Arial", 12), height=3)
        self.observacao_entry.pack(fill=X, padx=20, pady=2)

        # Botões
        self.btn_frame = Frame(self.frame, bg="white")
        self.btn_frame.pack(pady=10)

        Button(self.btn_frame, text="Registrar", command=self.registrar_medida, bg="#329542", fg="white", font=("Arial", 12), width=12).pack(side=LEFT, padx=5)
        Button(self.btn_frame, text="Limpar", command=self.limpar_campos, bg="#B22222", fg="white", font=("Arial", 12), width=12).pack(side=LEFT, padx=5)

    def limpar_campos(self):
        """Limpa os campos de entrada."""
        self.pressaoSistolica_entry.delete(0, END)
        self.pressaoDiastolica_entry.delete(0, END)
        self.batimentos_entry.delete(0, END)
        self.peso_entry.delete(0, END)
        self.temperatura_entry.delete(0, END)
        self.observacao_entry.delete("1.0", END)

    def registrar_medida(self):
        pressao_sistolica = self.pressaoSistolica_entry.get()
        pressao_diastolica = self.pressaoDiastolica_entry.get()
        batimentos = self.batimentos_entry.get()
        temperatura = self.temperatura_entry.get()
        peso = self.peso_entry.get()
        observacao = self.observacao_entry.get("1.0", END).strip()
        
        # Validação de campos obrigatórios
        if not pressao_sistolica or not pressao_diastolica or not batimentos or not temperatura:
            messagebox.showerror("Erro", "Campos de Pressão, Batimentos e Temperatura são obrigatórios.")
            return

        try:
            # Pressão: aceita apenas inteiros positivos em cada campo separado
            sistolica = int(pressao_sistolica)
            diastolica = int(pressao_diastolica)
            if sistolica <= 0 or diastolica <= 0:
                raise ValueError("Pressão deve ser um número positivo.")

            batimentos_val = int(batimentos)
            if batimentos_val <= 0:
                raise ValueError("Batimentos devem ser um número positivo.")

            temperatura_val = float(temperatura)
            peso_val = float(peso) if peso else None

            database.registrar_medida(
                self.paciente_id, datetime.now(),
                peso_val, sistolica, diastolica, batimentos_val, temperatura_val
            )

            messagebox.showinfo("Sucesso", "Medida registrada com sucesso!")
            self.limpar_campos()

            if self.callback_on_success:
                self.callback_on_success()

            self.window.destroy()

        except ValueError as e:
            messagebox.showerror("Erro de Validação", "Por favor, insira números válidos e positivos para Pressão, Batimentos e Temperatura.")
        except Exception as e:
            # Detalhe técnico vai apenas para o log — o usuário vê uma mensagem genérica.
            log_error(f"Erro em registrar_medida: {e}\n{traceback.format_exc()}")
            messagebox.showerror("Erro", "Ocorreu um erro inesperado ao registrar a medida. Verifique o log de erros.")

if __name__ == "__main__":
    paciente_id_arg = None
    nome_paciente_arg = "Paciente Desconhecido"

    try:
        if len(sys.argv) > 1:
            paciente_id_arg = sys.argv[1]
        if len(sys.argv) > 2:
            nome_paciente_arg = sys.argv[2]
        
        print(f"medidor.py iniciado com ID: {paciente_id_arg}, Nome: {nome_paciente_arg}")
        
        root = Tk()
        root.withdraw()
        app = RegistroMedidasWindow(root, paciente_id_arg, nome_paciente_arg)
        app.window.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), sys.exit()))
        root.mainloop()

    except Exception as e:
        error_info = traceback.format_exc()
        full_error_message = f"Erro na inicialização de medidor.py:\n\nDetalhes:\n{error_info}"
        
        print(f"ERRO DE INICIALIZAÇÃO NO MEDIDOR.PY:\n{full_error_message}")
        log_error(full_error_message)

        try:
            temp_root = Tk()
            temp_root.withdraw()
            messagebox.showerror("Erro de Inicialização", "Ocorreu um erro ao iniciar a tela de registro de medidas.\nVerifique o console ou o log de erros.")
            temp_root.destroy()
        except:
            pass 
        sys.exit(1)