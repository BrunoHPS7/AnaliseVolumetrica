import cv2
import numpy as np
from tqdm import tqdm
import os


# Obter nome da pasta onde os frames da execução serão salvos:
def obter_pasta_projeto(pasta_base_frames):
    # Garante existencia do path
    if not os.path.exists(pasta_base_frames):
        os.makedirs(pasta_base_frames)
        print(f"Pasta base criada: {pasta_base_frames}")

    # Captura o nome da pasta
    while True:
        nome_projeto = input("\nDigite o nome para este conjunto de frames (ex: clio_teste): ").strip()

        if not nome_projeto:
            print("O nome não pode ser vazio.")
            continue

        # Define o caminho da subpasta: data/out/frames/nome_projeto
        caminho_subpasta = os.path.join(pasta_base_frames, nome_projeto)

        if os.path.exists(caminho_subpasta):
            print(f"A pasta '{nome_projeto}' já existe em {pasta_base_frames}. Escolha outro nome.")
            # Lista pastas existentes para ajudar
            existentes = [d for d in os.listdir(pasta_base_frames) if
                          os.path.isdir(os.path.join(pasta_base_frames, d))]
            print("Projetos já existentes:", existentes)
        else:
            os.makedirs(caminho_subpasta)
            return caminho_subpasta, nome_projeto


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
    """Salva frames do vídeo criando uma subpasta e renomeando arquivos conforme o projeto."""

    # 1. Validação inicial do vídeo
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Erro: Não foi possível abrir o arquivo de vídeo em: {video_path}")
        return

    fps_original = get_video_frame_rate(cap)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 2. Pergunta o nome e prepara os caminhos (Sistema padronizado)
    pasta_final, nome_projeto = obter_pasta_projeto(output_dir)

    print(f"Processando...")

    # 3. Lógica de amostragem (FPS)
    if desired_fps <= 0:
        print("Erro: Desired FPS deve ser maior que 0.")
        return

    rate = max(1, int(fps_original / desired_fps))
    frame_number = 1

    # 4. Extração com barra de progresso
    for cont_frame in tqdm(range(total_frames), desc="Extraindo Frames"):
        ret, frame = cap.read()
        if not ret:
            break

        if cont_frame % rate == 0:
            # Nome do arquivo conforme solicitado: nomeProjeto_numero.png
            filename = f"{nome_projeto}_{frame_number:03d}.png"
            caminho_arquivo = os.path.join(pasta_final, filename)

            cv2.imwrite(caminho_arquivo, frame)
            frame_number += 1

    cap.release()

    print("Extração de Frames finalizada.")
    print(f"Frames salvos com sucesso em: {pasta_final}")