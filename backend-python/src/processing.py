from typing import Optional, Tuple, Dict, Union
import numpy as np
import trimesh
import open3d as o3d

"""
Módulo: processing
Responsabilidade:
    - Carregar uma malha 3D (triângulos).
    - Aplicar escala com base em um segmento conhecido.
    - Garantir malha fechada quando possível.
    - Calcular volume do objeto.
"""


def load_mesh(mesh_path: str) -> trimesh.Trimesh:
    mesh = trimesh.load(mesh_path, force="mesh")
    if isinstance(mesh, trimesh.Scene):
        geometries = list(mesh.geometry.values())
        if not geometries:
            raise ValueError("Nenhuma geometria encontrada no arquivo.")
        mesh = trimesh.util.concatenate(geometries)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError("Arquivo não contém uma malha triangular válida.")
    if mesh.is_empty:
        raise ValueError("Malha vazia.")
    return mesh


def generate_mesh_from_dense_point_cloud(
    dense_ply_path: str,
    output_ply_path: str,
    output_stl_path: Optional[str] = None,
    poisson_depth: int = 9,
    density_quantile: float = 0.01,
) -> Dict[str, Union[str, int, float]]:
    pcd = o3d.io.read_point_cloud(dense_ply_path)
    if pcd.is_empty():
        raise ValueError("Nuvem de pontos densa vazia ou inválida.")

    pcd.estimate_normals()
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=poisson_depth
    )

    if density_quantile is not None:
        dens = np.asarray(densities)
        threshold = np.quantile(dens, density_quantile)
        vertices_to_remove = dens < threshold
        mesh.remove_vertices_by_mask(vertices_to_remove)

    bbox = pcd.get_axis_aligned_bounding_box()
    mesh = mesh.crop(bbox)
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    mesh.remove_unreferenced_vertices()

    o3d.io.write_triangle_mesh(output_ply_path, mesh)
    if output_stl_path:
        o3d.io.write_triangle_mesh(output_stl_path, mesh)

    return {
        "output_ply": output_ply_path,
        "output_stl": output_stl_path or "",
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.triangles)),
    }


def compute_segment_scale(
    p1: np.ndarray,
    p2: np.ndarray,
    real_distance: float,
) -> float:
    if real_distance <= 0:
        raise ValueError("real_distance deve ser > 0.")
    dist_mesh = float(np.linalg.norm(p2 - p1))
    if dist_mesh == 0:
        raise ValueError("Segmento com distância zero.")
    return real_distance / dist_mesh


def scale_mesh(mesh: trimesh.Trimesh, scale: float) -> trimesh.Trimesh:
    if scale <= 0:
        raise ValueError("scale deve ser > 0.")
    mesh = mesh.copy()
    mesh.apply_scale(scale)
    return mesh


def try_make_watertight(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mesh = mesh.copy()

    # Remove faces degeneradas (área zero)
    try:
        mesh.update_faces(mesh.nondegenerate_faces())
    except Exception:
        pass

    # Remove faces duplicadas
    try:
        mesh.update_faces(mesh.unique_faces())
    except Exception:
        pass

    # Remove vértices não referenciados
    try:
        mesh.remove_unreferenced_vertices()
    except Exception:
        pass

    # Preenche buracos
    try:
        trimesh.repair.fill_holes(mesh)
    except Exception:
        pass

    return mesh


def compute_volume(
    mesh: trimesh.Trimesh,
    voxel_pitch: Optional[float] = None,
) -> Tuple[float, str]:
    # Tenta usar volume direto da malha (mais preciso)
    try:
        vol = float(mesh.volume)
        if np.isfinite(vol) and vol > 0:
            return vol, "mesh"
    except Exception:
        pass

    # Tenta reparar e calcular
    repaired = try_make_watertight(mesh)
    try:
        vol = float(repaired.volume)
        if np.isfinite(vol) and vol > 0:
            return vol, "mesh_repaired"
    except Exception:
        pass

    # Fallback: voxelização (menos preciso)
    if voxel_pitch is None:
        bbox_max = float(np.max(repaired.extents))
        voxel_pitch = max(bbox_max / 200.0, 1e-6)

    vox = repaired.voxelized(pitch=voxel_pitch).fill()
    return float(vox.volume), "voxel"


def compute_volume_from_mesh(
    mesh_path: str,
    scale: Optional[float] = None,
    segment_p1: Optional[np.ndarray] = None,
    segment_p2: Optional[np.ndarray] = None,
    real_distance: Optional[float] = None,
    input_unit: str = "m",
    output_unit: str = "m3",
    voxel_pitch: Optional[float] = None,
    export_stl_path: Optional[str] = None,
) -> Dict[str, Union[float, str]]:
    mesh = load_mesh(mesh_path)

    if scale is None:
        if segment_p1 is None or segment_p2 is None or real_distance is None:
            raise ValueError("Informe scale ou (segment_p1, segment_p2, real_distance).")
        unit_scale = {"m": 1.0, "cm": 0.01, "mm": 0.001}
        if input_unit not in unit_scale:
            raise ValueError("input_unit inválido (use m, cm ou mm).")
        real_distance_m = real_distance * unit_scale[input_unit]
        scale = compute_segment_scale(segment_p1, segment_p2, real_distance_m)

    mesh = scale_mesh(mesh, scale)

    if export_stl_path:
        mesh.export(export_stl_path)

    volume_m3, method = compute_volume(mesh, voxel_pitch=voxel_pitch)
    if output_unit == "m3":
        volume_out = volume_m3
    elif output_unit == "cm3":
        volume_out = volume_m3 * 1e6
    elif output_unit == "mm3":
        volume_out = volume_m3 * 1e9
    else:
        raise ValueError("output_unit inválido (use m3, cm3 ou mm3).")

    return {
        "volume": volume_out,
        "unit": output_unit,
        "method": method,
        "scale": scale,
    }
