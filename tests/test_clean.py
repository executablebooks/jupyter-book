"""Testing clean functionality of the CLI."""

import os

from click.testing import CliRunner

from jupyter_book.cli.main import build, clean


def test_clean_book(cli: CliRunner, build_resources):
    books, tocs = build_resources
    path = books.joinpath("clean_cache")
    build_path = path.joinpath("_build")
    result = cli.invoke(build, path.as_posix())
    assert result.exit_code == 0

    # Ensure _build exists
    assert build_path.exists()

    # Ensure _build/.jupyter_cache exists
    assert build_path.joinpath(".jupyter_cache").exists()

    # Empty _build except .jupyter_cache
    result = cli.invoke(clean, path.as_posix())
    assert result.exit_code == 0

    # Ensure _build and .jupyter_cache exist
    assert build_path.exists()
    assert build_path.joinpath(".jupyter_cache").exists()

    result = cli.invoke(clean, ("--all", path.as_posix()))
    assert result.exit_code == 0
    # Ensure _build is removed
    assert not path.joinpath("_build").exists()

    # === Excepted errors ===
    # Non-existent folder
    result = cli.invoke(clean, "doesnt/exist")
    assert result.exit_code != 0
    assert isinstance(result.exception, RuntimeError)
    assert "Path to book isn't a directory" in str(result.exception)


def test_clean_html(cli, build_resources):
    books, tocs = build_resources
    path = books.joinpath("clean_cache")
    build_path = path.joinpath("_build")
    print(path.as_posix())
    result = cli.invoke(build, path.as_posix())
    assert result.exit_code == 0

    # Ensure _build exists
    assert build_path.exists()
    # Ensure _build/html exists
    assert build_path.joinpath("html").exists()

    # Remove html
    result = cli.invoke(clean, ("--html", path.as_posix()))
    assert result.exit_code == 0

    # Ensure _build  exists
    assert build_path.exists()

    # Ensure html is removed
    assert not build_path.joinpath("html").exists()


def test_clean_latex(cli, build_resources):
    books, tocs = build_resources
    path = books.joinpath("clean_cache")
    result = cli.invoke(build, path.as_posix())
    assert result.exit_code == 0

    build_path = path.joinpath("_build")
    # Ensure _build exists
    assert build_path.exists()

    os.mkdir(os.path.join(build_path, "latex"))

    # Ensure _build/html exists
    assert build_path.joinpath("latex").exists()

    # Remove html
    result = cli.invoke(clean, ("--latex", path.as_posix()))
    assert result.exit_code == 0

    # Ensure _build exists
    assert build_path.exists()

    # Ensure latex is removed
    assert not build_path.joinpath("latex").exists()


def test_clean_html_latex(cli, build_resources):
    books, tocs = build_resources
    path = books.joinpath("clean_cache")
    result = cli.invoke(build, path.as_posix())
    assert result.exit_code == 0

    build_path = path.joinpath("_build")

    # Ensure _build exists
    assert build_path.exists()
    os.mkdir(os.path.join(build_path, "latex"))

    # Ensure _build/html exists
    assert build_path.joinpath("latex").exists()

    # Ensure _build/html exists
    assert build_path.joinpath("html").exists()

    # Remove html
    result = cli.invoke(clean, ("--html", "--latex", path.as_posix()))
    assert result.exit_code == 0

    # Ensure _build exists
    assert build_path.exists()

    # Ensure latex is removed
    assert not build_path.joinpath("latex").exists()

    # Ensure html is removed
    assert not build_path.joinpath("html").exists()
