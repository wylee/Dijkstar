import contextlib
import io
import sys
import unittest

from dijkstar import __version__
from dijkstar.__main__ import main


class TestConsoleScript(unittest.TestCase):

    usage = f"Dijkstar {__version__}\n\nusage: dijkstar"

    @classmethod
    def setUpClass(cls):
        cls.exit = sys.exit
        sys.exit = lambda *args, **kwargs: None

    @classmethod
    def tearDownClass(cls):
        sys.exit = cls.exit

    def setUp(self):
        stdout = io.StringIO()
        self.redirect_stdout = contextlib.redirect_stdout(stdout)
        self.get_stdout = lambda: stdout.getvalue()

    def test_run_with_no_args(self):
        with self.redirect_stdout:
            main.console_script([])
        self.assertTrue(self.get_stdout().startswith(self.usage))

    def test_run_with_help_flag(self):
        with self.redirect_stdout:
            main.console_script(["-h"])
        self.assertTrue(self.get_stdout().startswith(self.usage))

    def test_run_serve_command(self):
        with self.redirect_stdout:
            main.console_script(["serve"])

    def test_run_serve_with_help_flag(self):
        with self.redirect_stdout:
            main.console_script(["serve", "-h"])
        self.assertTrue(self.get_stdout().startswith("usage: dijkstar serve"))
