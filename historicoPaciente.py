from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import database
import theme


def _parse_date(date_str: str):
    """Converte strings de data do banco para objetos datetime."""
    if not date_str:
        return None
    date_str = date_str.strip()
    try:
        if "." in date_str:
            return datetime.strptime(date_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.fromisoformat(date_str)
        except Exception:
            return None


def historico_paciente(paciente_id):
    """Exibe a janela de histórico com tabela de medidas e gráficos evolutivos."""

    # ── Janela principal ──────────────────────────────────────
    historico_window = Toplevel()
    historico_window.title(f"Histórico de Medidas — Paciente #{paciente_id}")
    historico_window.geometry("1280x820")
    historico_window.configure(bg=theme.BG_DARK)
    theme.apply_theme(historico_window)

    figuras = []

    # ── Cabeçalho ─────────────────────────────────────────────
    header = Frame(historico_window, bg=theme.ACCENT, height=60)
    header.pack(fill=X)
    header.pack_propagate(False)

    Label(
        header,
        text=f"Histórico de Medidas — Paciente #{paciente_id}",
        font=theme.FONT_H2,
        bg=theme.ACCENT,
        fg="#0F1923",
        padx=24,
    ).pack(side=LEFT, fill=Y)

    Frame(historico_window, bg=theme.BORDER, height=1).pack(fill=X)

    # ── Seção: tabela de registros ────────────────────────────
    table_section = Frame(historico_window, bg=theme.BG_CARD, padx=16, pady=12)
    table_section.pack(fill=X)

    Label(
        table_section,
        text="Registros",
        font=theme.FONT_H3,
        bg=theme.BG_CARD,
        fg=theme.TEXT_SECONDARY,
    ).pack(anchor=W, pady=(0, 8))

    tree_frame = Frame(table_section, bg=theme.BG_CARD)
    tree_frame.pack(fill=X)

    columns = ("Data/Hora", "Peso (kg)", "Sistólica", "Diastólica", "Pulsação", "Temperatura (°C)")
    tree = ttk.Treeview(
        tree_frame,
        columns=columns,
        show="headings",
        style="Custom.Treeview",
        height=6,
    )

    vsb = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview,
                        style="Custom.Vertical.TScrollbar")
    hsb = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=tree.xview,
                        style="Custom.Horizontal.TScrollbar")
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side=RIGHT, fill=Y)
    hsb.pack(side=BOTTOM, fill=X)
    tree.pack(fill=X, expand=False)

    _col_widths = [165, 90, 100, 100, 90, 130]
    for col, w in zip(columns, _col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor=CENTER)

    tree.tag_configure("odd",  background=theme.ROW_ODD)
    tree.tag_configure("even", background=theme.ROW_EVEN)

    # ── Carga dos dados ───────────────────────────────────────
    try:
        medidas = database.obter_medidas_paciente(paciente_id)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao recuperar histórico: {e}")
        medidas = []

    for i, medida in enumerate(medidas):
        tag = "odd" if i % 2 == 0 else "even"
        tree.insert("", "end", values=medida, tags=(tag,))

    # ── Preparação dos dados para gráficos ────────────────────
    datas, pesos, sistolica, diastolica = [], [], [], []

    for medida in medidas:
        data_fmt = _parse_date(medida[0])
        if data_fmt:
            datas.append(data_fmt)
            pesos.append(medida[1])
            sistolica.append(medida[2])
            diastolica.append(medida[3])
        else:
            pass  # Data inválida: ignorada sem expor dados ao console

    # ── Divisor e seção de gráficos ───────────────────────────
    Frame(historico_window, bg=theme.BORDER, height=1).pack(fill=X)

    charts_header = Frame(historico_window, bg=theme.BG_DARK, padx=16, pady=10)
    charts_header.pack(fill=X)
    Label(
        charts_header,
        text="Evolução das Métricas",
        font=theme.FONT_H3,
        bg=theme.BG_DARK,
        fg=theme.TEXT_SECONDARY,
    ).pack(anchor=W)

    # Container com scroll vertical para os gráficos
    scroll_outer = Frame(historico_window, bg=theme.BG_DARK)
    scroll_outer.pack(fill=BOTH, expand=True)

    canvas_scroll = Canvas(scroll_outer, bg=theme.BG_DARK, highlightthickness=0)
    vsb_charts = ttk.Scrollbar(
        scroll_outer, orient=VERTICAL,
        command=canvas_scroll.yview,
        style="Custom.Vertical.TScrollbar",
    )
    canvas_scroll.configure(yscrollcommand=vsb_charts.set)
    vsb_charts.pack(side=RIGHT, fill=Y)
    canvas_scroll.pack(side=LEFT, fill=BOTH, expand=True)

    inner = Frame(canvas_scroll, bg=theme.BG_DARK)
    inner_id = canvas_scroll.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_configure(event):
        canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))

    def _on_canvas_resize(event):
        canvas_scroll.itemconfig(inner_id, width=event.width)

    inner.bind("<Configure>", _on_inner_configure)
    canvas_scroll.bind("<Configure>", _on_canvas_resize)

    # ── Tema Matplotlib ───────────────────────────────────────
    _BG     = theme.BG_CARD
    _AXES   = theme.BG_INPUT
    _TEXT   = theme.TEXT_SECONDARY
    _GRID   = theme.BORDER
    _COLORS = [theme.ACCENT, "#5B8DEF", "#F0A500"]

    def criar_grafico(titulo: str, dados_y: list, label_y: str, color: str):
        """Cria e empacota um gráfico estilizado no container de scroll."""
        validos = [(d, v) for d, v in zip(datas, dados_y) if v is not None]
        if not validos:
            return

        frame_g = Frame(
            inner,
            bg=_BG,
            padx=12,
            pady=12,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        frame_g.pack(fill=X, padx=16, pady=(0, 16))

        fig = Figure(figsize=(12, 3.4), dpi=96, facecolor=_BG)
        figuras.append(fig)

        ax = fig.add_subplot(111, facecolor=_AXES)

        xs, ys = zip(*validos)
        ax.plot(
            xs, ys,
            marker="o", markersize=5,
            linewidth=2.0,
            color=color,
            markerfacecolor=color,
            markeredgecolor=_BG,
            markeredgewidth=1.5,
        )
        ax.fill_between(xs, ys, alpha=0.08, color=color)

        ax.set_title(titulo, color=_TEXT, fontsize=11, fontweight="bold", pad=10)
        ax.set_xlabel("Data", color=_TEXT, fontsize=9)
        ax.set_ylabel(label_y, color=_TEXT, fontsize=9)
        ax.tick_params(colors=_TEXT, labelsize=8)
        ax.grid(True, color=_GRID, linewidth=0.5, alpha=0.6)
        for spine in ax.spines.values():
            spine.set_color(_GRID)

        fig.autofmt_xdate()
        fig.tight_layout(pad=1.5)

        canvas = FigureCanvasTkAgg(fig, master=frame_g)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=X)

    # ── Geração dos gráficos ──────────────────────────────────
    if datas:
        criar_grafico("Evolução do Peso",           pesos,     "Peso (kg)",        _COLORS[0])
        criar_grafico("Pressão Sistólica",          sistolica, "Sistólica (mmHg)", _COLORS[1])
        criar_grafico("Pressão Diastólica",         diastolica,"Diastólica (mmHg)",_COLORS[2])
    else:
        Label(
            inner,
            text="Nenhum dado disponível para gerar gráficos.",
            font=theme.FONT_BODY,
            bg=theme.BG_DARK,
            fg=theme.TEXT_SECONDARY,
        ).pack(pady=40)

    # ── Limpeza ao fechar ─────────────────────────────────────
    def on_close():
        for fig in figuras:
            try:
                fig.clear()
            except Exception:
                pass
        historico_window.destroy()

    historico_window.protocol("WM_DELETE_WINDOW", on_close)
