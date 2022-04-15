"""Test PEP-672 checker."""

from pathlib import Path

import pytest

from hooks import check_pep672_ascii


def test_noncompliant_file(tmp_path: Path) -> None:
    """Test scanning a known noncompliant file. Expects error."""
    tmpfile = tmp_path / "noncompliant.py"
    with open(tmpfile, "w") as f:
        f.write("⁦")
    with pytest.raises(UnicodeError):
        check_pep672_ascii.scan_files([tmpfile], False, False, [".py"])


def test_compliant_file(tmp_path: Path) -> None:
    """Test scanning a known valid file. Expects return success."""
    tmpfile = tmp_path / "compliant.py"
    with open(tmpfile, "w") as f:
        f.write("hello")
    assert(check_pep672_ascii.scan_files(
        [tmpfile], False, False, [".py"]) == None)
