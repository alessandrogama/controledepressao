import sys
from tkinter import *
from tkinter import ttk, messagebox
import database
import theme
from cadastropaciente import CadastroPacienteWindow
from medidor import RegistroMedidasWindow

# ──────────────────────────────────────────────────────────────
#  Estado da aplicação
# ──────────────────────────────────────────────────────────────
_todos_pacientes = []
_session = None

# ──────────────────────────────────────────────────────────────
#  Lógica de negócio
# ──────────────────────────────────────────────────────────────
def conectar_bd():
    """Inicializa o banco de dados na primeira execução."""
    database.inicializar_banco()


def _atualizar_status():
    """Atualiza o label de rodapé com o total de linhas visíveis."""
    total = len(tree.get_children())
    s = "s" if total != 1 else ""
    lbl_status.config(text=f"  {total} paciente{s} listado{s}")


def listar_pacientes(filtro: str = ""):
    """Recarrega a tabela, aplicando filtro por nome se fornecido."""
    global _todos_pacientes
    for item in tree.get_children():
        tree.delete(item)

    _todos_pacientes = database.listar_pacientes()
    filtro = filtro.lower().strip()

    for i, paciente in enumerate(_todos_pacientes):
        nome = paciente[1] or ""
        if filtro and filtro not in nome.lower():
            continue
        sus = paciente[2] if paciente[2] else "—"
        tag = "odd" if i % 2 == 0 else "even"
        tree.insert(
            "", "end",
            values=(paciente[0], nome, sus, "Medir", "Editar", "Histórico"),
            tags=(tag,),
        )

    _atualizar_status()


def _on_search(_event=None):
    listar_pacientes(filtro=entry_search.get_value())


def _atualizar_lista():
    """Recarrega toda a lista e reseta o campo de busca."""
    entry_search.clear()
    listar_pacientes()


def abrir_medidor(paciente_id, nome_paciente):
    try:
        RegistroMedidasWindow(
            root, paciente_id, nome_paciente, _session,
            callback_on_success=lambda: listar_pacientes(filtro=entry_search.get_value()),
        )
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao abrir o medidor: {e}")


def abrir_cadastro():
    if _session["role"] not in ("administrador", "recepcionista"):
        database.registrar_log_auditoria(
            _session.get("id"),
            _session.get("username"),
            _session.get("role"),
            "ACCESS_DENIED",
            "Tentativa de abertura da tela de cadastro de pacientes bloqueada."
        )
        messagebox.showwarning(
            "Acesso Negado",
            "Apenas administradores e recepcionistas possuem permissão para cadastrar pacientes.",
            parent=root
        )
        return
    try:
        CadastroPacienteWindow(
            root, _session,
            callback_on_success=lambda: listar_pacientes(filtro=entry_search.get_value()),
        )
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao abrir o cadastro: {e}")


def abrir_auditoria():
    if _session["role"] != "administrador":
        database.registrar_log_auditoria(
            _session.get("id"),
            _session.get("username"),
            _session.get("role"),
            "ACCESS_DENIED",
            "Tentativa de abertura do painel de auditoria do sistema bloqueada."
        )
        messagebox.showwarning(
            "Acesso Negado",
            "Acesso negado. Apenas administradores podem visualizar os registros de auditoria.",
            parent=root
        )
        return
    try:
        from auditoria import AuditoriaWindow
        AuditoriaWindow(root, _session)
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao abrir a auditoria: {e}")


def historico_paciente(paciente_id, session=None):
    try:
        import historicoPaciente
        historicoPaciente.historico_paciente(paciente_id, session)
    except ImportError:
        messagebox.showerror("Erro", "Arquivo 'historicoPaciente.py' não encontrado!")
    except Exception as e:
        messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao abrir o histórico: {e}")


def on_dashboard_close():
    """Registra o log de LOGOUT e encerra o aplicativo."""
    if _session:
        database.registrar_log_auditoria(
            _session.get("id"),
            _session.get("username"),
            _session.get("role"),
            "LOGOUT",
            "Sessão encerrada pelo fechamento da aplicação."
        )
    root.destroy()


