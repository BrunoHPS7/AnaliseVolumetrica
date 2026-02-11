from typing import Optional, Tuple, Dict, Union, List
import os
import numpy as np
import trimesh
import open3d as o3d
import cv2

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
    poisson_depth: int = 10,
    density_quantile: float = 0.005,
    remove_statistical_outliers: bool = True,
    stat_nb_neighbors: int = 20,
    stat_std_ratio: float = 2.0,
    remove_radius_outliers: bool = True,
    radius_nb_points: int = 16,
    radius_scale: float = 0.01,
    keep_largest_component: bool = True,
) -> Dict[str, Union[str, int, float]]:
    pcd = o3d.io.read_point_cloud(dense_ply_path)
    if pcd.is_empty():
        raise ValueError("Nuvem de pontos densa vazia ou inválida.")

    if remove_statistical_outliers:
        try:
            pcd, _ = pcd.remove_statistical_outlier(
                nb_neighbors=stat_nb_neighbors, std_ratio=stat_std_ratio
            )
        except Exception:
            pass
    if remove_radius_outliers and not pcd.is_empty():
        try:
            bbox = pcd.get_axis_aligned_bounding_box()
            diag = float(np.linalg.norm(bbox.get_extent()))
            radius = max(diag * radius_scale, 1e-6)
            pcd, _ = pcd.remove_radius_outlier(
                nb_points=radius_nb_points, radius=radius
            )
        except Exception:
            pass
    if pcd.is_empty():
        raise ValueError("Nuvem de pontos vazia após remoção de outliers.")

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
    if keep_largest_component and len(mesh.triangles) > 0:
        try:
            (
                triangle_clusters,
                cluster_n_triangles,
                _,
            ) = mesh.cluster_connected_triangles()
            if len(cluster_n_triangles) > 0:
                largest = int(np.argmax(cluster_n_triangles))
                mask = triangle_clusters != largest
                mesh.remove_triangles_by_mask(mask)
        except Exception:
            pass
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    mesh.remove_unreferenced_vertices()

    # Preenchimento mais agressivo via trimesh
    try:
        tm = trimesh.Trimesh(
            vertices=np.asarray(mesh.vertices),
            faces=np.asarray(mesh.triangles),
            process=False,
        )
        tm = try_make_watertight(tm, aggressive=True)
        if not tm.is_empty:
            mesh = o3d.geometry.TriangleMesh(
                o3d.utility.Vector3dVector(np.asarray(tm.vertices)),
                o3d.utility.Vector3iVector(np.asarray(tm.faces)),
            )
    except Exception:
        pass

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


def try_make_watertight(mesh: trimesh.Trimesh, aggressive: bool = False) -> trimesh.Trimesh:
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

    if aggressive:
        try:
            mesh.remove_degenerate_faces()
        except Exception:
            pass
        try:
            mesh.remove_duplicate_faces()
        except Exception:
            pass
        try:
            mesh.remove_unreferenced_vertices()
        except Exception:
            pass
        try:
            mesh.process(validate=True)
        except Exception:
            pass

    return mesh


def compute_volume(
    mesh: trimesh.Trimesh,
    voxel_pitch: Optional[float] = None,
) -> Tuple[float, str]:
    # Tenta usar volume direto da malha (mais preciso)
    try:
        if mesh.is_watertight:
            vol = float(mesh.volume)
            if np.isfinite(vol) and vol > 0:
                return vol, "mesh"
    except Exception:
        pass

    # Tenta reparar e calcular
    repaired = try_make_watertight(mesh, aggressive=True)
    try:
        if repaired.is_watertight:
            vol = float(repaired.volume)
            if np.isfinite(vol) and vol > 0:
                return vol, "mesh_repaired"
    except Exception:
        pass

    # Fallback: voxelização (garante volume fechado)
    if voxel_pitch is None:
        bbox_max = float(np.max(repaired.extents))
        voxel_pitch = max(bbox_max / 200.0, 1e-6)

    vox = repaired.voxelized(pitch=voxel_pitch).fill()
    return float(vox.volume), "voxel_watertight"


