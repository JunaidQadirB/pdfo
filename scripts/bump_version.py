#!/usr/bin/env python3
"""Bump semantic version in pyproject.toml."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VERSION_RE = re.compile(r"(?m)^version\s*=\s*\"(\d+\.\d+\.\d+)\"\s*$")


def bump_version(version: str, bump: str) -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    elif bump == "patch":
        patch += 1
    else:
        raise ValueError(f"Unknown bump type: {bump}")
    return f"{major}.{minor}.{patch}"


def read_version(text: str) -> str:
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def write_version(path: Path, new_version: str) -> None:
    text = path.read_text(encoding="utf-8")
    new_text, count = VERSION_RE.subn(f'version = "{new_version}"', text, count=1)
    if count != 1:
        raise ValueError("Failed to update version in pyproject.toml")
    path.write_text(new_text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml")
    parser.add_argument("--file", default="pyproject.toml", help="Path to pyproject.toml")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump type")
    parser.add_argument("--current", action="store_true", help="Print current version")
    args = parser.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    current = read_version(text)

    if args.current:
        print(current)
        return 0

    if not args.bump:
        raise SystemExit("--bump is required unless --current is set")

    new_version = bump_version(current, args.bump)
    write_version(path, new_version)
    print(new_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
