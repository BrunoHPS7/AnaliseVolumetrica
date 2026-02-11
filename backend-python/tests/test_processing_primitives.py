import trimesh

from src.processing import compute_volume_from_mesh


def test_primitive_box_detection(tmp_path):
    mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
    mesh_path = tmp_path / "box.stl"
    mesh.export(mesh_path)

    result = compute_volume_from_mesh(
        mesh_path=str(mesh_path),
        scale=1.0,
        volume_method="auto",
    )

    assert result["method"].startswith("primitive_")
    assert abs(result["volume"] - 8.0) < 1e-3