def _sample_points_for_heightmap(mesh: trimesh.Trimesh, min_points: int = 5000) -> np.ndarray:
    vertices = np.asarray(mesh.vertices)
    if len(vertices) >= min_points:
        return vertices
    if mesh.faces is None or len(mesh.faces) == 0:
        return vertices
    try:
        samples = mesh.sample(min_points)
        return np.asarray(samples)
    except Exception:
        return vertices


def compute_heightmap_volume(
    mesh: trimesh.Trimesh,
    grid_size: Optional[float] = None,
) -> Tuple[float, Dict[str, Union[float, int, List[float]]]]:
    points = _sample_points_for_heightmap(mesh)
    if points.size == 0:
        raise ValueError("Sem pontos para cálculo de altura.")

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    bbox = pcd.get_axis_aligned_bounding_box()
    diag = float(np.linalg.norm(bbox.get_extent()))
    distance_threshold = max(diag * 0.002, 1e-6)
    plane_model, inliers = pcd.segment_plane(
        distance_threshold=distance_threshold,
        ransac_n=3,
        num_iterations=1000,
    )
    min_inliers = max(500, int(len(points) * 0.05))
    if len(inliers) < min_inliers:
        raise ValueError("Plano da mesa não detectado com confiança.")

    normal = np.array(plane_model[:3], dtype=float)
    norm = float(np.linalg.norm(normal))
    if norm == 0:
        raise ValueError("Plano inválido para altura.")
    n = normal / norm
    d = float(plane_model[3]) / norm
    p0 = -d * n

    heights = (points - p0) @ n
    if np.median(heights) < 0:
        n = -n
        heights = -heights

    mask = heights > 0
    if not np.any(mask):
        raise ValueError("Nenhum ponto acima do plano.")
    points_above = points[mask]
    heights = heights[mask]

    helper = np.array([1.0, 0.0, 0.0], dtype=float)
    if abs(np.dot(helper, n)) > 0.9:
        helper = np.array([0.0, 1.0, 0.0], dtype=float)
    u = np.cross(n, helper)
    u_norm = float(np.linalg.norm(u))
    if u_norm == 0:
        raise ValueError("Plano inválido para altura.")
    u /= u_norm
    v = np.cross(n, u)

    coords = np.column_stack(((points_above - p0) @ u, (points_above - p0) @ v))
    min_xy = coords.min(axis=0)
    max_xy = coords.max(axis=0)
    extent = max_xy - min_xy
    if extent[0] <= 0 or extent[1] <= 0:
        raise ValueError("Extensão inválida para altura.")

    if grid_size is None:
        area = float(extent[0] * extent[1])
        spacing = np.sqrt(area / max(len(coords), 1))
        cell = max(spacing, 1e-6)
        width = int(extent[0] / cell) + 1
        height = int(extent[1] / cell) + 1
        max_dim = max(width, height)
        if max_dim > 1200:
            cell *= max_dim / 1200
        elif max_dim < 200:
            cell *= max_dim / 200
        grid_size = max(cell, 1e-6)

    width = int(extent[0] / grid_size) + 1
    height = int(extent[1] / grid_size) + 1

    xs = min_xy[0] + (np.arange(width) + 0.5) * grid_size
    ys = min_xy[1] + (np.arange(height) + 0.5) * grid_size
    xx, yy = np.meshgrid(xs, ys)
    origins = p0 + xx[..., None] * u + yy[..., None] * v

    max_height = float(np.max(heights))
    margin = max(grid_size * 2.0, max_height * 0.1)
    origins = origins + n * (max_height + margin)
    directions = np.tile(-n, (origins.shape[0], origins.shape[1], 1))

    legacy = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(np.asarray(mesh.vertices)),
        o3d.utility.Vector3iVector(np.asarray(mesh.faces)),
    )
    scene = o3d.t.geometry.RaycastingScene()
    tmesh = o3d.t.geometry.TriangleMesh.from_legacy(legacy)
    scene.add_triangles(tmesh)

    rays = np.hstack(
        [origins.reshape(-1, 3), directions.reshape(-1, 3)]
    ).astype(np.float32)
    hits = scene.cast_rays(o3d.core.Tensor(rays))
    t_hit = hits["t_hit"].numpy().reshape(height, width)

    height_grid = np.zeros((height, width), dtype=np.float32)
    hit_mask = np.isfinite(t_hit)
    height_grid[hit_mask] = (max_height + margin) - t_hit[hit_mask]
    height_grid = np.clip(height_grid, 0.0, None)

    volume = float(height_grid.sum() * (grid_size ** 2))
    return volume, {
        "grid_size": float(grid_size),
        "plane_model": [float(x) for x in plane_model],
        "points_used": int(len(points_above)),
    }


