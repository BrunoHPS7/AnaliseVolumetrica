import cv2
import numpy as np
import glob
import os


def obter_caminho_saida(pasta_destino):
    """
    Pergunta ao usuário o nome do arquivo e garante que ele não sobrescreva nada.
    """
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f"Pasta criada: {pasta_destino}")

    while True:
        nome_arquivo = input("\nDigite o nome para o arquivo de calibração (ex: calib_camera1.npz): ").strip()

        # Garante que tenha a extensão .npz
        if not nome_arquivo.endswith('.npz'):
            nome_arquivo += '.npz'

        caminho_completo = os.path.join(pasta_destino, nome_arquivo)

        if os.path.exists(caminho_completo):
            print(f"O arquivo '{nome_arquivo}' já existe em {pasta_destino}. Escolha outro nome.")
            # Opcional: listar arquivos para ajudar o usuário
            print("\nArquivos na pasta: ", os.listdir(pasta_destino))
        else:
            return caminho_completo


def run_calibration_process(settings: dict):
    chessboard_size = settings["checkerboard_size"]
    square_size = settings["square_size"]
    image_folder = settings["calibration_folder"]
    output_folder = settings["output_folder"]

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Preparação dos Pontos
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp = objp * square_size

    objpoints = []
    imgpoints = []

    # Busca imagens
    image_paths = []
    for ext in ('*.jpg', '*.jpeg', '*.png'):
        image_paths.extend(glob.glob(os.path.join(image_folder, ext)))

    if not image_paths:
        print(f"Erro: Nenhuma imagem encontrada em: {os.path.abspath(image_folder)}")
        return

    print(f"Processando...")

    gray = None
    for fname in image_paths:
        img = cv2.imread(fname)
        if img is None: continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

    if not objpoints:
        print("Falha: O tabuleiro não foi detectado em nenhuma imagem.")
        return

    # Calibração Matemática
    print("Calculando matrizes...")
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    if ret:
        print("Calibração bem sucedida!")

        # Define onde salvar perguntando ao usuário
        caminho_final = obter_caminho_saida(output_folder)

        # Salva os dados reais
        np.savez(caminho_final, mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

        print(f"Resultado salvo com sucesso em: {caminho_final}")
    else:
        print("Erro matemático na calibração.")