#!/usr/bin/env python
"""Python script to check for conventional commit style."""

from pathlib import Path

import toml

DEFAULT_CC_TYPES = ["build" "chore" "ci" "docs" "feat" "fix" "perf" "refactor" "revert" "style" "test"]
DEFAULT_CC_SCOPES = []
VALID_COMMIT_START_CHARS = [":", "!:"]


def cc_check():
    """Retrieve the git commit message and check it for CC style.

    CC stands for conventional commits [https://conventionalcommits.org]
    Not using regex.
    """

    # Setup
    project_dir = Path(__file__).parents[1]

    # Retrieve conventional commit configuration from pyproject.toml
    pyproject_file = project_dir / "pyproject.toml"
    toml_dict = toml.load(open(pyproject_file))

    # Need to retrieve types list from pyproject.toml.
    cc_types = toml_dict["tool"]["conventional_commit_check"]["types"] if toml_dict["tool"]["conventional_commit_check"]["types"] is not None else DEFAULT_CC_TYPES
    # Need to retrieve scope list from pyproject.toml.
    cc_scopes = toml_dict["tool"]["conventional_commit_check"]["scopes"] if toml_dict["tool"]["conventional_commit_check"]["scopes"] is not None else DEFAULT_CC_TYPES

    # Retrieve commit message.
    msg_file = project_dir / ".git" / "COMMIT_EDITMSG"
    commit_msg = open(msg_file).read()

    error_msg = f"""Commit message:
{commit_msg}

does not follow Conventional Commits formatting.
https://www.conventionalcommits.org/

Conventional Commits start with one of the below types:
{cc_types}

followed by the scope in parentheses which is one of:
{cc_scopes}

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

    # Validate the type in the commit message.
    cc_type_start_index = 0
    cc_type_end_index = commit_msg.index("(")
    cc_type = commit_msg[cc_type_start_index:cc_type_end_index]
    if cc_type not in cc_types:
        raise ValueError(error_msg)

    # Validate the scope in the commit message.
    cc_scope_start_index = cc_type_end_index
    cc_scope_end_index = commit_msg.index(")")
    cc_scope = commit_msg[cc_scope_start_index:cc_scope_end_index]
    if cc_scopes and cc_scope not in cc_scopes:
        raise ValueError(error_msg)
    commit_msg = commit_msg[cc_scope_end_index + 1:]

    # Validate that the commit message begins with either a ":" or "!:" (for breaking changes).
    breaking_change = commit_msg[0] == "!"
    colon_index = commit_msg.index(":")
    if commit_msg[:colon_index + 1] not in VALID_COMMIT_START_CHARS:
        raise ValueError(error_msg)
    commit_msg = commit_msg[colon_index + 1:]

    # Validate that the commit message actually exists
    if not commit_msg:
        raise ValueError(error_msg)

    # Validate that the breaking change description exists in the commit, if this is a breaking change.
    if breaking_change and "BREAKING CHANGE:" not in commit_msg:
        raise ValueError(error_msg)
    breaking_change_start_index = commit_msg.index("BREAKING CHANGE:")
    breaking_change_end_index = breaking_change_start_index + len("BREAKING CHANGE:")
    breaking_change_msg = commit_msg[breaking_change_end_index + 1:]

    # Validate that the description of the breaking change is non-zero length.
    if breaking_change and not breaking_change_msg:
        raise ValueError(error_msg)


def main():
    try:
        cc_check()
    except ValueError as exc:
        raise Exception().with_traceback(exc.__traceback__)


if __name__ == '__main__':
    main()