def _pca_basis(points: np.ndarray):
    center = points.mean(axis=0)
    centered = points - center
    cov = np.cov(centered, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    axes = eigvecs[:, order]
    return center, axes


def _fit_box(mesh: trimesh.Trimesh, points: np.ndarray) -> Optional[Dict[str, Union[float, List[float]]]]:
    try:
        obb = mesh.bounding_box_oriented
        extents = np.asarray(obb.primitive.extents, dtype=float)
        transform = np.linalg.inv(obb.primitive.transform)
    except Exception:
        return None
    if np.any(extents <= 0):
        return None
    local = trimesh.transform_points(points, transform)
    half = extents / 2.0
    abs_c = np.abs(local)
    delta = abs_c - half
    outside = np.maximum(delta, 0.0)
    outside_dist = np.linalg.norm(outside, axis=1)
    inside_dist = np.min(half - abs_c, axis=1)
    dist = np.where(np.any(delta > 0, axis=1), outside_dist, inside_dist)
    mean_dist = float(np.mean(np.abs(dist)))
    diag = float(np.linalg.norm(extents))
    rel_error = mean_dist / diag if diag > 0 else float("inf")
    volume = float(np.prod(extents))
    center = trimesh.transform_points([[0.0, 0.0, 0.0]], np.linalg.inv(transform))[0]
    return {
        "type": "box",
        "volume": volume,
        "rel_error": rel_error,
        "extents": extents.tolist(),
        "center": center.tolist(),
    }


def _fit_sphere(points: np.ndarray) -> Optional[Dict[str, Union[float, List[float]]]]:
    A = np.hstack((2.0 * points, np.ones((len(points), 1))))
    b = np.sum(points ** 2, axis=1)
    try:
        x, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    except Exception:
        return None
    center = x[:3]
    d = x[3]
    r2 = float(np.dot(center, center) + d)
    if r2 <= 0:
        return None
    r = float(np.sqrt(r2))
    distances = np.linalg.norm(points - center, axis=1)
    mean_dist = float(np.mean(np.abs(distances - r)))
    rel_error = mean_dist / r if r > 0 else float("inf")
    volume = float((4.0 / 3.0) * np.pi * r ** 3)
    return {
        "type": "sphere",
        "volume": volume,
        "rel_error": rel_error,
        "radius": r,
        "center": center.tolist(),
    }


def _fit_cylinder(points: np.ndarray, quantile: float = 0.02) -> Optional[Dict[str, Union[float, List[float]]]]:
    center, axes = _pca_basis(points)
    axis = axes[:, 0]
    z = (points - center) @ axis
    z_low = float(np.quantile(z, quantile))
    z_high = float(np.quantile(z, 1.0 - quantile))
    height = z_high - z_low
    if height <= 0:
        return None
    z_center = (z_high + z_low) / 2.0
    center = center + axis * z_center
    z = (points - center) @ axis
    radial_vec = points - center - np.outer(z, axis)
    radial = np.linalg.norm(radial_vec, axis=1)
    r = float(np.median(radial))
    if r <= 0:
        return None
    dx = radial - r
    dz = np.abs(z) - height / 2.0
    outside = np.stack([np.maximum(dx, 0.0), np.maximum(dz, 0.0)], axis=1)
    outside_dist = np.linalg.norm(outside, axis=1)
    inside_dist = np.minimum(-dx, -dz)
    dist = np.where((dx <= 0) & (dz <= 0), inside_dist, outside_dist)
    mean_dist = float(np.mean(np.abs(dist)))
    denom = max(r, height / 2.0)
    rel_error = mean_dist / denom if denom > 0 else float("inf")
    volume = float(np.pi * r ** 2 * height)
    return {
        "type": "cylinder",
        "volume": volume,
        "rel_error": rel_error,
        "radius": r,
        "height": height,
        "axis": axis.tolist(),
        "center": center.tolist(),
    }


def fit_primitive_volume(
    mesh: trimesh.Trimesh,
    max_rel_error: float = 0.02,
) -> Optional[Dict[str, Union[float, str, List[float]]]]:
    points = _sample_points_for_heightmap(mesh, min_points=8000)
    if points.size == 0:
        return None
    candidates = []
    box_fit = _fit_box(mesh, points)
    if box_fit:
        candidates.append(box_fit)
    sphere_fit = _fit_sphere(points)
    if sphere_fit:
        candidates.append(sphere_fit)
    cylinder_fit = _fit_cylinder(points)
    if cylinder_fit:
        candidates.append(cylinder_fit)
    if not candidates:
        return None
    candidates.sort(key=lambda c: c["rel_error"])
    best = candidates[0]
    if best["rel_error"] > max_rel_error:
        return None
    return best


def compute_volume_from_mesh(
    mesh_path: str,
    scale: Optional[float] = None,
    segment_p1: Optional[np.ndarray] = None,
    segment_p2: Optional[np.ndarray] = None,
    real_distance: Optional[float] = None,
    input_unit: str = "m",
    output_unit: str = "m3",
    volume_method: str = "auto",
    primitive_fit: bool = True,
    primitive_max_rel_error: float = 0.02,
    heightmap_grid_size: Optional[float] = None,
    voxel_pitch: Optional[float] = None,
    export_stl_path: Optional[str] = None,
) -> Dict[str, Union[float, str]]:
    heightmap_meta = None
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

    primitive_info = None

    if volume_method == "heightmap":
        volume_m3, heightmap_meta = compute_heightmap_volume(
            mesh, grid_size=heightmap_grid_size
        )
        method = "heightmap"
    else:
        if primitive_fit:
            primitive_info = fit_primitive_volume(
                mesh, max_rel_error=primitive_max_rel_error
            )
        if primitive_info:
            volume_m3 = float(primitive_info["volume"])
            method = f"primitive_{primitive_info['type']}"
        else:
            volume_m3, method = compute_volume(mesh, voxel_pitch=voxel_pitch)
    if output_unit == "m3":
        volume_out = volume_m3
    elif output_unit == "cm3":
        volume_out = volume_m3 * 1e6
    elif output_unit == "mm3":
        volume_out = volume_m3 * 1e9
    else:
        raise ValueError("output_unit inválido (use m3, cm3 ou mm3).")

    result = {
        "volume": volume_out,
        "unit": output_unit,
        "method": method,
        "scale": scale,
    }
    if volume_method == "heightmap" and heightmap_meta is not None:
        result["heightmap"] = heightmap_meta
    if primitive_info:
        result["primitive_fit"] = primitive_info
    return result


def _get_aruco_dictionary(name: str):
    if not hasattr(cv2, "aruco"):
        raise RuntimeError("OpenCV foi instalado sem o módulo aruco (opencv-contrib).")
    if not name.startswith("DICT_"):
        name = f"DICT_{name}"
    if not hasattr(cv2.aruco, name):
        raise ValueError(f"Dicionário ArUco inválido: {name}")
    return cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, name))


