from typing import Any
import cv2
import numpy as np
import glob
import os


# function to calibrate the camera
def calibrate_camera_from_images(Settings: dict) -> tuple[Any,Any,Any,Any]:
    """
    Calibrates the camera from a folder of chessboard images.

    Args:
        chessboard_size (tuple): The number of inner corners of the chessboard (width, height).
        square_size (float): The size of each square on the chessboard in units (e.g., mm).

    Returns:
        tuple: A tuple containing the camera matrix, distortion coefficients,
               rotation vectors, and translation vectors.
               Returns None if calibration fails.
               :param Settings:
    """
    chessboard_size = Settings["checkerboard size"]
    square_size = Settings["square size"]
    # define the termination criteria for the calibration
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), ..., (width-1,height-1,0)
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp = objp * square_size  # aplica o tamanho real do quadrado

    # Arrays to store object points and image points from all images
    objpoints = []  # 3d points in real world space
    imgpoints = []  # 2d points in image plane

    # Substitui a leitura de vídeo pela leitura de imagens da pasta 'fotosCalibration'
    image_folder = Settings["calibration folder"]  # nome da pasta onde estão as imagens
    image_paths = []
    for ext in ('*.jpg', '*.jpeg', '*.png'):
        image_paths.extend(glob.glob(os.path.join(image_folder, ext)))

    print(f"{len(image_paths)} imagens encontradas para calibração.")

    # >>> Novo loop: percorre todas as imagens coletadas da pasta
    for fname in image_paths:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # encontrar cantos do tabuleiro de xadrez
        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)

            # opcional: mostrar imagem com cantos detectados
            cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
            cv2.imshow('Cantos Detectados', img)
            cv2.waitKey(300)
        else:
            print(f"Falha ao detectar cantos em {fname}")

    cv2.destroyAllWindows()

    if len(objpoints) == 0:
        print("Nenhuma imagem válida para calibração. Processo cancelado.")
        return None

    # Calibrar a câmera
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    if ret:
        print("\nCalibração concluída com sucesso.")
        print("Matriz da câmera:\n", mtx)
        print("Coeficientes de distorção:\n", dist)
        return mtx, dist, rvecs, tvecs
    else:
        print("Falha na calibração.")
        return None

# >>> Exemplo de uso:
# Substitua (22, 15) pelo número de cantos internos do seu tabuleiro
# Substitua 25.0 pelo tamanho real de cada quadrado, se quiser
# calibration_result = calibrate_camera_from_images((22, 15), 25.0)
# if calibration_result:
#     camera_matrix, dist_coeffs, rvecs, tvecs = calibration_result