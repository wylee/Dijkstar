import contextlib
import io
import unittest

from .. import __version__
from ..__main__ import main


class TestConsoleScript(unittest.TestCase):

    def setUp(self):
        self.stdout = io.StringIO()
        self.redirected_stdout = contextlib.redirect_stdout(self.stdout)

    @property
    def stdout_val(self):
        return self.stdout.getvalue()

    def call_with_redirected_stdout(self, block, args):
        with self.redirected_stdout:
            block(args)

    def test_run_with_no_args(self):
        self.call_with_redirected_stdout(main, [])
        self.assertTrue(self.stdout_val.startswith(f'Dijkstar {__version__}\nusage: dijkstar'))

    def test_run_with_help_flag(self):
        try:
            self.call_with_redirected_stdout(main, ['-h'])
        except SystemExit as exc:
            self.assertEqual(exc.code, 0)
        self.assertTrue(self.stdout_val.startswith(f'Dijkstar {__version__}\n\nusage: dijkstar'))

    def test_run_serve_command(self):
        self.call_with_redirected_stdout(main, ['serve'])

    def test_run_serve_with_help_flag(self):
        try:
            self.call_with_redirected_stdout(main, ['serve', '-h'])
        except SystemExit as exc:
            self.assertEqual(exc.code, 0)
        self.assertTrue(self.stdout_val.startswith('usage: dijkstar serve'))
