import sqlite3
import sys 
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import os # Necessário para o log de erro e caminho


# ---------------------- Funções ----------------------

def registrar_medida(paciente_id, nome_paciente, pressao_sistolica, pressao_diastolica, batimentos, temperatura, peso, observacao):
    """Registra uma nova medida no banco de dados."""
    # Validação de campos
    if not pressao_sistolica or not pressao_diastolica or not batimentos or not temperatura:
        messagebox.showerror("Erro", "Campos de Pressão, Batimentos e Temperatura são obrigatórios.")
        return

    try:

        pressao_sistolica_val = float(pressao_sistolica)
        pressao_diastolica_val = float(pressao_diastolica)
        batimentos_val = int(batimentos)
        temperatura_val = float(temperatura)
        peso_val = float(peso) if peso else None 
        sistolica = None
        diastolica = None
        if '/' in pressao_sistolica:
            try:
                sistolica, diastolica = map(int, pressao_sistolica.split('/'))
            except ValueError:
                messagebox.showerror("Erro", "Formato de Pressão Arterial inválido. Use 'XXX/YYY'.")
                return
        else: 
            sistolica = int(pressao_sistolica_val)
            diastolica = int(pressao_diastolica_val)


        conn = sqlite3.connect("medidor.sqlite")
        cursor = conn.cursor()

        cursor.execute("""INSERT INTO medida (paciente_id, data_hora, peso, sistolica, diastolica, pulsacao, temperatura)
                          VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (paciente_id, datetime.now(), peso_val, sistolica, diastolica, batimentos_val, temperatura_val))


        conn.commit()
        conn.close()

        messagebox.showinfo("Sucesso", "Medida registrada com sucesso!")
        limpar_campos() 

    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira números válidos para Pressão, Batimentos e Temperatura.")
    except sqlite3.Error as e:
        messagebox.showerror("Erro", f"Erro ao salvar no banco de dados: {e}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado ao registrar: {e}\n{traceback.format_exc()}")

        log_error(f"Erro em registrar_medida: {e}\n{traceback.format_exc()}")

pressaoSistolica_entry = None
pressaoDiastolica_entry = None
batimentos_entry = None
peso_entry = None
temperatura_entry = None
observacao_entry = None


def limpar_campos():
    """Limpa os campos de entrada."""
    # Verifica se os widgets foram inicializados antes de tentar limpá-los
    if pressaoSistolica_entry:
        pressaoSistolica_entry.delete(0, END)
    if pressaoDiastolica_entry:
        pressaoDiastolica_entry.delete(0, END)
    if batimentos_entry:
        batimentos_entry.delete(0, END)
    if temperatura_entry:
        temperatura_entry.delete(0, END)
    if observacao_entry:
        observacao_entry.delete("1.0", END)

def log_error(message):
    """Função auxiliar para logar erros em um arquivo."""
    try:
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medidor_error_log.txt")
        with open(log_file_path, "a") as f:
            f.write(f"\n--- ERRO [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---\n")
            f.write(message)
            f.write("\n" + "="*80 + "\n")
    except Exception as e:
        print(f"Erro ao tentar gravar no log de erros: {e}")


# ---------------------- Interface Tkinter ----------------------

def abrir_tela_registro(paciente_id, nome_paciente):
    """Abre a tela de registro de medidas com os dados do paciente."""
    global pressao_entry, batimentos_entry, temperatura_entry, observacao_entry 

    root = Tk()
    root.title(f"Registro de Medidas para {nome_paciente}") # Título mais informativo
    root.geometry("500x550")
    root.resizable(False, False)

    try:
        bg_image = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon", "logo.png"))
        bg_image = bg_image.resize((500, 550), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = Label(root, image=bg_photo)
        bg_label.place(relwidth=1, relheight=1)
        bg_label.image = bg_photo 
    except FileNotFoundError:
        messagebox.showwarning("Aviso", "Imagem de fundo 'logo.png' não encontrada na pasta 'icon'.")

        bg_label = Label(root, bg="lightgray") 
        bg_label.place(relwidth=1, relheight=1)
    except Exception as e:
        messagebox.showwarning("Aviso", f"Erro ao carregar imagem de fundo: {e}")
        bg_label = Label(root, bg="lightgray")
        bg_label.place(relwidth=1, relheight=1)
        log_error(f"Erro ao carregar imagem de fundo: {e}\n{traceback.format_exc()}")


    # Frame principal
    frame = Frame(root, bg="white", bd=2, relief="ridge")
    frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=400, height=550)

    # Título
    Label(frame, text="Registro de Medidas", font=("Arial", 14, "bold"), bg="white").pack(pady=10)


    # Campos de entrada
    Label(frame, text="ID do Paciente:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    paciente_id_entry = Entry(frame, font=("Arial", 12))
    paciente_id_entry.pack(fill=X, padx=20, pady=2)
    paciente_id_entry.insert(0, paciente_id)  
    paciente_id_entry.config(state="readonly")  

    Label(frame, text="Nome do Paciente:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    nome_paciente_entry = Entry(frame, font=("Arial", 12))
    nome_paciente_entry.pack(fill=X, padx=20, pady=2)
    nome_paciente_entry.insert(0, nome_paciente)  
    nome_paciente_entry.config(state="readonly")  

    Label(frame, text="Pressão Arterial Sistolica:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    pressaoSistolica_entry = Entry(frame, font=("Arial", 12))
    pressaoSistolica_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Pressão Arterial Diastolica:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    pressaoDiastolica_entry = Entry(frame, font=("Arial", 12))
    pressaoDiastolica_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Batimentos Cardíacos:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    batimentos_entry = Entry(frame, font=("Arial", 12))
    batimentos_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Peso (kg):", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    peso_entry = Entry(frame, font=("Arial", 12))
    peso_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Temperatura (°C):", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    temperatura_entry = Entry(frame, font=("Arial", 12))
    temperatura_entry.pack(fill=X, padx=20, pady=2)

    Label(frame, text="Observação:", bg="white").pack(anchor=W, padx=20, pady=(5, 0))
    observacao_entry = Text(frame, font=("Arial", 12), height=3)
    observacao_entry.pack(fill=X, padx=20, pady=2)

    # Botões
    btn_frame = Frame(frame, bg="white")
    btn_frame.pack(pady=10)

    Button(btn_frame, text="Registrar", command=lambda: registrar_medida(
        paciente_id_entry.get(), nome_paciente_entry.get(), 
        pressaoSistolica_entry.get(), pressaoDiastolica_entry.get(), batimentos_entry.get(), 
        temperatura_entry.get(), peso_entry.get(), observacao_entry.get("1.0", END).strip()
    ), bg="#329542", fg="white", font=("Arial", 12), width=12).pack(side=LEFT, padx=5)

    Button(btn_frame, text="Limpar", command=limpar_campos, bg="#B22222", fg="white", font=("Arial", 12), width=12).pack(side=LEFT, padx=5)

    root.mainloop()

import traceback 

if __name__ == "__main__":
    paciente_id_arg = None
    nome_paciente_arg = "Paciente Desconhecido" #

    try:
        if len(sys.argv) > 1:
            paciente_id_arg = sys.argv[1]
        if len(sys.argv) > 2:
            nome_paciente_arg = sys.argv[2]
        
       
        print(f"medidor.py iniciado com ID: {paciente_id_arg}, Nome: {nome_paciente_arg}")
        
       
        abrir_tela_registro(paciente_id_arg, nome_paciente_arg)

    except Exception as e:
        error_info = traceback.format_exc()
        full_error_message = f"Erro na inicialização de medidor.py:\n\nDetalhes:\n{error_info}"
        
        print(f"ERRO DE INICIALIZAÇÃO NO MEDIDOR.PY:\n{full_error_message}")
        log_error(full_error_message)


        try:
            temp_root = tk.Tk()
            temp_root.withdraw()
            messagebox.showerror("Erro de Inicialização", "Ocorreu um erro ao iniciar a tela de registro de medidas.\nVerifique o console ou o log de erros.")
            temp_root.destroy()
        except:
            pass 
        sys.exit(1)