import subprocess
import os

def run_cmd(cmd):
    print(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def run_colmap_reconstruction(image_dir, output_dir, resources_dir):
    print("\n========= COMEÇANDO RECONSTRUÇÃO COM O COLMAP =========\n")

    database_path = os.path.join(output_dir, "database.db")
    sparse_dir = os.path.join(output_dir, "sparse")
    os.makedirs(sparse_dir, exist_ok=True)

    dense_dir = os.path.join(output_dir, "dense")
    os.makedirs(dense_dir, exist_ok=True)

    # 1. Extract features
    run_cmd(
        f"colmap feature_extractor "
        f"--database_path {database_path} "
        f"--image_path {image_dir} "
        f"--SiftExtraction.use_gpu 0 "
        f"--SiftExtraction.num_threads 8"
    )

    # 2. Match features
    run_cmd(
        f"colmap exhaustive_matcher "
        f"--database_path {database_path} "
        f"--SiftMatching.use_gpu 0 "
    )

    # 3. Sparse reconstruction
    run_cmd(
        f"colmap mapper "
        f"--database_path {database_path} "
        f"--image_path {image_dir} "
        f"--output_path {sparse_dir}"
    )

    # 4. Undistort images for dense
    run_cmd(
        f"colmap image_undistorter "
        f"--image_path {image_dir} "
        f"--input_path {sparse_dir}/0 "
        f"--output_path {dense_dir} "
        f"--output_type COLMAP "
        f"--max_image_size 4000"
    )

    # 5. Patch-match stereo
    run_cmd(
        f"colmap patch_match_stereo "
        f"--workspace_path {dense_dir}"
    )

    # 6. Merge into PLY mesh
    run_cmd(
        f"colmap stereo_fusion "
        f"--workspace_path {dense_dir} "
        f"--output_path {dense_dir}/fused.ply"
    )

    print("\n========= RECONSTRUÇÃO FINALIZADA =========\n")
