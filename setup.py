#!/usr/bin/env python3
import shutil
import subprocess
import sys


def main() -> None:
    if shutil.which("uv") is None:
        print(
            "Error: 'uv' not found. "
            "Please install UV first: https://docs.astral.sh/uv/",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Running 'uv sync'...")
    result = subprocess.run(["uv", "sync"], check=False)
    if result.returncode == 0:
        print("'uv sync' completed.")
    else:
        print(
            f"'uv sync' failed with exit code {result.returncode}.",
            file=sys.stderr,
        )
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
