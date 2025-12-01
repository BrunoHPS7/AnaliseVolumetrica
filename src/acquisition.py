import cv2
import numpy as np
from tqdm import tqdm
import os

"""
Módulo: acquisition
Responsabilidade:
    - Extrair frames do vídeo de entrada (MP4/AVI).
    - Calibrar os parâmetros intrínsecos da câmera.
    - Gerar e salvar a matriz K.
    - Armazenar frames e metadados em diretórios apropriados.
"""

class acquisition:

    @staticmethod
    def main_tests():
        image = cv2.imread("../data/in/images/simprao.jpg")
        if image is None:
            print("Could not open or find the image!")
            return

        cv2.imshow("Sample Image", image)
        cv2.waitKey(10000)
        cv2.destroyAllWindows()

    @staticmethod
    def camera_matrix_manipulations():
        camera_matrix = np.eye(4, dtype=np.float32)
        X = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        x = camera_matrix @ X
        print("x:", x)

    @staticmethod
    def save_video_frames(video_path, output_dir):
        print("************************************************")
        print(" Starting framing the video ")
        print("************************************************")

        cap = cv2.VideoCapture(video_path)
        fps = acquisition.get_video_frame_rate(cap)

        if not cap.isOpened():
            print("Not possible to open the video file:", video_path)
            return

        base_name = os.path.splitext(os.path.basename(video_path))[0]

        frame_number = 1
        cont_frame = 0

        os.makedirs(output_dir, exist_ok=True)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if cont_frame % 2 == 0:
                filename = f"{output_dir}/{base_name}_{frame_number:03d}.png"
                cv2.imwrite(filename, frame)
                frame_number += 1
                print("*", end="", flush=True)

            cont_frame += 1

        print("\n************************************************")
        print(" Frames saved in:", output_dir)
        print(" Ending framing the video ")
        print("************************************************")

    @staticmethod
    def save_video_frames_fps(video_path, output_dir, desired_fps):
        print("************************************************")
        print(" Starting framing the video ")
        print("************************************************")

        cap = cv2.VideoCapture(video_path)
        fps = acquisition.get_video_frame_rate(cap)

        if not cap.isOpened():
            print("Not possible to open the video file:", video_path)
            return

        base_name = os.path.splitext(os.path.basename(video_path))[0]

        frame_number = 1
        cont_frame = 0

        rate = int(fps / desired_fps)

        os.makedirs(output_dir, exist_ok=True)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if cont_frame % rate == 0:
                filename = f"{output_dir}/{base_name}_{frame_number:03d}.png"
                cv2.imwrite(filename, frame)
                frame_number += 1
                print("*", end="", flush=True)

            cont_frame += 1

        print("\n************************************************")
        print(" Frames saved in:", output_dir)
        print(" Ending framing the video ")
        print("************************************************")

    @staticmethod
    def get_video_frame_rate(video_capture_or_path):
        if isinstance(video_capture_or_path, str):
            cap = cv2.VideoCapture(video_capture_or_path)
            if not cap.isOpened():
                print("It's not possible to open the video:", video_capture_or_path)
                return 0.0
            return cap.get(cv2.CAP_PROP_FPS)

        else:
            return video_capture_or_path.get(cv2.CAP_PROP_FPS)