def on_treeview_click(event):
    """Roteador de cliques na tabela de pacientes de acordo com os perfis (RBAC)."""
    if tree.identify_region(event.x, event.y) != "cell":
        return
    column = tree.identify_column(event.x)
    item = tree.identify_row(event.y)
    if not item:
        return

    values = tree.item(item, "values")
    paciente_id  = values[0]
    nome_paciente = values[1]

    if column == "#4":      # Medir
        if _session["role"] not in ("medico", "enfermeiro"):
            database.registrar_log_auditoria(
                _session.get("id"),
                _session.get("username"),
                _session.get("role"),
                "ACCESS_DENIED",
                f"Tentativa de medição no paciente_id={paciente_id} bloqueada."
            )
            messagebox.showwarning(
                "Acesso Negado",
                "Apenas médicos e enfermeiros possuem permissão para registrar medições.",
                parent=root
            )
            return
        abrir_medidor(paciente_id, nome_paciente)
    elif column == "#5":    # Editar
        if _session["role"] not in ("administrador", "recepcionista"):
            database.registrar_log_auditoria(
                _session.get("id"),
                _session.get("username"),
                _session.get("role"),
                "ACCESS_DENIED",
                f"Tentativa de edição de cadastro no paciente_id={paciente_id} bloqueada."
            )
            messagebox.showwarning(
                "Acesso Negado",
                "Apenas administradores e recepcionistas possuem permissão para editar dados cadastrais.",
                parent=root
            )
            return
        messagebox.showinfo("Em breve", "Funcionalidade de edição ainda não implementada.")
    elif column == "#6":    # Histórico
        if _session["role"] not in ("medico", "administrador"):
            database.registrar_log_auditoria(
                _session.get("id"),
                _session.get("username"),
                _session.get("role"),
                "ACCESS_DENIED",
                f"Tentativa de acesso ao histórico clínico do paciente_id={paciente_id} bloqueada."
            )
            messagebox.showwarning(
                "Acesso Negado",
                "Apenas médicos e administradores possuem permissão para acessar o histórico clínico de gráficos.",
                parent=root
            )
            return
        historico_paciente(paciente_id, _session)


# ──────────────────────────────────────────────────────────────
#  Interface Principal
# ──────────────────────────────────────────────────────────────
root = Tk()
root.title("Controle de Pacientes — Dashboard")
root.geometry("1150x640")
root.minsize(900, 520)
theme.apply_theme(root)

try:
    root.iconbitmap("icon/logo.ico")
except Exception:
    pass

# ────────────────────────────────────────────────────────────
#  SIDEBAR
# ────────────────────────────────────────────────────────────
sidebar = Frame(root, bg=theme.BG_SIDEBAR, width=220)
sidebar.pack(side=LEFT, fill=Y)
sidebar.pack_propagate(False)

# Área do logo/marca
brand_frame = Frame(sidebar, bg=theme.BG_SIDEBAR, pady=30)
brand_frame.pack(fill=X)

# Ícone circular decorativo
Label(
    brand_frame,
    text="◉",
    font=("Segoe UI", 30),
    bg=theme.BG_SIDEBAR,
    fg=theme.ACCENT,
).pack()
Label(
    brand_frame,
    text="Controle de Pressão",
    font=theme.FONT_H3,
    bg=theme.BG_SIDEBAR,
    fg=theme.TEXT_PRIMARY,
).pack(pady=(4, 2))
Label(
    brand_frame,
    text="Monitoramento Clínico",
    font=theme.FONT_SMALL,
    bg=theme.BG_SIDEBAR,
    fg=theme.TEXT_SECONDARY,
).pack()

# Separador
Frame(sidebar, bg=theme.BORDER, height=1).pack(fill=X, padx=20, pady=6)

# Rótulo de seção
Label(
    sidebar,
    text="NAVEGAÇÃO",
    font=theme.FONT_SMALL,
    bg=theme.BG_SIDEBAR,
    fg=theme.TEXT_SECONDARY,
    anchor=W,
    padx=22,
    pady=8,
).pack(fill=X)

# Botões de navegação
btn_novo = theme.HoverButton(
    sidebar,
    style="sidebar",
    text="  +  Novo Paciente",
    font=(theme.FONT_FAMILY, 11),
    anchor=W,
    padx=22,
    pady=13,
    command=abrir_cadastro,
)
btn_novo.pack(fill=X)

btn_atualizar = theme.HoverButton(
    sidebar,
    style="sidebar",
    text="  ↻  Atualizar Lista",
    font=(theme.FONT_FAMILY, 11),
    anchor=W,
    padx=22,
    pady=13,
    command=_atualizar_lista,
)
btn_atualizar.pack(fill=X)

btn_auditoria = theme.HoverButton(
    sidebar,
    style="sidebar",
    text="  ✦  Auditoria do Sistema",
    font=(theme.FONT_FAMILY, 11),
    anchor=W,
    padx=22,
    pady=13,
    command=abrir_auditoria,
)

# Rodapé da sidebar
Frame(sidebar, bg=theme.BORDER, height=1).pack(side=BOTTOM, fill=X, padx=20, pady=6)
Label(
    sidebar,
    text="v1.0.0 · Projeto de Aprendizagem",
    font=theme.FONT_SMALL,
    bg=theme.BG_SIDEBAR,
    fg=theme.TEXT_SECONDARY,
    wraplength=180,
    justify=CENTER,
    pady=12,
).pack(side=BOTTOM)