def _detect_markers(gray: np.ndarray, dictionary):
    if hasattr(cv2.aruco, "ArucoDetector"):
        params = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(dictionary, params)
        return detector.detectMarkers(gray)
    params = cv2.aruco.DetectorParameters_create()
    return cv2.aruco.detectMarkers(gray, dictionary, parameters=params)


def _refine_corners_subpix(gray: np.ndarray, corners: np.ndarray) -> np.ndarray:
    if corners.size == 0:
        return corners
    if gray.dtype != np.uint8:
        gray = (gray.clip(0, 255)).astype(np.uint8)
    refined = corners.astype(np.float32).reshape(-1, 1, 2)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    try:
        cv2.cornerSubPix(gray, refined, (5, 5), (-1, -1), criteria)
    except Exception:
        return corners
    return refined.reshape(-1, 2)


def _point_cloud_from_mesh(mesh_path: str) -> Optional[o3d.geometry.PointCloud]:
    mesh = o3d.io.read_triangle_mesh(mesh_path, enable_post_processing=True)
    if mesh.is_empty():
        return None
    if len(mesh.vertex_colors) == 0:
        return None
    pcd = o3d.geometry.PointCloud()
    pcd.points = mesh.vertices
    pcd.colors = mesh.vertex_colors
    return pcd


