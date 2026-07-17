#!/usr/bin/env python3
"""
get_link.py - Generate GitHub links from gitrepo.toml metadata.
"""

import argparse
import importlib
import sys
import warnings
from pathlib import Path
from typing import Any, cast

tomllib: Any
try:
    tomllib = cast(Any, importlib.import_module("tomllib"))
except ImportError:
    try:
        tomllib = cast(Any, importlib.import_module("tomli"))
    except ImportError:
        print(
            "Error: Missing TOML parser. Install 'tomli' or use Python 3.11+.",
            file=sys.stderr,
        )
        sys.exit(1)


def parse_gitrepo_toml(file_path: Path) -> dict[str, Any]:
    try:
        with open(file_path, "rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.", file=sys.stderr)
        sys.exit(1)
    except tomllib.TOMLDecodeError as e:
        print(f"Error: Failed to parse {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def extract_github_info(data: dict[str, Any]) -> tuple[str, str, str]:
    meta = data.get("meta", {})
    repo_name = meta.get("name")
    if not isinstance(repo_name, str) or not repo_name:
        print("Error: Missing 'meta.name' field.", file=sys.stderr)
        sys.exit(1)

    authors = meta.get("author", [])
    if not isinstance(authors, list):
        print("Error: 'meta.author' must be a list.", file=sys.stderr)
        sys.exit(1)

    owner = ""
    for author in authors:
        if isinstance(author, dict) and isinstance(author.get("github"), str):
            owner = cast(str, author["github"])
            break
    if not owner:
        print("Error: No GitHub author found in 'meta.author'.", file=sys.stderr)
        sys.exit(1)

    platform = data.get("platform", {})
    if not isinstance(platform, dict):
        print("Error: 'platform' must be a table.", file=sys.stderr)
        sys.exit(1)

    remote_hosters = platform.get("remote-hoster", [])
    if not isinstance(remote_hosters, list):
        print("Error: 'platform.remote-hoster' must be a list.", file=sys.stderr)
        sys.exit(1)

    github_base_url = ""
    other_platforms = []
    for hoster in remote_hosters:
        if not isinstance(hoster, dict):
            continue
        for key, url in hoster.items():
            if key == "github" and isinstance(url, str):
                github_base_url = url.rstrip("/")
            else:
                other_platforms.append(key)

    if not github_base_url:
        print("Error: No GitHub remote hoster found.", file=sys.stderr)
        sys.exit(1)

    if len(remote_hosters) > 1 or other_platforms:
        warnings.warn(
            f"Multiple remote platforms detected: {other_platforms}. "
            "This script currently only supports GitHub.",
            UserWarning,
            stacklevel=2,
        )

    return owner, repo_name, github_base_url


def build_repo_url(owner: str, repo: str, base_url: str) -> str:
    return f"{base_url}/{owner}/{repo}"


def build_issues_url(base_repo_url: str) -> str:
    return f"{base_repo_url}/issues"


def build_actions_url(base_repo_url: str) -> str:
    return f"{base_repo_url}/actions"


# MODIFICATION 2: Update build_compare_url to support single argument
def build_compare_url(base_repo_url: str, old_tag: str, new_tag: str = "") -> str:
    """
    Build version compare URL.
    If new_tag is empty, returns base_repo_url/compare/old_tag
    Otherwise returns base_repo_url/compare/old_tag...new_tag
    """
    if not new_tag:
        return f"{base_repo_url}/compare/{old_tag}"
    return f"{base_repo_url}/compare/{old_tag}...{new_tag}"


def main():
    result = ""
    parser = argparse.ArgumentParser(
        description="Generate GitHub links from gitrepo.toml metadata.",
        add_help=False,
    )
    parser.add_argument(
        "--repo",
        action="store_true",
        help="Return the GitHub repository page (default behavior).",
    )
    parser.add_argument(
        "--issues", action="store_true", help="Return the GitHub Issues page."
    )
    parser.add_argument(
        "--actions", action="store_true", help="Return the GitHub Actions page."
    )
    # MODIFICATION 1: Change --compare to accept 1 or 2 arguments
    parser.add_argument(
        "--compare",
        nargs="*",
        metavar=("<old_tag>", "[<new_tag>]"),
        help="Return version compare link. With one tag: compare/<old_tag>; "
        "with two tags: compare/<old_tag>...<new_tag>.",
    )
    parser.add_argument(
        "--help", "-h", action="store_true", help="Show this help message and exit."
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="Directory containing gitrepo.toml (default: .)",
    )

    args = parser.parse_args()
    old_tag = ""
    new_tag = ""

    # === MODIFICATION 3: Fix help logic (no auto-help when no args) ===
    if args.help:
        parser.print_help()
        sys.exit(0)

    if len(sys.argv) >= 2 and sys.argv[1] == "help":
        parser.print_help()
        sys.exit(0)

    # Determine action
    if args.compare is not None:
        # Validate number of arguments
        if len(args.compare) == 1:
            old_tag = args.compare[0]
            action = "compare_one"
        elif len(args.compare) == 2:
            old_tag, new_tag = args.compare
            action = "compare_two"
        else:
            print("Error: --compare accepts 1 or 2 arguments.", file=sys.stderr)
            sys.exit(1)
    elif args.issues:
        action = "issues"
    elif args.actions:
        action = "actions"
    else:
        action = "repo"

    # Parse TOML
    toml_path = Path(args.dir) / "gitrepo.toml"
    data = parse_gitrepo_toml(toml_path)
    owner, repo_name, base_url = extract_github_info(data)
    repo_url = build_repo_url(owner, repo_name, base_url)

    # Generate result
    if action == "repo":
        result = repo_url
    elif action == "issues":
        result = build_issues_url(repo_url)
    elif action == "actions":
        result = build_actions_url(repo_url)
    elif action == "compare_one":
        result = build_compare_url(repo_url, old_tag)  # single argument
    elif action == "compare_two":
        result = build_compare_url(repo_url, old_tag, new_tag)  # two arguments

    print(result)


if __name__ == "__main__":
    main()
