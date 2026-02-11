import numpy as np
import trimesh

from src.processing import compute_heightmap_volume


def test_heightmap_volume_box():
    box = trimesh.creation.box(extents=[1.0, 2.0, 3.0])
    box.apply_translation([0.0, 0.0, 1.5])  # base no plano z=0

    volume, meta = compute_heightmap_volume(box, grid_size=0.05)
    assert abs(volume - 6.0) < 0.2
    assert meta["points_used"] > 0
