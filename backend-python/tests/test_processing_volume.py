import trimesh
from src.processing import compute_volume_from_mesh


def test_volume_box(tmp_path):
    mesh = trimesh.creation.box(extents=[1.0, 2.0, 3.0])
    mesh_path = tmp_path / "box.stl"
    mesh.export(mesh_path)

    result = compute_volume_from_mesh(
        mesh_path=str(mesh_path),
        scale=1.0,
        output_unit="m3",
    )

    assert abs(result["volume"] - 6.0) < 1e-6