lbl_operator = Label(
    sidebar,
    text="Operador:\nNão autenticado",
    font=theme.FONT_SMALL,
    bg=theme.BG_SIDEBAR,
    fg=theme.TEXT_SECONDARY,
    justify=LEFT,
    anchor=W,
    padx=22,
    pady=10,
)
lbl_operator.pack(side=BOTTOM, fill=X)

# ────────────────────────────────────────────────────────────
#  ÁREA PRINCIPAL
# ────────────────────────────────────────────────────────────
main_area = Frame(root, bg=theme.BG_DARK)
main_area.pack(side=LEFT, fill=BOTH, expand=True)

# ── Top bar ──────────────────────────────────────────────────
topbar = Frame(main_area, bg=theme.BG_CARD, height=68)
topbar.pack(fill=X)
topbar.pack_propagate(False)

Label(
    topbar,
    text="Pacientes Cadastrados",
    font=theme.FONT_H2,
    bg=theme.BG_CARD,
    fg=theme.TEXT_PRIMARY,
    padx=24,
).pack(side=LEFT, fill=Y)

# Campo de busca (à direita da topbar)
search_wrapper = Frame(topbar, bg=theme.BG_CARD, padx=20)
search_wrapper.pack(side=RIGHT, fill=Y)

Label(
    search_wrapper,
    text="Buscar:",
    font=theme.FONT_LABEL,
    bg=theme.BG_CARD,
    fg=theme.TEXT_SECONDARY,
).pack(side=LEFT, padx=(0, 8))

entry_search = theme.PlaceholderEntry(
    search_wrapper,
    placeholder="Nome do paciente...",
    width=26,
)
entry_search.pack(side=LEFT, ipady=6)
entry_search.bind("<KeyRelease>", _on_search)

Frame(main_area, bg=theme.BORDER, height=1).pack(fill=X)

# ── Área da tabela ────────────────────────────────────────────
table_area = Frame(main_area, bg=theme.BG_DARK, padx=16, pady=16)
table_area.pack(fill=BOTH, expand=True)

columns = ("ID", "Nome", "Cartão SUS", "Medir", "Editar", "Histórico")
tree = ttk.Treeview(
    table_area,
    columns=columns,
    show="headings",
    style="Custom.Treeview",
)

vsb = ttk.Scrollbar(
    table_area,
    orient=VERTICAL,
    command=tree.yview,
    style="Custom.Vertical.TScrollbar",
)
tree.configure(yscrollcommand=vsb.set)

vsb.pack(side=RIGHT, fill=Y)
tree.pack(fill=BOTH, expand=True)

# Configuração de colunas
_COL_CFG = {
    "ID":          (55,  CENTER),
    "Nome":        (300, W),
    "Cartão SUS":  (160, CENTER),
    "Medir":       (90,  CENTER),
    "Editar":      (90,  CENTER),
    "Histórico":   (90,  CENTER),
}
for col in columns:
    width, anchor = _COL_CFG.get(col, (120, CENTER))
    tree.heading(col, text=col)
    tree.column(col, width=width, anchor=anchor, minwidth=50)

# Tags para linhas alternadas
tree.tag_configure("odd",  background=theme.ROW_ODD)
tree.tag_configure("even", background=theme.ROW_EVEN)

# Bind de clique
tree.bind("<Button-1>", on_treeview_click)

# ── Barra de status ───────────────────────────────────────────
Frame(main_area, bg=theme.BORDER, height=1).pack(fill=X, side=BOTTOM)
status_bar = Frame(main_area, bg=theme.BG_SIDEBAR, height=30)
status_bar.pack(fill=X, side=BOTTOM)
status_bar.pack_propagate(False)

lbl_status = Label(
    status_bar,
    text="  0 pacientes listados",
    font=theme.FONT_SMALL,
    bg=theme.BG_SIDEBAR,
    fg=theme.TEXT_SECONDARY,
    anchor=W,
)
lbl_status.pack(side=LEFT, fill=Y)

# ──────────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    conectar_bd()
    
    # Ocultar janela raiz durante a autenticação
    root.withdraw()
    
    from login import LoginWindow
    login_app = LoginWindow(root)
    root.wait_window(login_app.window)
    
    if login_app.session:
        _session = login_app.session
        
        # Exibe as informações do operador ativo
        role_label = _session["role"].capitalize()
        lbl_operator.config(
            text=f"Operador:\n{_session['username']} ({role_label})",
            fg=theme.ACCENT
        )
        
        # Registrar protocolo de fechamento para gravar LOGOUT
        root.protocol("WM_DELETE_WINDOW", on_dashboard_close)
        
        # Exibir botão de auditoria se for administrador
        if _session["role"] == "administrador":
            btn_auditoria.pack(fill=X)
        
        # Restaurar janela principal
        root.deiconify()
        listar_pacientes()
        root.mainloop()
    else:
        root.destroy()
        sys.exit(0)