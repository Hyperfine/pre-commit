import os
import sys
import glob
import unittest
import tempfile

if sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess

COMMIT_MESSAGE_FOOTER_TEMPLATE = """{commit_msg}

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# Date:      Tue Dec 28 19:35:36 2021 -0500
#
# On branch master
# Your branch is ahead of 'origin/master' by 106 commits.
#
# Changes to be committed:
#	modified:   .pre-commit-hooks.yaml
#
# Untracked files:
#
"""


class TestConventionalPreCommit(unittest.TestCase):
    def setUp(self):
        self.root = get_git_root()
        self.hook_script = os.path.join(self.root, 'hooks', 'conventional_pre_commit.py')
        self.fixture_dir = os.path.join(self.root, 'test', 'fixtures')
        self.invalid_git_dir = tempfile.gettempdir()
        self.git_dir = os.path.join(self.fixture_dir, '.git')

    def tearDown(self):
        write_commit_message("", self.git_dir)

    def _check_success(self, project_dir, pyproject_toml):
        subprocess.run([self.hook_script, "--project_dir", project_dir, "--toml", pyproject_toml], check=True)

    def _check_failure(self, project_dir, pyproject_toml):
        result = subprocess.run([self.hook_script, "--project_dir", project_dir, "--toml", pyproject_toml], stderr=subprocess.PIPE)
        self.assertEqual(result.returncode, 1)

    def test_invalid_git_dir(self):
        self._check_failure(self.invalid_git_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_valid_commit_message_default(self):
        commit_msg = "build(precommit): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_success(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_default(self):
        commit_msg = "This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_default_empty_commit(self):
        commit_msg = ""
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_default_empty_commit_description(self):
        commit_msg = "build(precommit):"
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))
    
    def test_invalid_commit_message_default_invalid_commit_separator(self):
        commit_msg = "build(precommit)!"
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))
   
    def test_invalid_commit_message_default_no_scope(self):
        commit_msg = "build: This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_default_no_type(self):
        commit_msg = "(build): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_valid_commit_message_required_scope(self):
        commit_msg = "build(tools): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_success(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.scope_only'))

    def test_invalid_commit_message_required_scope(self):
        commit_msg = "build(precommit): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.scope_only'))

    def test_valid_commit_message_required_type(self):
        commit_msg = "feat(tools): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_success(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.type_only'))

    def test_invalid_commit_message_required_type(self):
        commit_msg = "chore(precommit): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.type_only'))

    def test_valid_commit_message_required_type_and_scope(self):
        commit_msg = "build(config): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_success(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.complete'))

    def test_invalid_commit_message_required_type_and_scope(self):
        commit_msg = "chore(chore): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.complete'))

    def test_invalid_commit_message_required_type_and_scope_invalid_type(self):
        commit_msg = "chore(config): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.complete'))

    def test_invalid_commit_message_required_type_and_scope_invalid_scope(self):
        commit_msg = "build(chore): This is a sample commit message."
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.complete'))

    def test_valid_commit_message_breaking_change(self):
        commit_msg = """build(config)!: This is a sample commit message.

BREAKING CHANGE: This is a breaking change description.
"""
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_success(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_breaking_change_missing_title(self):
        commit_msg = """build(config): This is a sample commit message.

BREAKING CHANGE: This is a breaking change description.
"""
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_breaking_change_missing_description_callout(self):
        commit_msg = """build(config)!: This is a sample commit message.

This is a breaking change description.
"""
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))

    def test_invalid_commit_message_breaking_change_missing_description(self):
        commit_msg = """build(config)!: This is a sample commit message.

BREAKING CHANGE:
"""
        write_commit_message(COMMIT_MESSAGE_FOOTER_TEMPLATE.format(commit_msg=commit_msg), self.git_dir)

        self._check_failure(self.fixture_dir, os.path.join(self.fixture_dir, 'pyproject.toml.default'))


def write_commit_message(commit_msg: str, git_dir: str) -> None:
    with open(f"{git_dir}/COMMIT_EDITMSG", 'w') as _:
        _.write(commit_msg)


def get_git_root() -> str:
    """ Returns the root directory of the git repository, assuming this script is run from within the repository. """
    result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, check=True)
    if result.stdout is None:
        # TODO: concrete exception
        raise Exception('Did not get any output from git: stderr is "{}"'.format(result.stderr))
    return result.stdout.decode('utf-8').rstrip('\n')


if __name__ == '__main__':
    unittest.main()
