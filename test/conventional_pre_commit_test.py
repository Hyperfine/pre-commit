import os
import sys
import glob
import unittest

if sys.version_info[0] < 3:
    import subprocess32 as subprocess
else:
    import subprocess


class TestConventionalPreCommit(unittest.TestCase):
    def setUp(self):
        self.root = get_git_root()
        self.hook_script = os.path.join(self.root, 'hooks', 'conventional_pre_commit.py')
        self.fixture_dir = os.path.join(self.root, 'test', 'fixtures')

    def _check_success(self, files):
        

def get_git_root():
    """ Returns the root directory of the git repository, assuming this script is run from within the repository. """
    result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, check=True)
    if result.stdout is None:
        # TODO: concrete exception
        raise Exception('Did not get any output from git: stderr is "{}"'.format(result.stderr))
    return result.stdout.decode('utf-8').rstrip('\n')
