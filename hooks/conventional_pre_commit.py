#!/usr/bin/env python3
"""Python script to check for conventional commit style."""

import os
from pathlib import Path
import argparse
import toml
import sys

DEFAULT_CC_TYPES = ["build", "chore", "ci", "docs", "feat", "fix", "perf", "refactor", "revert", "style", "test"]
DEFAULT_CC_SCOPES = []
VALID_COMMIT_START_CHARS = [":", "!:"]


def cc_check(project_dir: str, pyproject_file: str) -> None:
    """Retrieve the git commit message and check it for CC style.

    CC stands for conventional commits [https://conventionalcommits.org]
    Not using regex.

    Args:
        project_dir (str): The root directory of the project.
        pyproject_file (str): The path to the `pyproject.toml`
    """
    # Retrieve conventional commit configuration from pyproject.toml
    toml_dict = toml.load(open(pyproject_file))

    # Need to retrieve types list from pyproject.toml.
    try:
        cc_types = toml_dict["tool"]["conventional_commit_check"]["types"] if toml_dict["tool"]["conventional_commit_check"]["types"] is not None else DEFAULT_CC_TYPES
    except KeyError:
        cc_types = DEFAULT_CC_TYPES
    # Need to retrieve scope list from pyproject.toml.
    try:
        cc_scopes = toml_dict["tool"]["conventional_commit_check"]["scopes"] if toml_dict["tool"]["conventional_commit_check"]["scopes"] is not None else DEFAULT_CC_TYPES
    except KeyError:
        cc_scopes = DEFAULT_CC_SCOPES

    # Retrieve commit message.
    msg_file = project_dir / ".git" / "COMMIT_EDITMSG"
    commit_msg_lines = open(msg_file).readlines()

    # Parse the commit message to remove any ignored lines.
    commit_msg = []
    for line in commit_msg_lines:
        if line[0] == "#":
            continue
        commit_msg.append(line)

    commit_msg = '\n'.join(commit_msg).strip()

    error_msg = f"""Commit message:
{commit_msg}

does not follow Conventional Commits formatting.
https://www.conventionalcommits.org/

Conventional Commits start with one of the below types:
{','.join(cc_types)}

followed by the scope in parentheses which is one of:
{','.join(cc_scopes)}

followed by a colon and a space, followed by the commit message.

Example:
    fix(recon): remove infinite loop

If your commit contains a breaking change, then a "!" should come
before the colon and your commit message must have "BREAKING CHANGE:"
with a description of the change as it's last line.

Example:
    fix(recon)!: update to tensorflow 3

    This makes changes to support only tensorflow 3.

    BREAKING CHANGE: removes support for tensorflow 2
"""
    # Validate that the commit message is not just an empty string
    if not commit_msg:
        sys.exit(error_msg)

    # Validate the type in the commit message.
    cc_type_start_index = 0
    try:
        cc_type_end_index = commit_msg.index("(")
        cc_type = commit_msg[cc_type_start_index:cc_type_end_index]
        if cc_type not in cc_types:
            sys.exit(error_msg)
    except ValueError:
        sys.exit(error_msg)

    # Validate the scope in the commit message.
    try:
        cc_scope_start_index = cc_type_end_index + 1
        cc_scope_end_index = commit_msg.index(")")
        cc_scope = commit_msg[cc_scope_start_index:cc_scope_end_index]
        if cc_scopes and cc_scope not in cc_scopes:
            sys.exit(error_msg)
    except ValueError:
        sys.exit(error_msg)
    commit_msg = commit_msg[cc_scope_end_index + 1:]

    # Validate that the commit message begins with either a ":" or "!:" (for breaking changes).
    breaking_change = commit_msg[0] == "!"
    try:
        colon_index = commit_msg.index(":")
    except ValueError:
        sys.exit(error_msg)
    commit_msg = commit_msg[colon_index + 1:]

    # Validate that the commit message actually exists
    if not commit_msg:
        sys.exit(error_msg)

    # Validate that the breaking change description exists in the commit, if this is a breaking change.
    if breaking_change:
        if "BREAKING CHANGE:" not in commit_msg:
            sys.exit(error_msg)
        breaking_change_start_index = commit_msg.index("BREAKING CHANGE:")
        breaking_change_end_index = breaking_change_start_index + len("BREAKING CHANGE:")
        breaking_change_msg = commit_msg[breaking_change_end_index + 1:]

        # Validate that the description of the breaking change is non-zero length.
        if breaking_change and not breaking_change_msg:
            sys.exit(error_msg)
    if not breaking_change and "BREAKING CHANGE:" in commit_msg:
        sys.exit(error_msg)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            'A CLI for checking commit messages against the conventional commit standard '
            'Optionally takes in a project directory to check. Defaults to the current working directory.'
        ),
    )
    parser.add_argument(
        '--project_dir',
        dest='project_dir',
        metavar='PROJECT_DIR',
        type=str,
        nargs='?',
        default=os.getcwd(),
        help='The project directory. Defaults to the current working directory.',
    )
    parser.add_argument(
        '--toml',
        dest='toml',
        metavar='PYPROJECT_TOML',
        type=str,
        nargs='?',
        default=os.path.join(os.getcwd(), "pyproject.toml"),
        help='The path to the `pyproject.toml` file. Defaults to `pyproject.toml` in the current working directory.',
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    project_dir = Path(args.project_dir)
    pyproject_file = Path(args.toml)
    try:
        cc_check(project_dir=project_dir, pyproject_file=pyproject_file)
    except ValueError as e:
        sys.exit(str(e))


if __name__ == '__main__':
    main()