def _load_colored_point_cloud(mesh_path: str) -> Tuple[o3d.geometry.PointCloud, str]:
    pcd = _point_cloud_from_mesh(mesh_path)
    if pcd is not None and not pcd.is_empty() and pcd.has_colors():
        return pcd, mesh_path

    pcd = o3d.io.read_point_cloud(mesh_path)
    if not pcd.is_empty() and pcd.has_colors():
        return pcd, mesh_path

    candidate = os.path.join(os.path.dirname(mesh_path), "fused.ply")
    if os.path.exists(candidate):
        pcd = o3d.io.read_point_cloud(candidate)
        if not pcd.is_empty() and pcd.has_colors():
            return pcd, candidate

    raise ValueError(
        "Não foi possível obter cores para detectar o ArUco. "
        "Use uma malha .ply com cores ou garanta que exista fused.ply na pasta."
    )


def _plane_basis(plane_model: List[float]):
    normal = np.array(plane_model[:3], dtype=float)
    norm = float(np.linalg.norm(normal))
    if norm == 0:
        raise ValueError("Plano inválido para projeção.")
    n = normal / norm
    d = float(plane_model[3]) / norm
    p0 = -d * n
    helper = np.array([1.0, 0.0, 0.0], dtype=float)
    if abs(np.dot(helper, n)) > 0.9:
        helper = np.array([0.0, 1.0, 0.0], dtype=float)
    u = np.cross(n, helper)
    u_norm = float(np.linalg.norm(u))
    if u_norm == 0:
        raise ValueError("Plano inválido para projeção.")
    u /= u_norm
    v = np.cross(n, u)
    return p0, u, v


