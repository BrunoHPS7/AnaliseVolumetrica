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
    pixel_size = max(spacing / 1.5, 1e-6)

    width = int(extent[0] / pixel_size) + 1
    height = int(extent[1] / pixel_size) + 1
    max_dim = max(width, height)
    if max_dim > max_dim_px:
        pixel_size *= max_dim / max_dim_px
    elif max_dim < min_dim_px:
        pixel_size *= max_dim / min_dim_px

    width = int(extent[0] / pixel_size) + 1
    height = int(extent[1] / pixel_size) + 1

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
    return img_uint8, float(min_xy[0]), float(min_xy[1]), float(pixel_size), float(pixel_size)


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
