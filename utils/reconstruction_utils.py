import os

def ini_to_args(ini_path):
    """
    Lê arquivos de config do COLMAP no formato KEY=VALUE
    (exatamente como usados no C++)
    """
    args = {}
    if not os.path.exists(ini_path):
        print(f"WARNING: ini file not found: {ini_path}")
        return args

    with open(ini_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                args[k.strip()] = v.strip()

    return args


def args_to_cmd(params: dict):
    """Transforma dict em sequência --key value"""
    cmd = ""
    for k, v in params.items():
        cmd += f" --{k} {v}"
    return cmd
