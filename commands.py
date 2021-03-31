from pathlib import Path
from shutil import rmtree

from runcommands import command
from runcommands.commands import local as _local


__all__ = ["install"]


VENV = ".venv"
BIN = f"./{VENV}/bin"


@command
def install():
    _local("poetry install")


@command
def update():
    _local(f"{BIN}/pip install --upgrade --upgrade-strategy eager pip")
    _local("rm -f poetry.lock")
    _local("poetry update")


@command
def format_code(check=False):
    if check:
        _local("black --check .")
    else:
        _local("black .")


@command
def lint():
    _local("flake8 .")


@command
def test(*tests, with_coverage=True, check=True):
    if tests:
        _local(f'{BIN}/python -m unittest {" ".join(tests)}')
    elif with_coverage:
        _local(f"{BIN}/coverage run --source dijkstar -m unittest discover .")
        _local(f"{BIN}/coverage report --show-missing")
    else:
        _local(f"{BIN}/python -m unittest discover .")
    if check:
        format_code(check=True)
        lint()


@command
def tox(envs=(), clean=False):
    if clean:
        path = Path(".tox")
        if path.is_dir():
            rmtree(path)
    args = []
    if envs:
        args.append("-e")
        args.extend(envs)
    _local(("tox", args))
