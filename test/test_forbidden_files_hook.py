"""Test the forbidden-files hook."""

from pathlib import Path
import subprocess

import pytest

from hooks import forbidden_files


def _git_add_commit(test_name: str, tmp_path: Path) -> None:
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit",
                    "--author", "pytest <pytest@example.com>",
                    "--message", f"test commit from {test_name}"],
                   cwd=tmp_path, check=True)


def test_forbidden_files(tmp_path: Path) -> None:
    """Simulate a scenario where a protected file is edited."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    forbidden_file = tmp_path / "do_not_edit.txt"
    with open(forbidden_file, "w") as f:
        f.write("test")

    protected_list = tmp_path / "protected.txt"
    with open(protected_list, "w") as f:
        f.write("do_not_edit.txt\nprotected.txt")

    _git_add_commit("test_forbidden_files", tmp_path)

    with open(forbidden_file, "w") as f:
        f.write("I edited it!")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)

    forbidden_list = forbidden_files._get_file_list(protected_list, "")
    with pytest.raises(PermissionError):
        forbidden_files.protect_files(forbidden_list, cwd=tmp_path)


def test_non_forbidden_files(tmp_path: Path) -> None:
    """Simulate a scenario where a non-protected file is edited."""
    subprocess.run(["git", "init"], cwd=tmp_path, check=True)

    forbidden_file = tmp_path / "do_not_edit.txt"
    with open(forbidden_file, "w") as f:
        f.write("test")
    ok_file = tmp_path / "edit_me.txt"
    with open(ok_file, "w") as f:
        f.write("hello")
    protected_list = tmp_path / "protected.txt"
    with open(protected_list, "w") as f:
        f.write("do_not_edit.txt\nprotected.txt\n")

    _git_add_commit("test_non_forbidden_files", tmp_path)

    with open(ok_file, "w") as f:
        f.write("I edited it!")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)

    forbidden_list = forbidden_files._get_file_list(protected_list, "")
    assert(forbidden_files.protect_files(forbidden_list,
                                         cwd=tmp_path) == None)
