import sys
sys.path.append('/opt/scotty.py/')
import unittest
import os
import contextlib

from scotty import cli


class PerformStressorExperimentTest(unittest.TestCase):
    cmd = 'scotty experiment perform -c examples/experiment.yaml'
    script_dir = os.path.dirname(__file__)
    experiment_path = os.path.join(script_dir, '../../..')

    def test_perform_stressor_experiment(self):
        self.run_cmd()

    @contextlib.contextmanager
    def cwd(self, path):
        prev_cwd = os.getcwd()
        os.chdir(path)
        yield
        os.chdir(prev_cwd)

    def run_cmd(self):
        with self.cwd(self.experiment_path):
            cmd_args = self.cmd.split(' ')
            cli.run(cmd_args)
