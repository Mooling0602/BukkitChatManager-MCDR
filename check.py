#!/usr/bin/env python3
import shutil
import subprocess
import sys

STEPS = [
    ("ty", ["ty", "check", "src"]),
    ("ruff", ["ruff", "check", "src"]),
]


def run(name: str, cmd: list[str]) -> bool:
    print(f"----- {name} -----")
    if shutil.which(cmd[0]) is None:
        print(
            f"'{cmd[0]}' not found. Please install with `uv sync` or your package manager."
        )
        return False
    return subprocess.run(cmd, check=False).returncode == 0


def main() -> None:
    failed = False
    for name, cmd in STEPS:
        if not run(name, cmd):
            failed = True
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
