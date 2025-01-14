#!/usr/bin/env python3
"""Script to prevent git editing of a list of protected files."""

import argparse
import subprocess
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def protect_files(fpaths: List[Path], cwd: Path) -> None:
    """Protect a set of files against git edits."""
    edited_files = subprocess.run(["git", "diff", "--cached", "--name-only"],
                                  check=True, encoding="utf-8",
                                  capture_output=True, cwd=cwd).stdout
    edited_paths = [cwd / Path(x) for x in edited_files.splitlines()]
    for fpath in fpaths:
        if fpath in edited_paths:
            raise PermissionError(f"""Protected file {fpath} is staged.
Unstage the file or restore it to its original contents.""")


def _get_file_list(paths_file: Path, paths_list: list, cwd: Path) -> List[Path]:
    path_set = set()
    if paths_file.is_file():
        with open(paths_file) as f:
            for line in f:
                path_set.add(paths_file.parent / Path(line.strip()))
    [path_set.add(cwd / Path(x)) for x in paths_list]
    return list(path_set)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Forbid certain file edits.")
    parser.add_argument("-l", "--list", type=str, default="",
                        help="File, list of relative paths to protect.")
    parser.add_argument("-f", "--files", type=str, default="", nargs="+",
                        help="Whitespace-separated paths to protect.")
    args = parser.parse_args()
    cwd = Path.cwd()
    file_list = _get_file_list(cwd / Path(args.list), args.files, cwd)
    protect_files(file_list, cwd)
