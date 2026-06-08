"""
theme.py — Design system centralizado do projeto Controle de Pressão.

Define a paleta de cores, fontes e funções/classes auxiliares para criar
widgets com estilo consistente em toda a aplicação.
"""

import tkinter as tk
from tkinter import ttk

# ──────────────────────────────────────────────────────────────
#  Paleta de Cores (dark mode clínico)
# ──────────────────────────────────────────────────────────────
BG_DARK        = "#0F1923"   # Fundo principal
BG_CARD        = "#162230"   # Cards e painéis
BG_INPUT       = "#1E2E3D"   # Campos de entrada
BG_SIDEBAR     = "#0B1520"   # Sidebar / header escuro

ACCENT         = "#00C9A7"   # Ação primária / destaque
ACCENT_DIM     = "#009E84"   # Hover de botão primário

DANGER         = "#E05252"   # Ação destrutiva / alerta
DANGER_DIM     = "#B83E3E"   # Hover de botão perigo

TEXT_PRIMARY   = "#E8EDF2"   # Texto principal
TEXT_SECONDARY = "#8A9BAE"   # Rótulos e textos auxiliares

BORDER         = "#253545"   # Bordas de cards e inputs
ROW_ODD        = "#162230"   # Linha ímpar da tabela
ROW_EVEN       = "#192839"   # Linha par da tabela
ROW_SELECT     = "#1A3A4A"   # Linha selecionada na tabela

# ──────────────────────────────────────────────────────────────
#  Tipografia
# ──────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"     # Nativo do Windows, sem instalação extra

FONT_H1    = (FONT_FAMILY, 20, "bold")
FONT_H2    = (FONT_FAMILY, 14, "bold")
FONT_H3    = (FONT_FAMILY, 11, "bold")
FONT_BODY  = (FONT_FAMILY, 11)
FONT_LABEL = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 9)


# ──────────────────────────────────────────────────────────────
#  Função principal de tema
# ──────────────────────────────────────────────────────────────
def apply_theme(root: tk.Misc) -> ttk.Style:
    """
    Aplica o tema dark clínico ao widget raiz e configura o ttk.Style
    globalmente para a aplicação. Retorna o objeto Style.
    """
    root.configure(bg=BG_DARK)

    style = ttk.Style(root)
    style.theme_use("clam")

    # ── Treeview ──────────────────────────────────────────────────
    style.configure(
        "Custom.Treeview",
        background=ROW_ODD,
        foreground=TEXT_PRIMARY,
        fieldbackground=ROW_ODD,
        borderwidth=0,
        rowheight=38,
        font=FONT_BODY,
    )
    style.configure(
        "Custom.Treeview.Heading",
        background=BG_SIDEBAR,
        foreground=TEXT_SECONDARY,
        borderwidth=0,
        relief="flat",
        font=FONT_H3,
        padding=(10, 12),
    )
    style.map(
        "Custom.Treeview",
        background=[("selected", ROW_SELECT)],
        foreground=[("selected", TEXT_PRIMARY)],
    )
    style.map(
        "Custom.Treeview.Heading",
        background=[("active", BG_CARD)],
        relief=[("active", "flat")],
    )

    # ── Scrollbars ────────────────────────────────────────────────
    for name in ("Custom.Vertical.TScrollbar", "Custom.Horizontal.TScrollbar"):
        style.configure(
            name,
            background=BORDER,
            troughcolor=BG_DARK,
            arrowcolor=TEXT_SECONDARY,
            borderwidth=0,
            relief="flat",
            width=8,
        )
        style.map(name, background=[("active", ACCENT_DIM)])

    return style


# ──────────────────────────────────────────────────────────────
#  Helpers de widgets
# ──────────────────────────────────────────────────────────────
def make_card(parent: tk.Widget, **kwargs) -> tk.Frame:
    """Cria um Frame estilizado como card com borda sutil e highlight de foco."""
    defaults = dict(
        bg=BG_CARD,
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
    )
    defaults.update(kwargs)
    return tk.Frame(parent, **defaults)


def make_separator(parent: tk.Widget, orient: str = "horizontal") -> tk.Frame:
    """Cria um separador visual de 1px."""
    if orient == "horizontal":
        return tk.Frame(parent, bg=BORDER, height=1, bd=0)
    return tk.Frame(parent, bg=BORDER, width=1, bd=0)


# ──────────────────────────────────────────────────────────────
#  PlaceholderEntry
# ──────────────────────────────────────────────────────────────
class PlaceholderEntry(tk.Entry):
    """
    Campo Entry com placeholder dinâmico, highlight de foco colorido
    e estilo consistente com o design system.
    """

    def __init__(self, parent: tk.Widget, placeholder: str = "", **kwargs):
        self._show_char = kwargs.pop("show", "")
        super().__init__(
            parent,
            font=FONT_BODY,
            bg=BG_INPUT,
            fg=TEXT_SECONDARY,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            **kwargs,
        )
        self._placeholder = placeholder
        self._has_placeholder = False
        self._set_placeholder()
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _set_placeholder(self):
        if not self.get():
            self.config(show="")
            self.insert(0, self._placeholder)
            self.config(fg=TEXT_SECONDARY)
            self._has_placeholder = True

    def _on_focus_in(self, _event=None):
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.config(fg=TEXT_PRIMARY, show=self._show_char)
            self._has_placeholder = False

    def _on_focus_out(self, _event=None):
        if not self.get():
            self._set_placeholder()

    def get_value(self) -> str:
        """Retorna o valor real do campo, ignorando o texto de placeholder."""
        return "" if self._has_placeholder else self.get()

    def set_value(self, value: str):
        """Define o valor do campo programaticamente, removendo o placeholder."""
        self._has_placeholder = False
        self.delete(0, tk.END)
        self.config(fg=TEXT_PRIMARY, show=self._show_char)
        self.insert(0, value)

    def clear(self):
        """Limpa o campo e restaura o placeholder."""
        self.delete(0, tk.END)
        self._set_placeholder()


# ──────────────────────────────────────────────────────────────
#  HoverButton
# ──────────────────────────────────────────────────────────────
class HoverButton(tk.Button):
    """
    Botão com efeito de hover animado e variantes de estilo pré-definidas.

    Styles disponíveis:
        primary   — fundo accent, texto escuro (ação principal)
        secondary — fundo escuro, texto secundário (ação auxiliar)
        danger    — fundo vermelho (ação destrutiva)
        sidebar   — fundo da sidebar, texto secundário (navegação)
    """

    _PALETTES = {
        "primary":   (ACCENT,      "#0F1923", ACCENT_DIM),
        "secondary": (BG_INPUT,    TEXT_SECONDARY, BORDER),
        "danger":    (DANGER,      "#FFFFFF",  DANGER_DIM),
        "sidebar":   (BG_SIDEBAR,  TEXT_SECONDARY, BG_CARD),
    }

    def __init__(self, parent: tk.Widget, style: str = "primary", **kwargs):
        bg, fg, hover = self._PALETTES.get(style, self._PALETTES["primary"])

        defaults = dict(
            font=FONT_LABEL,
            fg=fg,
            bg=bg,
            activeforeground=fg,
            activebackground=hover,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=18,
            pady=9,
        )
        defaults.update(kwargs)
        super().__init__(parent, **defaults)
        self._bg = defaults["bg"]
        self._hover = hover
        self.bind("<Enter>", lambda _: self.config(bg=self._hover))
        self.bind("<Leave>", lambda _: self.config(bg=self._bg))
