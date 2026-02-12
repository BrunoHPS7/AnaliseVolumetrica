import numpy as np
import open3d as o3d
import pytest

from src.processing import (
    _hsv_mask,
    _multi_hsv_mask,
    _extract_hsv_profiles_from_config,
    _detect_ground_plane,
    _segment_above_ground,
    _cluster_and_select_pile,
    _improved_heightmap_volume,
    compute_bean_volume_from_point_cloud,
)


def _make_flat_plane(n_points=5000, z=0.0, extent=2.0):
    """Create a flat plane of random points at given z."""
    xy = np.random.uniform(-extent / 2, extent / 2, (n_points, 2))
    zz = np.full((n_points, 1), z)
    return np.hstack([xy, zz])


def _make_dome(center, radius, n_points=2000):
    """Create a dome (upper hemisphere) of points."""
    pts = []
    while len(pts) < n_points:
        p = np.random.uniform(-radius, radius, 3)
        if np.linalg.norm(p) <= radius and p[2] >= 0:
            pts.append(p + center)
    return np.array(pts)


def _rgb_from_hsv_target(h, s, v, n):
    """Generate n RGB colors (0-1 float) from a given HSV center."""
    import cv2
    hsv = np.array([[[h, s, v]]], dtype=np.uint8)
    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB).reshape(3).astype(float) / 255.0
    return np.tile(rgb, (n, 1))


# ---- Test 1: Multi HSV mask union ----

def test_multi_hsv_mask_union():
    """Multiple profiles should match more points than a single one."""
    import cv2
    # Create points with 3 distinct HSV colors
    n = 100
    # Red bean (H~175)
    red_hsv = np.tile([175, 155, 79], (n, 1)).astype(np.uint8)
    # Carioca bean (H~12)
    carioca_hsv = np.tile([12, 140, 100], (n, 1)).astype(np.uint8)
    # Blue (should not match any bean profile)
    blue_hsv = np.tile([110, 200, 200], (n, 1)).astype(np.uint8)

    hsv_all = np.vstack([red_hsv, carioca_hsv, blue_hsv])

    # Single profile: only red
    single = _hsv_mask(hsv_all, 175, 155, 79, 12, 80, 80)
    assert single[:n].sum() == n  # all red matched
    assert single[n:2*n].sum() == 0  # carioca not matched

    # Multi profile: red + carioca
    profiles = [
        {"hsv_target": (175, 155, 79), "hsv_tolerance": (12, 80, 80)},
        {"hsv_target": (12, 140, 100), "hsv_tolerance": (15, 70, 70)},
    ]
    multi = _multi_hsv_mask(hsv_all, profiles)
    assert multi[:n].sum() == n       # red matched
    assert multi[n:2*n].sum() == n    # carioca matched
    assert multi[2*n:].sum() == 0     # blue not matched


# ---- Test 2: Ground plane detection ----

def test_ground_plane_detection_on_full_cloud():
    """RANSAC should detect z=0 plane as ground when table is dominant."""
    table = _make_flat_plane(5000, z=0.0, extent=3.0)
    dome = _make_dome(center=[0, 0, 0.3], radius=0.3, n_points=500)
    pts = np.vstack([table, dome])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)

    n, p0, plane_model, inliers = _detect_ground_plane(pcd)

    # Normal should be close to [0, 0, 1]
    assert abs(abs(n[2]) - 1.0) < 0.1
    # p0 z should be near 0
    assert abs(p0[2]) < 0.1
    # Should have many inliers (the table)
    assert len(inliers) > 3000


# ---- Test 3: DBSCAN clustering ----

def test_cluster_and_select_pile():
    """Should select the larger cluster and discard the smaller one."""
    # Large cluster: 2000 points around origin
    big = np.random.normal(0, 0.1, (2000, 3))
    # Small cluster: 100 points far away
    small = np.random.normal(5.0, 0.05, (100, 3))
    pts = np.vstack([big, small])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)

    result_pcd, diag = _cluster_and_select_pile(pcd, eps_fraction=0.02, min_points=10)
    result_pts = np.asarray(result_pcd.points)

    # Should have selected the big cluster
    assert len(result_pts) > 1500
    assert len(result_pts) < 2100
    # Diagnostics
    assert diag["num_clusters_found"] >= 2
    assert diag["largest_cluster_points"] > 1500


# ---- Test 4: Full pipeline with synthetic scene ----

