import argparse
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import (
    load_config,
    run_calibration_module,
    run_opencv_module,
    run_reconstruction_module,
    run_full_module,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa módulos do backend em processo separado.")
    parser.add_argument(
        "--task",
        required=True,
        choices=["calibration", "extraction", "reconstruction", "full"],
    )
    args = parser.parse_args()

    cfg = load_config()

    if args.task == "calibration":
        ok = run_calibration_module(cfg)
    elif args.task == "extraction":
        ok = run_opencv_module(cfg)
    elif args.task == "reconstruction":
        ok = run_reconstruction_module(cfg)
    elif args.task == "full":
        ok = run_full_module(cfg)
    else:
        ok = False

    if not ok:
        print("Operação cancelada.", file=sys.stderr)
        return 2

    print(json.dumps({"status": "ok", "task": args.task}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
