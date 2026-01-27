import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services import load_config, run_volume_module


def main():
    try:
        cfg = load_config()
        result = run_volume_module(cfg)
        if not result:
            print("Operação cancelada.", file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
