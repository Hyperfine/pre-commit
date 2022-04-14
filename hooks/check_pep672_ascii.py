"""Check for PEP-672 (ASCII-only chars in source code) compliance."""

import argparse
import logging
from pathlib import Path
from typing import List, Union

logger = logging.getLogger(__name__)


def scan_files(plist: List[Path], recursive: bool, suppress: bool,
               extensions: List[str]) -> None:
    """Check files for PEP-672 compliance."""
    flist = []
    for pth in plist:
        if pth.is_file():
            if pth.suffix in extensions:
                flist.append(pth)
        elif pth.is_dir():
            glob_str = "**/*" if recursive else "*"
            new_files = [x for x in pth.glob(glob_str)
                         if x.suffix in extensions]
            flist.extend(new_files)
        else:
            logger.error(f"Path {pth} is not valid, skipping.")
    for fname in flist:
        _scan_file(fname, suppress)
    logger.info(f"Scanned {len(flist)} files.")


def _scan_file(fpath: Path, suppress: bool) -> None:
    utf_str = _get_unicode_str(fpath)
    if not utf_str:
        return
    bidi_chars = [u"\u2066", u"\u2067", u"\u2068", u"\u202A", u"\u202B",
                  u"\u202D", u"\u202E"]
    for bidi_char in bidi_chars:
        if bidi_char in utf_str:
            raise UnicodeError(f"""{fpath}
BIDI control character detected. Possible malicious code execution.""")
    for i, char in enumerate(utf_str):
        code_point = ord(char)
        if code_point > 127:
            msg = f"""{fpath}: char# {i}
Non-ASCII character detected.
If the file is a source code file, please check for possible homoglyphs.
"""
            if suppress:
                logger.warn(msg)
            else:
                raise UnicodeError(msg)


def _get_unicode_str(fpath: Path) -> Union[str, None]:
    with open(fpath) as f:
        try:
            f_str = f.read()
            return f_str
        except UnicodeDecodeError:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Check code for PEP-672.")
    parser.add_argument("-s", "--suppress", action="store_true",
                        help="Suppress errors on non-bidi characters.")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Recurse through directories.")
    parser.add_argument("-e", "--extension", type=str, nargs="+",
                        default=[".c", ".cc", ".cpp", ".py"],
                        help="Specify extensions to scan.")
    parser.add_argument("targets", type=str, nargs="+",
                        help="Full path to files or directories to scan.")
    args = parser.parse_args()
    scan_files([Path(x) for x in args.targets], args.recursive, args.suppress,
               args.extension)
