import os
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

import customtkinter as ctk

from services import (
    load_config,
    run_opencv_module,
    run_reconstruction_module,
    run_volume_module,
)


BG = "#F8F9FA"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#212121"
TEXT_SECONDARY = "#616161"
CARD_BORDER = "#E0E0E0"
HOVER_BG = "#F3F5F7"
HOVER_BORDER = "#D0D6DB"

STEP_COLORS = ["#7C4DFF", "#F06292", "#26C6DA", "#FFA726"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _pick_font():
    preferred = ["Inter", "Roboto", "Arial"]
    families = set(tkfont.families())
    for name in preferred:
        if name in families:
            return name
    return "Arial"


def _center_window(root, width, height):
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = int((sw - width) / 2)
    y = int((sh - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def _resolve_path(path):
    if not path:
        return ""
    if os.path.isabs(path):
        return path
    return os.path.abspath(os.path.join(BASE_DIR, path))


def _open_path(path):
    if not path:
        return
    if sys.platform == "darwin":
        subprocess.run(["open", path])
    elif os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", path])


class StepCard(ctk.CTkFrame):
    def __init__(self, master, step, title, subtitle, color, icon, command):
        super().__init__(
            master,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.command = command

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        icon_label.grid(row=0, column=0, padx=(16, 8), pady=16, sticky="w")

        circle = ctk.CTkLabel(
            self,
            text=str(step),
            fg_color=color,
            text_color="white",
            corner_radius=18,
            width=36,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        circle.grid(row=0, column=1, padx=(0, 12), pady=16, sticky="w")

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=2, sticky="w")

        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            text_frame,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        )
        subtitle_label.pack(anchor="w")

        arrow_btn = ctk.CTkButton(
            self,
            text="→",
            width=40,
            height=36,
            corner_radius=12,
            fg_color="#E9ECEF",
            hover_color="#DEE2E6",
            text_color=TEXT_PRIMARY,
            command=self._on_click,
        )
        arrow_btn.grid(row=0, column=3, padx=(8, 16), pady=16, sticky="e")

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for child in self.winfo_children():
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

    def _on_click(self):
        if self.command:
            self.command()

    def _on_enter(self, _event):
        self.configure(fg_color=HOVER_BG, border_color=HOVER_BORDER)

    def _on_leave(self, _event):
        self.configure(fg_color=CARD_BG, border_color=CARD_BORDER)


class HistoryPanel(ctk.CTkFrame):
    def __init__(self, master, title, subtitle, path, mode="dir"):
        super().__init__(
            master,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=CARD_BORDER,
        )
        self.path = path
        self.mode = mode
        os.makedirs(self.path, exist_ok=True)

        self.items = []

        header = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        header.pack(anchor="w", padx=14, pady=(12, 0))

        sub = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
        )
        sub.pack(anchor="w", padx=14, pady=(0, 6))

        frame_list = tk.Frame(self)
        frame_list.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        scrollbar = tk.Scrollbar(frame_list)
        scrollbar.pack(side="right", fill="y")

        self.listbox = tk.Listbox(frame_list, yscrollcommand=scrollbar.set, font=("Consolas", 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.detail = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
            wraplength=360,
            justify="left",
        )
        self.detail.pack(anchor="w", padx=14, pady=(0, 8))

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(pady=(0, 12))

        ctk.CTkButton(actions, text="Atualizar", width=90, command=self.refresh).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Abrir", width=90, command=self.open_selected).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Abrir pasta", width=110, command=self.open_folder).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Excluir", width=90, command=self.delete_selected).pack(side="left", padx=4)

        self.listbox.bind("<<ListboxSelect>>", self.update_detail)
        self.refresh()

    def refresh(self):
        self.items = []
        self.listbox.delete(0, "end")
        try:
            entries = os.listdir(self.path)
        except Exception:
            entries = []

        if self.mode == "volumes":
            files = [
                f for f in entries
                if f.lower().endswith(".json") and os.path.isfile(os.path.join(self.path, f))
            ]
            files.sort(key=lambda f: os.path.getmtime(os.path.join(self.path, f)), reverse=True)
            for f in files:
                self.items.append(os.path.join(self.path, f))
                self.listbox.insert("end", f)
        else:
            dirs = [
                d for d in entries
                if os.path.isdir(os.path.join(self.path, d))
            ]
            dirs.sort()
            for d in dirs:
                self.items.append(os.path.join(self.path, d))
                self.listbox.insert("end", d)
        self.detail.configure(text="")

    def _selected_path(self):
        sel = self.listbox.curselection()
        if not sel:
            return None
        return self.items[sel[0]]

    def update_detail(self, _event=None):
        path = self._selected_path()
        if not path:
            self.detail.configure(text="")
            return
        if self.mode == "volumes":
            try:
                import json
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                summary = data.get("summary", {})
                text = (
                    f"Volume: {summary.get('volume_m3', 0):.6f} m³\n"
                    f"Litros: {summary.get('volume_liters', 0):.2f} L\n"
                    f"Método: {summary.get('method', '')}\n"
                    f"Escala: {summary.get('scale', 0):.6f}"
                )
            except Exception:
                text = os.path.basename(path)
        else:
            text = os.path.basename(path)
        self.detail.configure(text=text)

    def open_selected(self):
        path = self._selected_path()
        if not path:
            messagebox.showerror("Seleção inválida", "Selecione um item.", parent=self)
            return
        if self.mode == "volumes" and path.lower().endswith(".json"):
            md = os.path.splitext(path)[0] + ".md"
            if os.path.exists(md):
                _open_path(md)
                return
        _open_path(path)

    def open_folder(self):
        _open_path(self.path)

    def delete_selected(self):
        path = self._selected_path()
        if not path:
            messagebox.showerror("Seleção inválida", "Selecione um item.", parent=self)
            return
        name = os.path.basename(path)
        if not messagebox.askyesno(
            "Confirmar exclusão",
            f"Tem certeza que deseja excluir:\n{name}\n\nEssa ação não pode ser desfeita.",
            parent=self,
        ):
            return
        try:
            if self.mode == "volumes":
                os.remove(path)
            else:
                shutil.rmtree(path)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Erro ao excluir", str(exc), parent=self)

def build_ui():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Análise Volumétrica 3D")
    root.configure(fg_color=BG)
    _center_window(root, 900, 600)

    font_name = _pick_font()

    header = ctk.CTkFrame(root, fg_color="transparent")
    header.pack(pady=(30, 10))

    title = ctk.CTkLabel(
        header,
        text="Análise Volumétrica 3D",
        font=ctk.CTkFont(family=font_name, size=24, weight="bold"),
        text_color=TEXT_PRIMARY,
    )
    title.pack()

    subtitle = ctk.CTkLabel(
        header,
        text="Siga os passos abaixo para processar seu vídeo e calcular o volume",
        font=ctk.CTkFont(family=font_name, size=14),
        text_color=TEXT_SECONDARY,
    )
    subtitle.pack(pady=(6, 0))

    tabs = ctk.CTkTabview(root, fg_color="transparent")
    tabs.pack(fill="both", expand=True, padx=32, pady=(10, 20))

    tab_process = tabs.add("Processo")
    tab_history = tabs.add("Histórico")
    tab_about = tabs.add("Sobre")

    content = ctk.CTkFrame(tab_process, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=8, pady=10)

    cfg = load_config()

    def run_task(task_fn):
        try:
            task_fn(cfg, parent=root)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    steps = [
        ("Extrair Frames", "Extrair frames do vídeo para análise", "🎞️", run_opencv_module),
        ("Reconstruir 3D", "Gerar malha 3D usando COLMAP e MVS", "🧩", run_reconstruction_module),
        ("Calcular Volume", "Calcular volume final do objeto em m³", "📦", run_volume_module),
    ]

    for idx, (title, subtitle, icon, fn) in enumerate(steps, start=1):
        card = StepCard(
            content,
            step=idx,
            title=title,
            subtitle=subtitle,
            color=STEP_COLORS[idx - 1],
            icon=icon,
            command=lambda f=fn: run_task(f),
        )
        card.pack(fill="x", pady=10)

    history_wrap = ctk.CTkScrollableFrame(tab_history, fg_color="transparent")
    history_wrap.pack(fill="both", expand=True, padx=8, pady=10)
    history_wrap.grid_columnconfigure((0, 1), weight=1)

    history_items = [
        ("Reconstruções", "Projetos gerados pelo COLMAP", _resolve_path(cfg["paths"]["colmap_output"]), "dir"),
        ("Frames", "Pastas de frames extraídos", _resolve_path(cfg["paths"]["frames_output"]), "dir"),
        ("Volumes", "Relatórios e resultados de volume", _resolve_path(cfg["paths"]["volumes_output"]), "volumes"),
    ]

    for idx, (title, subtitle, path, mode) in enumerate(history_items):
        panel = HistoryPanel(history_wrap, title, subtitle, path, mode=mode)
        row = idx // 2
        col = idx % 2
        panel.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    about_frame = ctk.CTkFrame(tab_about, fg_color="transparent")
    about_frame.pack(fill="both", expand=True, padx=20, pady=20)

    about_title = ctk.CTkLabel(
        about_frame,
        text="Sobre o Sistema",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=TEXT_PRIMARY,
    )
    about_title.pack(pady=(10, 6))
    about_text = (
        "Este aplicativo foi desenvolvido para analise volumetrica 3D a partir de videos.\n\n"
        "Fluxo recomendado:\n"
        "1) Extrair frames\n"
        "2) Reconstruir 3D\n"
        "3) Calcular volume\n\n"
        "O sistema suporta escala manual, ArUco, folha A4, volume por altura e deteccao de formas regulares."
    )

    about_label = ctk.CTkLabel(
        about_frame,
        text=about_text,
        font=ctk.CTkFont(size=12),
        text_color=TEXT_SECONDARY,
        justify="left",
    )
    about_label.pack(pady=(0, 10))

    return root


def main():
    app = build_ui()
    app.mainloop()


if __name__ == "__main__":
    main()

