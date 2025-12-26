import cv2
import numpy as np
from tqdm import tqdm
import os


class acquisition:

    @staticmethod
    def save_video_frames_fps(video_path, output_dir, desired_fps):
        """Salva frames do vídeo, ajustando para um FPS desejado."""
        print("Começando extração de frames do video:\n")

        cap = cv2.VideoCapture(video_path)
        fps = acquisition.get_video_frame_rate(cap)

        if not cap.isOpened():
            print("Não foi possivel abrir o arquivo do video:", video_path)
            return

        # 1. Obter o número total de frames para o tqdm
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        frame_number = 1

        # Garante que 'rate' seja pelo menos 1 para evitar divisão por zero ou saltos inválidos
        if desired_fps <= 0:
            print("Desired FPS não pode ser 0.")
            return
        rate = max(1, int(fps / desired_fps))  # Calcula o fator de salto

        os.makedirs(output_dir, exist_ok=True)

        # 2. Usar tqdm para iterar em todos os frames
        for cont_frame in tqdm(range(total_frames), desc=f"Extracting Frames (Target FPS: {desired_fps})"):
            ret, frame = cap.read()
            if not ret:
                break

            if cont_frame % rate == 0:
                filename = f"{output_dir}/{base_name}_{frame_number:03d}.png"
                cv2.imwrite(filename, frame)
                frame_number += 1

        print(" \nFrames salvos em:", output_dir)
        print(" Extração de Frames finalizada. ")

    @staticmethod
    def get_video_frame_rate(video_capture_or_path):
        if isinstance(video_capture_or_path, str):
            cap = cv2.VideoCapture(video_capture_or_path)
            if not cap.isOpened():
                # print("It's not possible to open the video:", video_capture_or_path)
                return 0.0
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()  # Liberar o recurso se abriu
            return fps

        else:
            return video_capture_or_path.get(cv2.CAP_PROP_FPS)