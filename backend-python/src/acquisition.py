import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, messagebox


# Extrai o frame do video
def get_video_frame_rate(video_capture_or_path):
    if isinstance(video_capture_or_path, str):
        cap = cv2.VideoCapture(video_capture_or_path)
        if not cap.isOpened():
            return 0.0
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return fps
    else:
        return video_capture_or_path.get(cv2.CAP_PROP_FPS)


# Controla o fluxo da extração e salvamento de frames
def save_video_frames_fps(video_path, output_dir, desired_fps):
    """Salva frames do vídeo na pasta enviada pelo main, com barra de progresso e aviso final em Tkinter."""

    # 1. Validação inicial do vídeo
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror("Erro", f"Não foi possível abrir o arquivo de vídeo em:\n{video_path}")
        root_err.destroy()
        return

    fps_original = get_video_frame_rate(cap)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 2. Prepara os caminhos
    nome_projeto = os.path.basename(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 3. Lógica de amostragem (FPS)
    if desired_fps <= 0:
        return

    rate = max(1, int(fps_original / desired_fps))
    frame_number = 1

    # JANELA DE PROGRESSO TKINTER
    root_pg = tk.Tk()
    root_pg.title("Processando Vídeo")
    root_pg.geometry("400x150")
    root_pg.attributes('-topmost', True)

    # Centralizar janela
    screen_width = root_pg.winfo_screenwidth()
    screen_height = root_pg.winfo_screenheight()
    x = (screen_width // 2) - (400 // 2)
    y = (screen_height // 2) - (150 // 2)
    root_pg.geometry(f"400x150+{x}+{y}")

    label = tk.Label(root_pg, text=f"Extraindo frames para o projeto:\n{nome_projeto}", pady=10)
    label.pack()

    progress = ttk.Progressbar(root_pg, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=5)
    progress["maximum"] = total_frames

    label_perc = tk.Label(root_pg, text="0%")
    label_perc.pack()

    # 4. Extração
    for cont_frame in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break

        if cont_frame % rate == 0:
            filename = f"{nome_projeto}_{frame_number:03d}.png"
            caminho_arquivo = os.path.join(output_dir, filename)
            cv2.imwrite(caminho_arquivo, frame)
            frame_number += 1

        # Atualiza a interface a cada 5 frames para performance
        if cont_frame % 5 == 0:
            progress["value"] = cont_frame
            porcentagem = int((cont_frame / total_frames) * 100)
            label_perc.config(text=f"{porcentagem}%")
            root_pg.update()

    cap.release()
    root_pg.destroy()  # Fecha a barra de progresso

    # AVISO DE FINALIZAÇÃO
    root_fin = tk.Tk()
    root_fin.withdraw()
    root_fin.attributes('-topmost', True)
    messagebox.showinfo("Sucesso", f"Extração de Frames finalizada!\n\nProjeto: {nome_projeto}\nLocal: {output_dir}")
    root_fin.destroy()