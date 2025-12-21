import subprocess
import os

# Converte caminhos Windows para formato universal com /
def normalize_path(path: str) -> str:
    return path.replace("\\", "/")

def run_cmd(cmd):
    """Executa um comando no terminal e verifica se há erros."""
    print(f"[RUN] {cmd}")
    # O shell=True é usado para que o f-string seja interpretado como um comando único.
    subprocess.run(cmd, shell=True, check=True)

def run_colmap_reconstruction(image_dir, output_dir, resources_dir):
    """
    Executa o pipeline completo de reconstrução 3D do COLMAP.
    """
    print("\n========= COMEÇANDO RECONSTRUÇÃO COM O COLMAP =========\n")

    image_dir = normalize_path(image_dir)
    output_dir = normalize_path(output_dir)
    resources_dir = normalize_path(resources_dir)

    # Define os caminhos de saída
    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    os.makedirs(sparse_dir, exist_ok=True)

    dense_dir = os.path.join(output_dir, "dense")
    os.makedirs(dense_dir, exist_ok=True)

    database_path = normalize_path(os.path.join(output_dir, "database.db"))

    # ----------------------------------------------------
    # 1. Feature extractor (Extração de Features)
    #    -> Usando CPU (use_gpu 0) para evitar o erro de driver CUDA.
    # ----------------------------------------------------
    run_cmd(
        f"colmap feature_extractor "
        f"--database_path {database_path} "
        f"--image_path {image_dir} "
        f"--SiftExtraction.use_gpu 0 "
        f"--SiftExtraction.num_threads 8"
    )

    # ----------------------------------------------------
    # 2. Match features (Correspondência Exaustiva)
    #    -> Usando CPU (use_gpu 0).
    # ----------------------------------------------------
    run_cmd(
        f"colmap exhaustive_matcher "
        f"--database_path {database_path} "
        f"--SiftMatching.use_gpu 0 "
    )

    # ----------------------------------------------------
    # 3. Sparse reconstruction (Mapeamento Esparso)
    # ----------------------------------------------------
    run_cmd(
        f"colmap mapper "
        f"--database_path {database_path} "
        f"--image_path {image_dir} "
        f"--output_path {sparse_dir}"
    )

    # ----------------------------------------------------
    # 4. Undistort images for dense (Remoção de Distorção)
    #    -> Preparação obrigatória para a reconstrução densa.
    # ----------------------------------------------------
    run_cmd(
        f"colmap image_undistorter "
        f"--image_path {image_dir} "
        f"--input_path {sparse_dir}/0 "
        f"--output_path {dense_dir} "
        f"--output_type COLMAP "
        f"--max_image_size 4000"
    )

    # ----------------------------------------------------
    # 5. Patch-match stereo (Reconstrução Densa - Step 1)
    #    -> Gera mapas de profundidade.
    # ----------------------------------------------------
    run_cmd(
        f"colmap patch_match_stereo "
        f"--workspace_path {dense_dir}"
        # Parâmetros opcionais (comuns para aumentar a qualidade, mas demoram):
        # f" --PatchMatchStereo.max_image_size 2000 "
        # f" --PatchMatchStereo.window_radius 5 "
    )

    # ----------------------------------------------------
    # 6. Stereo fusion (Fusão Estéreo)
    #    -> Combina mapas de profundidade em uma Nuvem de Pontos Densa (.PLY).
    # ----------------------------------------------------
    fused_ply_path = os.path.join(dense_dir, "fused.ply")
    run_cmd(
        f"colmap stereo_fusion "
        f"--workspace_path {dense_dir} "
        f"--output_path {fused_ply_path}"
    )

    # ----------------------------------------------------
    # 7. Poisson Mesher (Malha 3D Final)
    #    -> Cria uma malha de superfície a partir da nuvem de pontos densa.
    # ----------------------------------------------------
    meshed_ply_path = os.path.join(dense_dir, "meshed_poisson.ply")
    if os.path.exists(fused_ply_path):
        run_cmd(
            f"colmap poisson_mesher "
            f"--input_path {fused_ply_path} "
            f"--output_path {meshed_ply_path}"
            # f" --PoissonMesher.depth 8 " # Parâmetro comum (controla a resolução da malha)
        )
    else:
        print("AVISO: Não foi possível rodar o Poisson Mesher, pois 'fused.ply' não foi encontrado.")

    print("\n========= RECONSTRUÇÃO FINALIZADA =========\n")