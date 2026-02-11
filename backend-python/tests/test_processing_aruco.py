import numpy as np
import pytest

import open3d as o3d

cv2 = pytest.importorskip("cv2")

from src.processing import compute_aruco_scale_from_point_cloud


def _make_marker_point_cloud(
    marker_size: float = 1.0,
    marker_px: int = 200,
    canvas_px: int = 240,
):
    if not hasattr(cv2, "aruco"):
        pytest.skip("OpenCV sem módulo aruco.")

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    if hasattr(cv2.aruco, "generateImageMarker"):
        marker = cv2.aruco.generateImageMarker(dictionary, 0, marker_px)
    else:
        marker = cv2.aruco.drawMarker(dictionary, 0, marker_px)

    img = np.full((canvas_px, canvas_px), 255, dtype=np.uint8)
    start = (canvas_px - marker_px) // 2
    img[start:start + marker_px, start:start + marker_px] = marker

    plane_size = marker_size * (canvas_px - 1) / marker_px
    ys, xs = np.mgrid[0:canvas_px, 0:canvas_px]
    xs = xs.astype(np.float32) / (canvas_px - 1) * plane_size
    ys = ys.astype(np.float32) / (canvas_px - 1) * plane_size
    points = np.column_stack([xs.ravel(), ys.ravel(), np.zeros(xs.size, dtype=np.float32)])

    colors = img.astype(np.float32) / 255.0
    colors = np.repeat(colors[..., None], 3, axis=2).reshape(-1, 3)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd


def test_compute_aruco_scale_from_point_cloud():
    pcd = _make_marker_point_cloud()
    result = compute_aruco_scale_from_point_cloud(
        pcd=pcd,
        real_marker_size=1.0,
        input_unit="m",
        aruco_dict="DICT_4X4_50",
        aruco_id=0,
    )
    assert abs(result["scale"] - 1.0) < 0.05
    assert abs(result["marker_size_mesh"] - 1.0) < 0.05
