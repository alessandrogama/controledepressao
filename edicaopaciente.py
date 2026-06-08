import database
import sys
import re
import sqlite3
import threading
from tkinter import *
from tkinter import messagebox
from datetime import datetime
import theme

class EdicaoPacienteWindow:
    """Janela modal para edição de dados cadastrais e endereço de pacientes."""

    def __init__(self, master, paciente_id, session=None, callback_on_success=None):
        self.master = master
        self.paciente_id = paciente_id
        self.session = session
        self.callback_on_success = callback_on_success

        # Fallback de sessão para modo de desenvolvimento/standalone
        if self.session is None:
            self.session = {"id": 0, "username": "dev", "role": "recepcionista"}

        # Defesa em Profundidade: Autorização no Frontend
        if self.session["role"] not in ("administrador", "recepcionista"):
            messagebox.showerror(
                "Acesso Negado",
                "Apenas administradores e recepcionistas possuem permissão para editar dados de pacientes.",
                parent=master
            )
            return

        self.window = Toplevel(master)
        self.window.title(f"Editar Paciente #{paciente_id}")
        self.window.geometry("450x660")
        self.window.resizable(False, False)
        self.window.configure(bg=theme.BG_DARK)
        theme.apply_theme(self.window)

        # Configurar modalidade (grab_set)
        self.window.grab_set()

        self._build_ui()
        self._carregar_dados()

    def _build_ui(self):
        w = self.window

        # ── Cabeçalho colorido ────────────────────────────────
        header = Frame(w, bg=theme.ACCENT, height=60)
        header.pack(fill=X)
        header.pack_propagate(False)
        Label(
            header,
            text=f"Editar Cadastro · ID #{self.paciente_id}",
            font=theme.FONT_H2,
            bg=theme.ACCENT,
            fg="#0F1923",
        ).pack(expand=True)

        # ── Corpo do formulário ───────────────────────────────
        body = Frame(w, bg=theme.BG_CARD, padx=24, pady=8)
        body.pack(fill=BOTH, expand=True, padx=12, pady=(12, 0))
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        def _add_field(label_text: str, row: int, col: int, colspan: int = 1, required: bool = False) -> Entry:
            suffix = "  *" if required else ""
            lbl = Label(
                body,
                text=f"{label_text}{suffix}",
                font=theme.FONT_LABEL,
                bg=theme.BG_CARD,
                fg=theme.TEXT_SECONDARY,
                anchor=W,
            )
            lbl.grid(
                row=row * 2, column=col, columnspan=colspan, sticky=W,
                padx=(0, 6) if col == 0 and colspan == 1 else (6, 0) if col == 1 and colspan == 1 else 0,
                pady=(5, 1)
            )

            e = Entry(
                body,
                font=theme.FONT_BODY,
                bg=theme.BG_INPUT,
                fg=theme.TEXT_PRIMARY,
                insertbackground=theme.ACCENT,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=theme.BORDER,
                highlightcolor=theme.ACCENT,
            )
            e.grid(
                row=row * 2 + 1, column=col, columnspan=colspan, sticky=EW,
                padx=(0, 6) if col == 0 and colspan == 1 else (6, 0) if col == 1 and colspan == 1 else 0,
                pady=(1, 3), ipady=5
            )
            return e

        self.nome_entry       = _add_field("Nome completo", 0, col=0, colspan=2, required=True)
        self.nascimento_entry = _add_field("Data Nasc. (DD/MM/AAAA)", 1, col=0, required=True)
        self.cpf_entry        = _add_field("CPF", 1, col=1)
        self.sus_entry        = _add_field("Cartão SUS", 2, col=0)
        self.telefone_entry   = _add_field("Telefone", 2, col=1)
        self.email_entry      = _add_field("E-mail", 3, col=0, colspan=2)
        
        # Campos de endereço
        self.cep_entry        = _add_field("CEP", 4, col=0, required=True)
        self.numero_entry     = _add_field("Número", 4, col=1, required=True)
        self.rua_entry        = _add_field("Rua (logradouro)", 5, col=0, colspan=2, required=True)
        self.bairro_entry     = _add_field("Bairro", 6, col=0, required=True)
        self.complemento_entry = _add_field("Complemento", 6, col=1)
        self.cidade_entry     = _add_field("Cidade", 7, col=0, required=True)
        self.estado_entry     = _add_field("Estado (UF)", 7, col=1, required=True)

        # Máscaras de formatação automática
        self.nascimento_entry.bind("<KeyRelease>", self.formatar_data)
        self.cpf_entry.bind("<KeyRelease>", self.formatar_cpf)
        self.cep_entry.bind("<KeyRelease>", self.formatar_cep)
        self.cep_entry.bind("<FocusOut>", self._on_cep_focus_out)

        # ── Rodapé com botões ─────────────────────────────────
        footer = Frame(w, bg=theme.BG_DARK, padx=24, pady=16)
        footer.pack(fill=X, side=BOTTOM)

        Label(
            footer,
            text="* Campos obrigatórios",
            font=theme.FONT_SMALL,
            bg=theme.BG_DARK,
            fg=theme.TEXT_SECONDARY,
        ).pack(anchor=W, pady=(0, 8))

        btn_row = Frame(footer, bg=theme.BG_DARK)
        btn_row.pack(fill=X)

        theme.HoverButton(
            btn_row,
            text="Salvar Alterações",
            style="primary",
            font=(theme.FONT_FAMILY, 10, "bold"),
            command=self.salvar_alteracoes,
        ).pack(side=LEFT, padx=(0, 10))

        theme.HoverButton(
            btn_row,
            text="Cancelar",
            style="secondary",
            font=(theme.FONT_FAMILY, 10),
            command=self.window.destroy,
        ).pack(side=LEFT)

    def _carregar_dados(self):
        """Busca as informações no banco de dados e preenche os campos."""
        try:
            paciente = database.obter_paciente_por_id(self.paciente_id)
            if not paciente:
                messagebox.showerror("Erro", "Paciente não localizado no banco de dados.", parent=self.window)
                self.window.destroy()
                return

            # Preencher dados básicos
            # paciente = (id, nome, data_nascimento, cpf, cartao_sus, telefone, email)
            self.nome_entry.insert(0, paciente[1] or "")
            self.nascimento_entry.insert(0, paciente[2] or "")
            self.cpf_entry.insert(0, paciente[3] or "")
            self.sus_entry.insert(0, paciente[4] or "")
            self.telefone_entry.insert(0, paciente[5] or "")
            self.email_entry.insert(0, paciente[6] or "")

            # Buscar e preencher endereço
            endereco = database.obter_endereco_paciente(self.paciente_id)
            if endereco:
                # endereco = (cep, rua, numero, bairro, cidade, estado, complemento)
                self.cep_entry.insert(0, endereco[0] or "")
                self.rua_entry.insert(0, endereco[1] or "")
                self.numero_entry.insert(0, endereco[2] or "")
                self.bairro_entry.insert(0, endereco[3] or "")
                self.cidade_entry.insert(0, endereco[4] or "")
                self.estado_entry.insert(0, endereco[5] or "")
                self.complemento_entry.insert(0, endereco[6] or "")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados do paciente: {e}", parent=self.window)
            self.window.destroy()

    # ──────────────────────────────────────────────────────────
    #  Máscaras de entrada
    # ──────────────────────────────────────────────────────────
    def formatar_data(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Shift_L", "Shift_R"):
            return
        digits = "".join(c for c in self.nascimento_entry.get() if c.isdigit())[:8]
        fmt = ""
        for i, d in enumerate(digits):
            if i in (2, 4):
                fmt += "/"
            fmt += d
        self.nascimento_entry.delete(0, END)
        self.nascimento_entry.insert(0, fmt)

    def formatar_cpf(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Shift_L", "Shift_R"):
            return
        digits = "".join(c for c in self.cpf_entry.get() if c.isdigit())[:11]
        fmt = ""
        for i, d in enumerate(digits):
            if i in (3, 6):
                fmt += "."
            elif i == 9:
                fmt += "-"
            fmt += d
        self.cpf_entry.delete(0, END)
        self.cpf_entry.insert(0, fmt)

    def formatar_cep(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Shift_L", "Shift_R"):
            return
        digits = "".join(c for c in self.cep_entry.get() if c.isdigit())[:8]
        fmt = ""
        for i, d in enumerate(digits):
            if i == 5:
                fmt += "-"
            fmt += d
        self.cep_entry.delete(0, END)
        self.cep_entry.insert(0, fmt)

    # ──────────────────────────────────────────────────────────
    #  Busca de CEP Automática
    # ──────────────────────────────────────────────────────────
    def _on_cep_focus_out(self, event=None):
        cep = self.cep_entry.get().strip()
        cep_limpo = "".join(c for c in cep if c.isdigit())
        if len(cep_limpo) == 8:
            threading.Thread(target=self._buscar_cep_background, args=(cep_limpo,), daemon=True).start()

    def _buscar_cep_background(self, cep):
        from services.cep_service import consultar_cep
        dados = consultar_cep(cep)
        self.window.after(0, lambda: self._atualizar_campos_endereco(dados))

    def _atualizar_campos_endereco(self, dados):
        if dados:
            self.rua_entry.delete(0, END)
            self.rua_entry.insert(0, dados.get("rua", ""))
            self.bairro_entry.delete(0, END)
            self.bairro_entry.insert(0, dados.get("bairro", ""))
            self.cidade_entry.delete(0, END)
            self.cidade_entry.insert(0, dados.get("cidade", ""))
            self.estado_entry.delete(0, END)
            self.estado_entry.insert(0, dados.get("estado", ""))
            if dados.get("complemento") and not self.complemento_entry.get().strip():
                self.complemento_entry.delete(0, END)
                self.complemento_entry.insert(0, dados.get("complemento", ""))
            self.numero_entry.focus()
        else:
            messagebox.showinfo(
                "Consulta de CEP",
                "Não foi possível consultar o CEP automaticamente. Preencha o endereço manualmente.",
                parent=self.window
            )

    # ──────────────────────────────────────────────────────────
    #  Validação de CPF
    # ──────────────────────────────────────────────────────────
    def validar_cpf(self, cpf_str: str) -> bool:
        cpf = "".join(c for c in cpf_str if c.isdigit())
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        r1 = (soma * 10) % 11
        if r1 == 10:
            r1 = 0
        if r1 != int(cpf[9]):
            return False
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        r2 = (soma * 10) % 11
        if r2 == 10:
            r2 = 0
        return r2 == int(cpf[10])

    # ──────────────────────────────────────────────────────────
    #  Ação de Salvamento
    # ──────────────────────────────────────────────────────────
    def salvar_alteracoes(self):
        nome           = self.nome_entry.get().strip()
        data_nasc      = self.nascimento_entry.get().strip()
        cpf            = self.cpf_entry.get().strip()
        cartao_sus     = self.sus_entry.get().strip()
        telefone       = self.telefone_entry.get().strip()
        email          = self.email_entry.get().strip()
        
        # Endereço
        cep            = self.cep_entry.get().strip()
        numero         = self.numero_entry.get().strip()
        rua            = self.rua_entry.get().strip()
        bairro         = self.bairro_entry.get().strip()
        complemento    = self.complemento_entry.get().strip()
        cidade         = self.cidade_entry.get().strip()
        estado         = self.estado_entry.get().strip()

        # ── Validações ────────────────────────────────────────
        if not nome:
            messagebox.showerror("Validação", "O campo Nome é obrigatório!", parent=self.window)
            self.nome_entry.focus()
            return

        if not data_nasc:
            messagebox.showerror("Validação", "O campo Data de Nascimento é obrigatório!", parent=self.window)
            return

        try:
            dt = datetime.strptime(data_nasc, "%d/%m/%Y")
            if dt.year < 1900 or dt.year > datetime.now().year:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                "Validação",
                "Data de Nascimento inválida! Use DD/MM/AAAA com valores reais entre 1900 e o ano atual.",
                parent=self.window,
            )
            return

        if cpf and not self.validar_cpf(cpf):
            messagebox.showerror("Validação", "O CPF informado é inválido!", parent=self.window)
            return

        if email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            messagebox.showerror("Validação", "O formato do E-mail é inválido!", parent=self.window)
            return

        # Validação do Endereço
        if not cep or not numero or not rua or not bairro or not cidade or not estado:
            messagebox.showerror(
                "Validação",
                "Todos os campos de endereço (CEP, Número, Rua, Bairro, Cidade e Estado) são obrigatórios!",
                parent=self.window
            )
            return

        cep_limpo = "".join(c for c in cep if c.isdigit())
        if len(cep_limpo) != 8:
            messagebox.showerror("Validação", "O CEP informado deve conter 8 dígitos!", parent=self.window)
            return

        # Defesa em Profundidade: Autorização no Backend
        if self.session["role"] not in ("administrador", "recepcionista"):
            messagebox.showerror(
                "Erro de Permissão",
                "Ação não autorizada. Seu perfil não possui permissão para editar dados de pacientes.",
                parent=self.window
            )
            raise PermissionError("Acesso não autorizado para o perfil: " + self.session["role"])

        # ── Persistência ──────────────────────────────────────
        try:
            # Atualiza paciente
            database.atualizar_paciente(
                self.paciente_id, nome, data_nasc, cpf, cartao_sus, telefone, email, self.session
            )
            
            # Atualiza/Salva endereço
            database.salvar_ou_atualizar_endereco(
                self.paciente_id, cep, rua, numero, bairro, cidade, estado, complemento, self.session
            )
            
            messagebox.showinfo("Sucesso", "Cadastro do paciente atualizado com sucesso!", parent=self.window)
            
            if self.callback_on_success:
                self.callback_on_success()
                
            self.window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Validação",
                "Já existe um paciente cadastrado com esse CPF ou Cartão SUS.",
                parent=self.window,
            )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Ocorreu um erro inesperado ao atualizar o paciente: {e}",
                parent=self.window,
            )
