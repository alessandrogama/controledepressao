import sys
import os
import traceback
from tkinter import *
from tkinter import ttk, messagebox
from datetime import datetime
import database
import theme

# Caminho absoluto resolvido no momento do import para evitar ambiguidade quando
# o módulo é importado a partir de outro diretório de trabalho.
_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "medidor_error_log.txt")


def log_error(message: str):
    """Registra erros técnicos em arquivo local. Nunca exibe detalhes internos ao usuário."""
    try:
        with open(_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n--- ERRO [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ---\n")
            f.write(message)
            f.write("\n" + "=" * 80 + "\n")
    except Exception as e:
        print(f"Erro ao gravar no log de erros: {e}")


def _classificar_pressao(sistolica: int, diastolica: int) -> tuple[str, str]:
    """
    Retorna (texto_classificação, cor_hex) conforme diretrizes clínicas AHA/ESC.
    """
    if sistolica < 120 and diastolica < 80:
        return "Normal", theme.ACCENT
    elif sistolica < 130 and diastolica < 80:
        return "Elevada", "#F0A500"
    elif sistolica < 140 or (80 <= diastolica < 90):
        return "Alta — Estágio 1", "#E07A52"
    elif sistolica >= 180 or diastolica >= 120:
        return "Crise Hipertensiva", theme.DANGER
    else:
        return "Alta — Estágio 2", theme.DANGER


# ──────────────────────────────────────────────────────────────────────────────
class RegistroMedidasWindow:
    """Janela de registro de medidas vitais com indicador de pressão em tempo real."""

    def __init__(self, master, paciente_id, nome_paciente, callback_on_success=None):
        self.master              = master
        self.paciente_id         = paciente_id
        self.nome_paciente       = nome_paciente
        self.callback_on_success = callback_on_success

        self.window = Toplevel(master)
        self.window.title(f"Registro de Medidas — {nome_paciente}")
        self.window.geometry("560x580")
        self.window.resizable(False, False)
        self.window.configure(bg=theme.BG_DARK)
        theme.apply_theme(self.window)

        self._build_ui()

    # ──────────────────────────────────────────────────────────
    #  Interface
    # ──────────────────────────────────────────────────────────
    def _build_ui(self):
        w = self.window

        # ── Cabeçalho ─────────────────────────────────────────
        header = Frame(w, bg=theme.ACCENT, height=76)
        header.pack(fill=X)
        header.pack_propagate(False)

        Label(
            header,
            text="Registro de Medidas",
            font=theme.FONT_H2,
            bg=theme.ACCENT,
            fg="#0F1923",
        ).pack(anchor=W, padx=24, pady=(18, 0))
        Label(
            header,
            text=f"Paciente: {self.nome_paciente}  ·  ID #{self.paciente_id}",
            font=theme.FONT_LABEL,
            bg=theme.ACCENT,
            fg="#0F1923",
        ).pack(anchor=W, padx=24)

        # ── Card de campos ────────────────────────────────────
        card = Frame(
            w,
            bg=theme.BG_CARD,
            padx=28,
            pady=20,
            highlightthickness=0,
        )
        card.pack(fill=BOTH, expand=True, padx=16, pady=16)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        def _lbl(parent, text, row, col, **kw):
            Label(
                parent,
                text=text,
                font=theme.FONT_LABEL,
                bg=theme.BG_CARD,
                fg=theme.TEXT_SECONDARY,
                anchor=W,
                **kw,
            ).grid(row=row, column=col, sticky=W, padx=(0, 12) if col == 0 else 0, pady=(10, 2))

        def _entry(parent, row, col):
            e = Entry(
                parent,
                font=theme.FONT_BODY,
                bg=theme.BG_INPUT,
                fg=theme.TEXT_PRIMARY,
                insertbackground=theme.ACCENT,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=theme.BORDER,
                highlightcolor=theme.ACCENT,
                width=14,
            )
            e.grid(
                row=row, column=col,
                sticky=EW, ipady=7,
                padx=(0, 12) if col == 0 else 0,
            )
            return e

        # Linha 0-1: Sistólica | Diastólica
        _lbl(card, "Pressão Sistólica (mmHg)",  row=0, col=0)
        _lbl(card, "Pressão Diastólica (mmHg)", row=0, col=1)
        self.pressaoSistolica_entry  = _entry(card, row=1, col=0)
        self.pressaoDiastolica_entry = _entry(card, row=1, col=1)

        # Indicador de classificação
        self.lbl_class = Label(
            card,
            text="",
            font=(theme.FONT_FAMILY, 10, "bold"),
            bg=theme.BG_CARD,
            fg=theme.TEXT_SECONDARY,
            anchor=W,
        )
        self.lbl_class.grid(row=2, column=0, columnspan=2, sticky=W, pady=(4, 0))

        self.pressaoSistolica_entry.bind("<KeyRelease>",  self._atualizar_classificacao)
        self.pressaoDiastolica_entry.bind("<KeyRelease>", self._atualizar_classificacao)

        # Linha 2-3: Batimentos | Peso
        _lbl(card, "Batimentos Cardíacos (bpm)", row=3, col=0)
        _lbl(card, "Peso (kg)",                  row=3, col=1)
        self.batimentos_entry = _entry(card, row=4, col=0)
        self.peso_entry       = _entry(card, row=4, col=1)

        # Linha 4-5: Temperatura | ID (readonly)
        _lbl(card, "Temperatura (°C)", row=5, col=0)
        _lbl(card, "ID do Paciente",   row=5, col=1)
        self.temperatura_entry = _entry(card, row=6, col=0)

        id_entry = Entry(
            card,
            font=theme.FONT_BODY,
            bg=theme.BG_INPUT,
            fg=theme.TEXT_SECONDARY,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
            width=14,
            state="normal",
            readonlybackground=theme.BG_INPUT,
        )
        id_entry.grid(row=6, column=1, sticky=EW, ipady=7)
        id_entry.insert(0, str(self.paciente_id) if self.paciente_id else "")
        id_entry.config(state="readonly")

        # Separador
        Frame(card, bg=theme.BORDER, height=1).grid(
            row=7, column=0, columnspan=2, sticky=EW, pady=(18, 0)
        )

        # Observação
        _lbl(card, "Observação (opcional)", row=8, col=0)
        self.observacao_entry = Text(
            card,
            font=theme.FONT_BODY,
            bg=theme.BG_INPUT,
            fg=theme.TEXT_PRIMARY,
            insertbackground=theme.ACCENT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
            highlightcolor=theme.ACCENT,
            height=3,
        )
        self.observacao_entry.grid(row=9, column=0, columnspan=2, sticky=EW)

        # ── Botões ────────────────────────────────────────────
        btn_frame = Frame(card, bg=theme.BG_CARD, pady=16)
        btn_frame.grid(row=10, column=0, columnspan=2, sticky=EW)

        theme.HoverButton(
            btn_frame,
            text="Registrar",
            style="primary",
            font=(theme.FONT_FAMILY, 11, "bold"),
            command=self.registrar_medida,
        ).pack(side=LEFT, padx=(0, 12))

        theme.HoverButton(
            btn_frame,
            text="Limpar Campos",
            style="secondary",
            font=(theme.FONT_FAMILY, 11),
            command=self.limpar_campos,
        ).pack(side=LEFT)

    # ──────────────────────────────────────────────────────────
    #  Lógica
    # ──────────────────────────────────────────────────────────
    def _atualizar_classificacao(self, _event=None):
        """Atualiza o indicador de classificação de pressão em tempo real."""
        try:
            sist  = int(self.pressaoSistolica_entry.get())
            diast = int(self.pressaoDiastolica_entry.get())
            texto, cor = _classificar_pressao(sist, diast)
            self.lbl_class.config(text=f"  Classificação: {texto}", fg=cor)
        except ValueError:
            self.lbl_class.config(text="", fg=theme.TEXT_SECONDARY)

    def limpar_campos(self):
        """Limpa todos os campos de entrada."""
        for e in (
            self.pressaoSistolica_entry,
            self.pressaoDiastolica_entry,
            self.batimentos_entry,
            self.peso_entry,
            self.temperatura_entry,
        ):
            e.delete(0, END)
        self.observacao_entry.delete("1.0", END)
        self.lbl_class.config(text="", fg=theme.TEXT_SECONDARY)

    def registrar_medida(self):
        """Valida os campos e persiste a medida no banco de dados."""
        pressao_sistolica  = self.pressaoSistolica_entry.get().strip()
        pressao_diastolica = self.pressaoDiastolica_entry.get().strip()
        batimentos         = self.batimentos_entry.get().strip()
        temperatura        = self.temperatura_entry.get().strip()
        peso               = self.peso_entry.get().strip()

        # Validação de campos obrigatórios
        if not pressao_sistolica or not pressao_diastolica or not batimentos or not temperatura:
            messagebox.showerror(
                "Validação",
                "Pressão Sistólica, Pressão Diastólica, Batimentos e Temperatura são obrigatórios.",
                parent=self.window,
            )
            return

        try:
            sistolica = int(pressao_sistolica)
            diastolica = int(pressao_diastolica)
            if sistolica <= 0 or diastolica <= 0:
                raise ValueError("Pressão deve ser um número positivo.")

            batimentos_val = int(batimentos)
            if batimentos_val <= 0:
                raise ValueError("Batimentos devem ser um número positivo.")

            temperatura_val = float(temperatura)
            peso_val        = float(peso) if peso else None

            database.registrar_medida(
                self.paciente_id,
                datetime.now(),
                peso_val,
                sistolica,
                diastolica,
                batimentos_val,
                temperatura_val,
            )

            messagebox.showinfo("Sucesso", "Medida registrada com sucesso!", parent=self.window)
            self.limpar_campos()

            if self.callback_on_success:
                self.callback_on_success()

            self.window.destroy()

        except ValueError:
            messagebox.showerror(
                "Validação",
                "Insira números válidos e positivos para Pressão, Batimentos e Temperatura.",
                parent=self.window,
            )
        except Exception as e:
            log_error(f"Erro em registrar_medida: {e}\n{traceback.format_exc()}")
            messagebox.showerror(
                "Erro",
                "Ocorreu um erro inesperado ao registrar a medida. Verifique o log de erros.",
                parent=self.window,
            )


# ──────────────────────────────────────────────────────────────
#  Execução standalone
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    paciente_id_arg    = None
    nome_paciente_arg  = "Paciente Desconhecido"

    try:
        if len(sys.argv) > 1:
            paciente_id_arg = sys.argv[1]
        if len(sys.argv) > 2:
            nome_paciente_arg = sys.argv[2]

        root = Tk()
        root.withdraw()
        app = RegistroMedidasWindow(root, paciente_id_arg, nome_paciente_arg)
        app.window.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), sys.exit()))
        root.mainloop()

    except Exception as e:
        error_info        = traceback.format_exc()
        full_error_message = f"Erro na inicialização de medidor.py:\n\nDetalhes:\n{error_info}"
        print(f"ERRO DE INICIALIZAÇÃO NO MEDIDOR.PY:\n{full_error_message}")
        log_error(full_error_message)
        try:
            temp_root = Tk()
            temp_root.withdraw()
            messagebox.showerror(
                "Erro de Inicialização",
                "Ocorreu um erro ao iniciar a tela de registro de medidas.\n"
                "Verifique o console ou o log de erros.",
            )
            temp_root.destroy()
        except Exception:
            pass
        sys.exit(1)