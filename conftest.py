"""On GH Actions windows-latest, the supplied tmpdir is on a different Drive to the CWD,
and so relative path computations fail.
Therefore, here we allow for the directory to be directly supplied,
via an environmental variable.
"""

import shutil
from pathlib import Path
from uuid import uuid4

import pytest


def pytest_addoption(parser):
    """Define pytest command-line option"""
    group = parser.getgroup("jupyter_book")
    group.addoption(
        "--jb-tempdir",
        dest="jb_tempdir",
        default=None,
        help="Specify a directory in which to create tempdirs",
    )


def pytest_report_header(config):
    path = "<TEMP>"
    if config.getoption("jb_tempdir"):
        path = Path(config.getoption("jb_tempdir")).absolute().as_posix()
    return [f"JB TEMPDIR: {path}"]


@pytest.fixture()
def temp_with_override(pytestconfig, tmpdir):
    if pytestconfig.getoption("jb_tempdir"):
        path = Path(pytestconfig.getoption("jb_tempdir")).resolve().absolute()
        path = path / str(uuid4())
        path.mkdir(parents=True)
        yield path
        shutil.rmtree(path)
    else:
        yield Path(tmpdir.dirname) / tmpdir.basename
