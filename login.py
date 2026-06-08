import tkinter as tk
from tkinter import messagebox
import theme
import database

class LoginWindow:
    """
    Janela de Login modal da aplicação.
    Bloqueia a execução até que o usuário seja autenticado com sucesso
    ou feche a tela de login.
    """

    def __init__(self, master):
        self.master = master
        self.session = None

        self.window = tk.Toplevel(master)
        self.window.title("Controle de Pressão — Acesso")
        self.window.geometry("420x420")
        self.window.resizable(False, False)
        self.window.configure(bg=theme.BG_DARK)
        theme.apply_theme(self.window)

        # Centralizar na tela
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        # Configurar modalidade (grab_set)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()

    def _build_ui(self):
        w = self.window

        card = theme.make_card(w)
        card.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Logo / Marca decorativa
        tk.Label(
            card,
            text="◉",
            font=(theme.FONT_FAMILY, 32),
            bg=theme.BG_CARD,
            fg=theme.ACCENT,
        ).pack(pady=(15, 0))

        tk.Label(
            card,
            text="Acesso ao Sistema",
            font=theme.FONT_H2,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
        ).pack(pady=(0, 20))

        # Campo Usuário
        tk.Label(
            card,
            text="Usuário",
            font=theme.FONT_LABEL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_SECONDARY,
        ).pack(anchor=tk.W, padx=30, pady=(0, 2))

        self.user_entry = theme.PlaceholderEntry(card, placeholder="Nome de usuário")
        self.user_entry.pack(fill=tk.X, padx=30, ipady=6)

        # Campo Senha
        tk.Label(
            card,
            text="Senha",
            font=theme.FONT_LABEL,
            bg=theme.BG_CARD,
            fg=theme.TEXT_SECONDARY,
        ).pack(anchor=tk.W, padx=30, pady=(12, 2))

        self.pwd_entry = theme.PlaceholderEntry(card, placeholder="Sua senha", show="*")
        self.pwd_entry.pack(fill=tk.X, padx=30, ipady=6)

        # Label para mensagens de erro
        self.lbl_error = tk.Label(
            card,
            text="",
            font=theme.FONT_SMALL,
            bg=theme.BG_CARD,
            fg=theme.DANGER,
        )
        self.lbl_error.pack(pady=(8, 0))

        # Botão de Login
        btn_entrar = theme.HoverButton(
            card,
            text="Acessar",
            style="primary",
            font=(theme.FONT_FAMILY, 11, "bold"),
            command=self._do_login,
        )
        btn_entrar.pack(fill=tk.X, padx=30, pady=(15, 15))

        # Atalho de teclado Enter para submeter
        self.user_entry.bind("<Return>", lambda _: self._do_login())
        self.pwd_entry.bind("<Return>", lambda _: self._do_login())

        # Foco inicial no campo de Usuário
        self.user_entry.focus()

    def _do_login(self):
        username = self.user_entry.get_value().strip()
        password = self.pwd_entry.get_value().strip()

        if not username or not password:
            self.lbl_error.config(text="Preencha o usuário e a senha.")
            return

        session = database.autenticar_usuario(username, password)
        if session:
            self.session = session
            self.window.grab_release()
            self.window.destroy()
        else:
            self.lbl_error.config(text="Usuário ou senha incorretos.")

    def _on_close(self):
        self.session = None
        self.window.grab_release()
        self.window.destroy()


# Execução para testes rápidos da interface de login
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    app = LoginWindow(root)
    root.wait_window(app.window)
    print("Sessão obtida:", app.session)
    root.destroy()