def _rasterize_plane_points(
    points: np.ndarray,
    colors: np.ndarray,
    p0: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    min_dim_px: int = 400,
    max_dim_px: int = 1600,
) -> Tuple[np.ndarray, float, float, float, float]:
    vectors = points - p0
    coords = np.column_stack((vectors @ u, vectors @ v))
    min_xy = coords.min(axis=0)
    max_xy = coords.max(axis=0)
    extent = max_xy - min_xy
    if extent[0] <= 0 or extent[1] <= 0:
        raise ValueError("Projeção inválida do plano.")
    area = float(extent[0] * extent[1])
    spacing = np.sqrt(area / max(len(coords), 1))
    pixel_size = max(spacing, 1e-6)

    width = int(extent[0] / pixel_size) + 1
    height = int(extent[1] / pixel_size) + 1
    max_dim = max(width, height)
    scale = 1.0
    if max_dim > max_dim_px:
        scale = max_dim_px / max_dim
    elif max_dim < min_dim_px:
        scale = min_dim_px / max_dim

    px = np.floor((coords[:, 0] - min_xy[0]) / pixel_size).astype(int)
    py = np.floor((coords[:, 1] - min_xy[1]) / pixel_size).astype(int)
    mask = (px >= 0) & (px < width) & (py >= 0) & (py < height)
    px = px[mask]
    py = py[mask]
    col = colors[mask]

    if col.max() > 1.0:
        col = col / 255.0

    img_sum = np.zeros((height, width, 3), dtype=np.float32)
    img_count = np.zeros((height, width), dtype=np.int32)
    np.add.at(img_sum, (py, px), col)
    np.add.at(img_count, (py, px), 1)

    img = np.ones((height, width, 3), dtype=np.float32)
    filled = img_count > 0
    img[filled] = img_sum[filled] / img_count[filled][:, None]
    img_uint8 = (img * 255.0).clip(0, 255).astype(np.uint8)
    if scale != 1.0:
        new_w = max(1, int(round(width * scale)))
        new_h = max(1, int(round(height * scale)))
        img_uint8 = cv2.resize(img_uint8, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
        pixel_size /= scale
    return img_uint8, float(min_xy[0]), float(min_xy[1]), float(pixel_size), float(pixel_size)


def _order_quad_corners(corners: np.ndarray) -> np.ndarray:
    corners = corners.reshape(4, 2)
    s = corners.sum(axis=1)
    diff = np.diff(corners, axis=1).reshape(-1)
    ordered = np.zeros((4, 2), dtype=float)
    ordered[0] = corners[np.argmin(s)]  # top-left
    ordered[2] = corners[np.argmax(s)]  # bottom-right
    ordered[1] = corners[np.argmin(diff)]  # top-right
    ordered[3] = corners[np.argmax(diff)]  # bottom-left
    return ordered


def _detect_a4_corners(gray: np.ndarray) -> Optional[np.ndarray]:
    if gray.dtype != np.uint8:
        gray = (gray.clip(0, 255)).astype(np.uint8)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    v = np.median(blur)
    lower = int(max(0, 0.66 * v))
    upper = int(min(255, 1.33 * v))
    edges = cv2.Canny(blur, lower, upper)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    target_ratio = np.sqrt(2.0)
    best = None
    best_score = -1.0
    img_area = float(gray.shape[0] * gray.shape[1])

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        if peri <= 0:
            continue
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) != 4 or not cv2.isContourConvex(approx):
            continue
        area = float(cv2.contourArea(approx))
        if area < img_area * 0.02 or area > img_area * 0.95:
            continue
        corners = approx.reshape(4, 2).astype(float)
        ordered = _order_quad_corners(corners)
        edges_len = [
            float(np.linalg.norm(ordered[i] - ordered[(i + 1) % 4])) for i in range(4)
        ]
        if min(edges_len) <= 0:
            continue
        ratio = max(edges_len) / min(edges_len)
        if ratio < 1.30 or ratio > 1.55:
            continue
        ratio_score = 1.0 - abs(ratio - target_ratio) / 0.25
        score = area * max(ratio_score, 0.0)
        if score > best_score:
            best_score = score
            best = ordered

    return best


