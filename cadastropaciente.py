import database
import sys
import re
import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import theme


class CadastroPacienteWindow:
    """Janela de cadastro de pacientes com layout em dois painéis."""

    def __init__(self, master, session=None, callback_on_success=None):
        self.master = master
        self.session = session
        self.callback_on_success = callback_on_success

        # Fallback de sessão para modo de desenvolvimento/standalone
        if self.session is None:
            self.session = {"id": 0, "username": "dev", "role": "recepcionista"}

        self.window = Toplevel(master)
        self.window.title("Cadastro de Pacientes")
        self.window.geometry("1040x620")
        self.window.minsize(820, 520)
        self.window.configure(bg=theme.BG_DARK)
        theme.apply_theme(self.window)

        self._build_layout()
        self.listar_pacientes()

    # ──────────────────────────────────────────────────────────
    #  Layout
    # ──────────────────────────────────────────────────────────
    def _build_layout(self):
        # Painel esquerdo — formulário (largura fixa)
        self.panel_form = Frame(self.window, bg=theme.BG_CARD, width=400)
        self.panel_form.pack(side=LEFT, fill=Y)
        self.panel_form.pack_propagate(False)

        # Divisor vertical
        Frame(self.window, bg=theme.BORDER, width=1).pack(side=LEFT, fill=Y)

        # Painel direito — tabela de pacientes
        self.panel_table = Frame(self.window, bg=theme.BG_DARK)
        self.panel_table.pack(side=LEFT, fill=BOTH, expand=True)

        self._build_form()
        self._build_table()

    def _build_form(self):
        p = self.panel_form

        # ── Cabeçalho colorido ────────────────────────────────
        header = Frame(p, bg=theme.ACCENT, height=64)
        header.pack(fill=X)
        header.pack_propagate(False)
        Label(
            header,
            text="Novo Paciente",
            font=theme.FONT_H2,
            bg=theme.ACCENT,
            fg="#0F1923",
        ).pack(expand=True)

        # ── Corpo do formulário ───────────────────────────────
        body = Frame(p, bg=theme.BG_CARD, padx=24, pady=8)
        body.pack(fill=BOTH, expand=True)
        body.grid_columnconfigure(0, weight=1)

        def _entry_row(label_text: str, row: int, required: bool = False) -> Entry:
            suffix = "  *" if required else ""
            Label(
                body,
                text=f"{label_text}{suffix}",
                font=theme.FONT_LABEL,
                bg=theme.BG_CARD,
                fg=theme.TEXT_SECONDARY,
                anchor=W,
            ).grid(row=row * 2, column=0, sticky=W, pady=(10, 2))

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
            e.grid(row=row * 2 + 1, column=0, sticky=EW, ipady=7)
            return e

        self.nome_entry       = _entry_row("Nome completo", 0, required=True)
        self.nascimento_entry = _entry_row("Data de Nascimento (DD/MM/AAAA)", 1, required=True)
        self.cpf_entry        = _entry_row("CPF", 2)
        self.sus_entry        = _entry_row("Cartão SUS", 3)
        self.telefone_entry   = _entry_row("Telefone", 4)
        self.email_entry      = _entry_row("E-mail", 5)

        # Máscaras de formatação automática
        self.nascimento_entry.bind("<KeyRelease>", self.formatar_data)
        self.cpf_entry.bind("<KeyRelease>", self.formatar_cpf)

        # ── Rodapé com botões ─────────────────────────────────
        Frame(p, bg=theme.BORDER, height=1).pack(fill=X, side=BOTTOM)
        footer = Frame(p, bg=theme.BG_CARD, padx=24, pady=16)
        footer.pack(fill=X, side=BOTTOM)

        Label(
            footer,
            text="* Campos obrigatórios",
            font=theme.FONT_SMALL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_SECONDARY,
        ).pack(anchor=W, pady=(0, 10))

        btn_row = Frame(footer, bg=theme.BG_CARD)
        btn_row.pack(fill=X)

        theme.HoverButton(
            btn_row,
            text="Cadastrar",
            style="primary",
            font=(theme.FONT_FAMILY, 11, "bold"),
            command=self.cadastrar_paciente,
        ).pack(side=LEFT, padx=(0, 10))

        theme.HoverButton(
            btn_row,
            text="Limpar",
            style="secondary",
            font=(theme.FONT_FAMILY, 11),
            command=self._limpar_campos,
        ).pack(side=LEFT)

    def _build_table(self):
        p = self.panel_table

        # ── Cabeçalho ─────────────────────────────────────────
        header = Frame(p, bg=theme.BG_CARD, height=64)
        header.pack(fill=X)
        header.pack_propagate(False)
        Frame(p, bg=theme.BORDER, height=1).pack(fill=X)

        Label(
            header,
            text="Pacientes Cadastrados",
            font=theme.FONT_H2,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            padx=20,
        ).pack(side=LEFT, fill=Y)

        # ── Treeview ──────────────────────────────────────────
        tree_frame = Frame(p, bg=theme.BG_DARK, padx=12, pady=12)
        tree_frame.pack(fill=BOTH, expand=True)

        cols = ("ID", "Nome", "Cartão SUS")
        self.tree = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
        )
        vsb = ttk.Scrollbar(
            tree_frame,
            orient=VERTICAL,
            command=self.tree.yview,
            style="Custom.Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=RIGHT, fill=Y)
        self.tree.pack(fill=BOTH, expand=True)

        _col_cfg = {"ID": (60, CENTER), "Nome": (260, W), "Cartão SUS": (160, CENTER)}
        for col in cols:
            w, anchor = _col_cfg[col]
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=anchor)

        self.tree.tag_configure("odd",  background=theme.ROW_ODD)
        self.tree.tag_configure("even", background=theme.ROW_EVEN)

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

    # ──────────────────────────────────────────────────────────
    #  Validação
    # ──────────────────────────────────────────────────────────
    def validar_cpf(self, cpf_str: str) -> bool:
        """Valida o CPF usando o algoritmo oficial de dígitos verificadores."""
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
    #  Ações
    # ──────────────────────────────────────────────────────────
    def _limpar_campos(self):
        for e in (
            self.nome_entry, self.nascimento_entry, self.cpf_entry,
            self.sus_entry, self.telefone_entry, self.email_entry,
        ):
            e.delete(0, END)

    def cadastrar_paciente(self):
        nome           = self.nome_entry.get().strip()
        data_nasc      = self.nascimento_entry.get().strip()
        cpf            = self.cpf_entry.get().strip()
        cartao_sus     = self.sus_entry.get().strip()
        telefone       = self.telefone_entry.get().strip()
        email          = self.email_entry.get().strip()

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

        # ── Defesa em Profundidade: Autorização no Backend ────
        if self.session["role"] not in ("administrador", "recepcionista"):
            messagebox.showerror(
                "Erro de Permissão",
                "Ação não autorizada. Seu perfil não possui permissão para cadastrar pacientes.",
                parent=self.window
            )
            raise PermissionError("Acesso não autorizado para o perfil: " + self.session["role"])

        # ── Persistência ──────────────────────────────────────
        try:
            database.cadastrar_paciente(nome, data_nasc, cpf, cartao_sus, telefone, email, self.session)
            messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!", parent=self.window)
            self.listar_pacientes()
            self._limpar_campos()
            if self.callback_on_success:
                self.callback_on_success()
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Validação",
                "Já existe um paciente cadastrado com esse CPF ou Cartão SUS.",
                parent=self.window,
            )
        except Exception:
            messagebox.showerror(
                "Erro",
                "Ocorreu um erro inesperado ao cadastrar o paciente. Tente novamente.",
                parent=self.window,
            )

    def listar_pacientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            pacientes = database.listar_pacientes()
            for i, pac in enumerate(pacientes):
                sus = pac[2] if pac[2] else "—"
                tag = "odd" if i % 2 == 0 else "even"
                self.tree.insert("", "end", values=(pac[0], pac[1], sus), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar pacientes: {e}", parent=self.window)


# ──────────────────────────────────────────────────────────────
#  Execução standalone
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    app = CadastroPacienteWindow(root)
    app.window.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), sys.exit()))
    root.mainloop()