from runcommands import command
from runcommands.commands import local as _local, release


__all__ = ['install', 'release']


VENV = '.venv'
BIN = f'./{VENV}/bin'


@command
def install():
    _local(f'{BIN}/pip install --upgrade --upgrade-strategy eager pip --editable .[dev,server]')


@command
def lint():
    _local('flake8 .')


@command
def test(*tests):
    if tests:
        _local(f'{BIN}/python -m unittest {" ".join(tests)}')
    else:
        _local(f'{BIN}/coverage run --source dijkstar -m unittest discover .')
        _local(f'{BIN}/coverage report --show-missing')


@command
def tox():
    _local('tox')