def compute_a4_scale_from_point_cloud(
    pcd: o3d.geometry.PointCloud,
    input_unit: str = "mm",
    max_planes: int = 4,
) -> Dict[str, Union[float, str, List[List[float]]]]:
    if pcd.is_empty():
        raise ValueError("Nuvem de pontos vazia.")
    if not pcd.has_colors():
        raise ValueError("Nuvem de pontos sem cores.")

    unit_scale = {"m": 1.0, "cm": 0.01, "mm": 0.001}
    if input_unit not in unit_scale:
        raise ValueError("input_unit inválido (use m, cm ou mm).")
    real_short_m = 210.0 * unit_scale[input_unit]
    real_long_m = 297.0 * unit_scale[input_unit]

    pcd_work = pcd
    bbox = pcd.get_axis_aligned_bounding_box()
    diag = float(np.linalg.norm(bbox.get_extent()))
    if len(pcd.points) > 400_000:
        voxel_size = max(diag / 500.0, 1e-6)
        pcd_work = pcd.voxel_down_sample(voxel_size)

    candidates = []
    pcd_iter = pcd_work
    for _ in range(max_planes):
        if len(pcd_iter.points) < 1000:
            break
        plane_model, inliers = pcd_iter.segment_plane(
            distance_threshold=max(diag * 0.002, 1e-6),
            ransac_n=3,
            num_iterations=1000,
        )
        if len(inliers) < 1000:
            break

        plane_pcd = pcd_iter.select_by_index(inliers)
        points = np.asarray(plane_pcd.points)
        colors = np.asarray(plane_pcd.colors)

        p0, u, v = _plane_basis(plane_model)
        img, min_x, min_y, px_size_x, _ = _rasterize_plane_points(
            points, colors, p0, u, v
        )
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        corners_px = _detect_a4_corners(gray)
        if corners_px is None:
            pcd_iter = pcd_iter.select_by_index(inliers, invert=True)
            continue

        corners_3d = []
        for px, py in corners_px:
            coord_x = min_x + (px + 0.5) * px_size_x
            coord_y = min_y + (py + 0.5) * px_size_x
            point_3d = p0 + coord_x * u + coord_y * v
            corners_3d.append(point_3d)
        corners_3d = np.array(corners_3d)

        edges = [
            float(np.linalg.norm(corners_3d[i] - corners_3d[(i + 1) % 4]))
            for i in range(4)
        ]
        edges_sorted = sorted(edges)
        short_mesh = float(np.mean(edges_sorted[:2]))
        long_mesh = float(np.mean(edges_sorted[2:]))
        if short_mesh <= 0 or long_mesh <= 0:
            pcd_iter = pcd_iter.select_by_index(inliers, invert=True)
            continue

        scale_short = real_short_m / short_mesh
        scale_long = real_long_m / long_mesh
        scale = (scale_short + scale_long) / 2.0
        consistency = abs(scale_short - scale_long) / max(scale, 1e-9)
        area_score = float(cv2.contourArea(corners_px.astype(np.float32)))
        candidates.append({
            "scale": float(scale),
            "short_mesh": short_mesh,
            "long_mesh": long_mesh,
            "short_m": float(real_short_m),
            "long_m": float(real_long_m),
            "corners_3d": corners_3d.tolist(),
            "consistency": float(consistency),
            "area_score": area_score,
        })

        pcd_iter = pcd_iter.select_by_index(inliers, invert=True)

    if not candidates:
        raise ValueError("Folha A4 não detectada no plano principal.")

    candidates.sort(key=lambda c: (c["consistency"], -c["area_score"]))
    best = candidates[0]
    return {
        "scale": float(best["scale"]),
        "sheet_size_mesh": [float(best["short_mesh"]), float(best["long_mesh"])],
        "sheet_size_m": [float(best["short_m"]), float(best["long_m"])],
        "corners_3d": best["corners_3d"],
    }


def compute_a4_scale_from_mesh(
    mesh_path: str,
    input_unit: str = "mm",
) -> Dict[str, Union[float, str, List[List[float]]]]:
    pcd, source = _load_colored_point_cloud(mesh_path)
    result = compute_a4_scale_from_point_cloud(
        pcd=pcd,
        input_unit=input_unit,
    )
    result["source_path"] = source
    return result


