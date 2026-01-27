import argparse
import os
import sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.processing import compute_volume_from_mesh


def parse_point(values: list[str]) -> np.ndarray:
    if len(values) != 3:
        raise argparse.ArgumentTypeError("Ponto deve ter 3 valores (x y z).")
    return np.array([float(values[0]), float(values[1]), float(values[2])], dtype=float)


def main():
    parser = argparse.ArgumentParser(
        description="Calcula volume a partir de uma malha 3D escalada."
    )
    parser.add_argument("--mesh", required=True, help="Caminho da malha (.ply/.stl/.obj).")
    parser.add_argument("--scale", type=float, help="Fator de escala direto (opcional).")
    parser.add_argument("--p1", nargs=3, metavar=("X", "Y", "Z"), help="Ponto 1 do segmento.")
    parser.add_argument("--p2", nargs=3, metavar=("X", "Y", "Z"), help="Ponto 2 do segmento.")
    parser.add_argument("--real-length", type=float, help="Comprimento real do segmento.")
    parser.add_argument("--input-unit", default="m", choices=["m", "cm", "mm"])
    parser.add_argument("--output-unit", default="m3", choices=["m3", "cm3", "mm3"])
    parser.add_argument("--voxel-pitch", type=float, help="Tamanho do voxel (em metros).")
    parser.add_argument("--export-stl", help="Exporta malha escalada para STL.")

    args = parser.parse_args()

    p1 = parse_point(args.p1) if args.p1 else None
    p2 = parse_point(args.p2) if args.p2 else None

    result = compute_volume_from_mesh(
        mesh_path=args.mesh,
        scale=args.scale,
        segment_p1=p1,
        segment_p2=p2,
        real_distance=args.real_length,
        input_unit=args.input_unit,
        output_unit=args.output_unit,
        voxel_pitch=args.voxel_pitch,
        export_stl_path=args.export_stl,
    )

    print(
        f"Volume: {result['volume']:.6f} {result['unit']} "
        f"(método: {result['method']}, escala: {result['scale']:.6f})"
    )


if __name__ == "__main__":
    main()
