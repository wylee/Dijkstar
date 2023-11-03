from pathlib import Path
from shutil import rmtree

from runcommands import command, commands as c, printer

__all__ = ["install"]

VENV = Path(__file__).parent / ".venv"
BIN = VENV / "bin"
COVERAGE = BIN / "coverage"
PIP = BIN / "pip"
PYTHON = BIN / "python"
RUFF = BIN / "ruff"


@command
def install():
    c.local("poetry install")


@command
def update():
    c.local(f"{PIP} install --upgrade --upgrade-strategy eager pip")
    c.local("rm -f poetry.lock")
    c.local("poetry update")


@command
def format_code(check=False):
    c.local((RUFF, "check" if check else "format", "."))


@command
def test(*tests, with_coverage=True, check=True):
    if tests:
        c.local((f"{PYTHON}", "-m", "unittest", tests))
    elif with_coverage:
        c.local(f"{COVERAGE} run --source dijkstar -m unittest discover .")
        c.local(f"{COVERAGE} report --show-missing")
    else:
        c.local(f"{PYTHON} -m unittest discover .")
    if check:
        format_code(check=True)


@command
def tox(envs=(), clean=False):
    if clean:
        path = Path(".tox")
        if path.is_dir():
            printer.warning("Removing .tox directory...", end="")
            rmtree(path)
            printer.print()
    args = []
    if envs:
        args.append("-e")
        args.extend(envs)
    c.local(("tox", args))