def test_full_bean_pipeline_synthetic():
    """End-to-end test: table + brown dome → volume should be reasonable."""
    np.random.seed(42)
    # Table at z=0
    table = _make_flat_plane(5000, z=0.0, extent=2.0)
    # Bean dome at center, radius 0.15m
    dome = _make_dome(center=[0, 0, 0.15], radius=0.15, n_points=3000)
    pts = np.vstack([table, dome])

    # Colors: table is gray, dome is brown (HSV ~12, 140, 100 = carioca)
    table_colors = np.tile([0.5, 0.5, 0.5], (len(table), 1))
    dome_colors = _rgb_from_hsv_target(12, 140, 100, len(dome))
    colors = np.vstack([table_colors, dome_colors])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    profiles = [
        {"hsv_target": (12, 140, 100), "hsv_tolerance": (15, 70, 70)},
    ]
    volume, meta = compute_bean_volume_from_point_cloud(
        pcd=pcd,
        scale=1.0,
        hsv_profiles=profiles,
        detection_cfg={"voxel_downsample_fraction": 0},
    )

    # Hemisphere volume = (2/3) * pi * r^3 = (2/3) * pi * 0.15^3 ≈ 0.00707 m3
    expected = (2.0 / 3.0) * np.pi * (0.15 ** 3)
    # Heightmap on sparse synthetic data underestimates; allow wide tolerance
    assert volume > expected * 0.05
    assert volume < expected * 3.0
    assert "cluster_diagnostics" in meta
    assert meta["points_above_ground"] > 0
    assert meta["points_after_hsv_filter"] > 0


# ---- Test 5: Backward compatibility ----

def test_backward_compatibility_no_new_params():
    """Calling with only legacy params should still work."""
    np.random.seed(123)
    table = _make_flat_plane(5000, z=0.0, extent=2.0)
    dome = _make_dome(center=[0, 0, 0.15], radius=0.15, n_points=3000)
    pts = np.vstack([table, dome])

    table_colors = np.tile([0.5, 0.5, 0.5], (len(table), 1))
    dome_colors = _rgb_from_hsv_target(175, 155, 79, len(dome))
    colors = np.vstack([table_colors, dome_colors])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pts)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    # Call with only the legacy signature (no profiles, no detection_cfg)
    volume, meta = compute_bean_volume_from_point_cloud(
        pcd=pcd,
        scale=1.0,
        hsv_target=(175, 155, 79),
        hsv_tolerance=(12, 80, 80),
    )
    assert volume > 0
    assert meta["method"] == "heightmap_color"


# ---- Test 6: Config profile extraction ----

def test_extract_profiles_legacy_config():
    """Legacy config (no profiles section) should return single profile."""
    cfg = {"hsv_target": [10, 20, 30], "hsv_tolerance": [5, 10, 15]}
    profiles = _extract_hsv_profiles_from_config(cfg)
    assert len(profiles) == 1
    assert profiles[0]["hsv_target"] == (10, 20, 30)
    assert profiles[0]["hsv_tolerance"] == (5, 10, 15)


def test_extract_profiles_multi_config():
    """Config with profiles section should return multiple profiles."""
    cfg = {
        "hsv_target": [175, 155, 79],
        "hsv_tolerance": [12, 80, 80],
        "profiles": {
            "carioca": {"hsv_target": [12, 140, 100], "hsv_tolerance": [15, 70, 70]},
            "preto": {"hsv_target": [0, 0, 40], "hsv_tolerance": [180, 50, 40]},
        },
        "active_profiles": "all",
    }
    profiles = _extract_hsv_profiles_from_config(cfg)
    assert len(profiles) == 2


# ---- Test 7: Heightmap with Gaussian smoothing ----

def test_heightmap_with_gaussian_smoothing():
    """Gaussian smoothing should not change volume by more than 10%."""
    np.random.seed(99)
    # Create a flat-top box of points above z=0
    n = 5000
    xy = np.random.uniform(-0.5, 0.5, (n, 2))
    z = np.random.uniform(0.0, 1.0, (n, 1))
    pts = np.hstack([xy, z])
    heights = pts[:, 2].copy()
    normal = np.array([0.0, 0.0, 1.0])
    p0 = np.array([0.0, 0.0, 0.0])

    vol_smooth, meta_s = _improved_heightmap_volume(
        pts, heights, normal, p0, gaussian_sigma=1.0, fill_holes=False,
    )
    vol_raw, meta_r = _improved_heightmap_volume(
        pts, heights, normal, p0, gaussian_sigma=0.0, fill_holes=False,
    )

    # Both should be positive
    assert vol_smooth > 0
    assert vol_raw > 0
    # Volume difference < 10%
    diff = abs(vol_smooth - vol_raw) / vol_raw
    assert diff < 0.10
