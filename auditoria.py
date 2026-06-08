import sys
import tkinter as tk
from tkinter import ttk, messagebox
import database
import theme

class AuditoriaWindow:
    """
    Janela de visualização da trilha de auditoria do sistema.
    Restrita exclusivamente ao perfil de administrador.
    """

    def __init__(self, master, session=None):
        self.master = master
        self.session = session

        # ── Defesa em Profundidade: Validação do Perfil no Backend ──
        if not self.session or self.session.get("role") != "administrador":
            # Registrar log de acesso negado
            user_id = self.session.get("id") if self.session else None
            username = self.session.get("username") if self.session else "desconhecido"
            role = self.session.get("role") if self.session else "nenhum"
            database.registrar_log_auditoria(
                user_id, username, role, "ACCESS_DENIED",
                "Tentativa não autorizada de abrir a tela de Auditoria do Sistema."
            )

            messagebox.showerror(
                "Acesso Negado",
                "Acesso negado. Apenas administradores podem visualizar os registros de auditoria.",
                parent=master
            )
            raise PermissionError("Acesso não autorizado à tela de auditoria.")

        self.window = tk.Toplevel(master)
        self.window.title("Auditoria do Sistema")
        self.window.geometry("960x600")
        self.window.minsize(800, 480)
        self.window.configure(bg=theme.BG_DARK)
        theme.apply_theme(self.window)

        self._build_ui()
        self.carregar_logs()

    def _build_ui(self):
        w = self.window

        # ── Cabeçalho ─────────────────────────────────────────
        header = tk.Frame(w, bg=theme.BG_CARD, height=68)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Trilha de Auditoria (Logs)",
            font=theme.FONT_H2,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            padx=24,
        ).pack(side=tk.LEFT, fill=tk.Y)

        # Botão de atualizar à direita do cabeçalho
        btn_refresh = theme.HoverButton(
            header,
            text="↻  Atualizar",
            style="secondary",
            font=theme.FONT_LABEL,
            command=self.carregar_logs,
        )
        btn_refresh.pack(side=tk.RIGHT, padx=24, pady=15)

        tk.Frame(w, bg=theme.BORDER, height=1).pack(fill=tk.X)

        # ── Corpo da tabela ───────────────────────────────────
        body = tk.Frame(w, bg=theme.BG_DARK, padx=20, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        columns = ("Data/Hora", "Operador", "Perfil", "Evento", "Detalhes")
        self.tree = ttk.Treeview(
            body,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
        )

        vsb = ttk.Scrollbar(
            body,
            orient=tk.VERTICAL,
            command=self.tree.yview,
            style="Custom.Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=vsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configuração das colunas
        _col_widths = {
            "Data/Hora": (170, tk.CENTER),
            "Operador":  (110, tk.W),
            "Perfil":    (110, tk.CENTER),
            "Evento":    (180, tk.CENTER),
            "Detalhes":  (320, tk.W),
        }
        for col in columns:
            w_col, anchor = _col_widths[col]
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w_col, anchor=anchor, minwidth=50)

        self.tree.tag_configure("odd",  background=theme.ROW_ODD)
        self.tree.tag_configure("even", background=theme.ROW_EVEN)

    def carregar_logs(self):
        """Busca os logs do banco de dados e atualiza a tabela."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        logs = database.obter_logs_auditoria()
        for i, log in enumerate(logs):
            tag = "odd" if i % 2 == 0 else "even"
            # Formatar papel para exibição
            role_display = log[2].capitalize() if log[2] else "—"
            row_values = (log[0], log[1] or "—", role_display, log[3], log[4] or "")
            self.tree.insert("", "end", values=row_values, tags=(tag,))


# Execução standalone para testes rápidos
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    # Criar uma sessão mock de administrador
    admin_session = {"id": 1, "username": "admin", "role": "administrador"}
    
    try:
        app = AuditoriaWindow(root, session=admin_session)
        app.window.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), sys.exit()))
        root.mainloop()
    except Exception as e:
        print(f"Erro ao inicializar janela de auditoria: {e}")
        root.destroy()