def compute_aruco_scale_from_point_cloud(
    pcd: o3d.geometry.PointCloud,
    real_marker_size: float,
    input_unit: str = "cm",
    aruco_dict: Union[str, List[str]] = "DICT_4X4_50",
    aruco_id: Optional[int] = 0,
    max_planes: int = 4,
) -> Dict[str, Union[float, int, str, List[List[float]]]]:
    if real_marker_size is None or real_marker_size <= 0:
        raise ValueError("real_marker_size deve ser > 0.")
    if pcd.is_empty():
        raise ValueError("Nuvem de pontos vazia.")
    if not pcd.has_colors():
        raise ValueError("Nuvem de pontos sem cores.")

    unit_scale = {"m": 1.0, "cm": 0.01, "mm": 0.001}
    if input_unit not in unit_scale:
        raise ValueError("input_unit inválido (use m, cm ou mm).")
    real_marker_size_m = real_marker_size * unit_scale[input_unit]

    pcd_work = pcd
    bbox = pcd.get_axis_aligned_bounding_box()
    diag = float(np.linalg.norm(bbox.get_extent()))
    if len(pcd.points) > 400_000:
        voxel_size = max(diag / 500.0, 1e-6)
        pcd_work = pcd.voxel_down_sample(voxel_size)

    dict_list = aruco_dict if isinstance(aruco_dict, (list, tuple)) else [aruco_dict]
    candidates: List[Dict[str, Union[float, int, str, List[List[float]]]]] = []

    for dict_name in dict_list:
        dictionary = _get_aruco_dictionary(dict_name)

        pcd_iter = pcd_work
        for _ in range(max_planes):
            if len(pcd_iter.points) < 1000:
                break
            plane_model, inliers = pcd_iter.segment_plane(
                distance_threshold=max(diag * 0.002, 1e-6),
                ransac_n=3,
                num_iterations=1000,
            )
            if len(inliers) < 1000:
                break

            plane_pcd = pcd_iter.select_by_index(inliers)
            points = np.asarray(plane_pcd.points)
            colors = np.asarray(plane_pcd.colors)

            p0, u, v = _plane_basis(plane_model)
            img, min_x, min_y, px_size_x, _ = _rasterize_plane_points(
                points, colors, p0, u, v
            )

            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            gray = cv2.medianBlur(gray, 3)
            corners, ids, _ = _detect_markers(gray, dictionary)

            if ids is None or len(corners) == 0:
                pcd_iter = pcd_iter.select_by_index(inliers, invert=True)
                continue

            ids = ids.flatten().tolist()
            if aruco_id is not None:
                candidate_indices = [i for i, mid in enumerate(ids) if mid == aruco_id]
                if not candidate_indices:
                    pcd_iter = pcd_iter.select_by_index(inliers, invert=True)
                    continue
            else:
                candidate_indices = list(range(len(ids)))

            for idx in candidate_indices:
                marker_id = int(ids[idx])
                marker_corners_px = np.array(corners[idx][0], dtype=float)
                marker_corners_px = _refine_corners_subpix(gray, marker_corners_px)

                marker_corners_3d = []
                for px, py in marker_corners_px:
                    coord_x = min_x + (px + 0.5) * px_size_x
                    coord_y = min_y + (py + 0.5) * px_size_x
                    point_3d = p0 + coord_x * u + coord_y * v
                    marker_corners_3d.append(point_3d)
                marker_corners_3d = np.array(marker_corners_3d)

                edges = [
                    float(np.linalg.norm(marker_corners_3d[i] - marker_corners_3d[(i + 1) % 4]))
                    for i in range(4)
                ]
                marker_size_mesh = float(np.median(edges))
                if marker_size_mesh <= 0:
                    continue

                edge_mean = float(np.mean(edges))
                edge_std = float(np.std(edges))
                edge_cv = edge_std / edge_mean if edge_mean > 0 else float("inf")
                contour = marker_corners_px.astype(np.float32).reshape(-1, 1, 2)
                perimeter_px = float(cv2.arcLength(contour, True))

                scale = real_marker_size_m / marker_size_mesh
                candidates.append({
                    "scale": float(scale),
                    "marker_size_mesh": marker_size_mesh,
                    "marker_size_m": float(real_marker_size_m),
                    "aruco_id": marker_id,
                    "aruco_dict": dict_name,
                    "corners_3d": marker_corners_3d.tolist(),
                    "edge_cv": float(edge_cv),
                    "perimeter_px": float(perimeter_px),
                })

            pcd_iter = pcd_iter.select_by_index(inliers, invert=True)

    if not candidates:
        raise ValueError("ArUco não detectado no plano principal.")

    candidates.sort(key=lambda c: (c["edge_cv"], -c["perimeter_px"]))
    best = candidates[0]
    return {
        "scale": float(best["scale"]),
        "marker_size_mesh": float(best["marker_size_mesh"]),
        "marker_size_m": float(best["marker_size_m"]),
        "aruco_id": int(best["aruco_id"]),
        "aruco_dict": best["aruco_dict"],
        "corners_3d": best["corners_3d"],
    }


def compute_aruco_scale_from_mesh(
    mesh_path: str,
    real_marker_size: float,
    input_unit: str = "cm",
    aruco_dict: Union[str, List[str]] = "DICT_4X4_50",
    aruco_id: Optional[int] = 0,
) -> Dict[str, Union[float, int, str, List[List[float]]]]:
    pcd, source = _load_colored_point_cloud(mesh_path)
    result = compute_aruco_scale_from_point_cloud(
        pcd=pcd,
        real_marker_size=real_marker_size,
        input_unit=input_unit,
        aruco_dict=aruco_dict,
        aruco_id=aruco_id,
    )
    result["source_path"] = source
    return result
