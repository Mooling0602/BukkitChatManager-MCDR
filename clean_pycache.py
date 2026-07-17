#!/usr/bin/env python3
import shutil
from pathlib import Path


def clean_pycache(root_dir: Path | str = ".") -> tuple[int, int]:
    """Recursively remove all __pycache__ directories under root_dir.

    Returns:
        (deleted_count, error_count)
    """
    root = Path(root_dir).resolve()
    if not root.is_dir():
        print(f"Error: '{root_dir}' is not a valid directory.")
        return 0, 1

    deleted = 0
    errors = 0

    for pycache in root.rglob("__pycache__"):
        if not pycache.is_dir():
            continue
        try:
            shutil.rmtree(pycache)
            print(f"Removed: {pycache}")
            deleted += 1
        except OSError as e:
            print(f"Failed to remove {pycache}: {e}")
            errors += 1

    return deleted, errors


def main() -> None:
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    deleted, errors = clean_pycache(root)

    if deleted == 0 and errors == 0:
        print("No __pycache__ directories found.")
    else:
        print()
        print(f"Done. {deleted} removed, {errors} failed.")


if __name__ == "__main__":
    main()
