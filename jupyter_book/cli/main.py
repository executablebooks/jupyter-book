"""Defines the commands that the CLI will use.

IMPORTANT: Top-level imports should be minimised here, to improve CLI responsiveness
"""
import os
import os.path as op
import shutil as sh
import subprocess
import sys
from glob import iglob
from pathlib import Path
from textwrap import dedent
from typing import Tuple

import click

from jupyter_book.utils import _error, _message_box

from .pluggable import PluggableGroup


def version_callback(ctx, param, value):
    """Callback for supplying version information"""
    if not value or ctx.resilient_parsing:
        return

    from jupyter_cache import __version__ as jcv
    from myst_nb import __version__ as mnbv
    from myst_parser import __version__ as mpv
    from nbclient import __version__ as ncv
    from sphinx_book_theme import __version__ as sbtv
    from sphinx_external_toc import __version__ as etoc

    from jupyter_book import __version__ as jbv

    versions = {
        "Jupyter Book": jbv,
        "External ToC": etoc,
        "MyST-Parser": mpv,
        "MyST-NB": mnbv,
        "Sphinx Book Theme": sbtv,
        "Jupyter-Cache": jcv,
        "NbClient": ncv,
    }
    versions_string = "\n".join(f"{tt:<18}: {vv}" for tt, vv in versions.items())
    click.echo(versions_string)
    ctx.exit()


@click.group(
    cls=PluggableGroup,
    entry_point_group="jb.cmdline",
    use_internal={"build", "clean", "config", "create", "myst"},
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--version",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    help="Show the version and exit.",
    callback=version_callback,
)
def main():
    """Build and manage books with Jupyter."""
    pass


BUILDER_OPTS = {
    "html": "html",
    "dirhtml": "dirhtml",
    "singlehtml": "singlehtml",
    "pdfhtml": "singlehtml",
    "latex": "latex",
    "pdflatex": "latex",
    "linkcheck": "linkcheck",
    "custom": None,
}


@main.command()
@click.argument("path-source", type=click.Path(exists=True, file_okay=True))
@click.option("--path-output", default=None, help="Path to the output artifacts")
@click.option(
    "--config",
    default=None,
    help="Path to the YAML configuration file (default: PATH_SOURCE/_config.yml)",
)
@click.option(
    "--toc",
    default=None,
    help="Path to the Table of Contents YAML file (default: PATH_SOURCE/_toc.yml)",
)
@click.option("-W", "--warningiserror", is_flag=True, help="Error on warnings.")
@click.option(
    "-n",
    "--nitpick",
    is_flag=True,
    help="Run in nit-picky mode, to generates warnings for all missing references.",
)
@click.option(
    "--keep-going",
    is_flag=True,
    help="With -W, do not stop the build on the first warning, "
    "instead error on build completion",
)
@click.option(
    "--all",
    "freshenv",
    is_flag=True,
    help="Re-build all pages. "
    "The default is to only re-build pages that are new/changed since the last run.",
)
@click.option(
    "--builder",
    default="html",
    help="Which builder to use.",
    type=click.Choice(list(BUILDER_OPTS.keys())),
)
@click.option(
    "--custom-builder",
    default=None,
    help="Specify alternative builder provided by Sphinx, including text and epub. "
    "This can only be used with --builder=custom. Valid options listed at "
    "https://www.sphinx-doc.org/en/master/man/sphinx-build.html",
)
@click.option(
    "-v", "--verbose", count=True, help="increase verbosity (can be repeated)"
)
@click.option(
    "-q",
    "--quiet",
    count=True,
    help="-q means no sphinx status, -qq also turns off warnings ",
)
@click.option(
    "--individualpages",
    is_flag=True,
    default=False,
    help="[pdflatex] Enable build of PDF files for each individual page",
)
def build(
    path_source,
    path_output,
    config,
    toc,
    warningiserror,
    nitpick,
    keep_going,
    freshenv,
    builder,
    custom_builder,
    verbose,
    quiet,
    individualpages,
    get_config_only=False,
):
    """Convert your book's or page's content to HTML or a PDF."""
    from sphinx_external_toc.parsing import MalformedError, parse_toc_yaml

    from jupyter_book import __version__ as jbv
    from jupyter_book.sphinx import build_sphinx

    if not get_config_only:
        click.secho(f"Running Jupyter-Book v{jbv}", bold=True, fg="green")

    # Paths for the notebooks
    PATH_SRC_FOLDER = Path(path_source).absolute()

    config_overrides = {}
    use_external_toc = True
    found_config = find_config_path(PATH_SRC_FOLDER)
    BUILD_PATH = path_output if path_output is not None else found_config[0]

    # Set config for --individualpages option (pages, documents)
    if individualpages:
        if builder != "pdflatex":
            _error(
                """
                Specified option --individualpages only works with the
                following builders:

                pdflatex
                """
            )

    # Build Page
    if not PATH_SRC_FOLDER.is_dir():
        # it is a single file
        build_type = "page"
        use_external_toc = False
        subdir = None
        PATH_SRC = Path(path_source)
        PATH_SRC_FOLDER = PATH_SRC.parent.absolute()
        PAGE_NAME = PATH_SRC.with_suffix("").name

        # checking if the page is inside a sub directory
        # then changing the build_path accordingly
        if str(BUILD_PATH) in str(PATH_SRC_FOLDER):
            subdir = str(PATH_SRC_FOLDER.relative_to(BUILD_PATH))
        if subdir and subdir != ".":
            subdir = subdir.replace("/", "-")
            subdir = subdir + "-" + PAGE_NAME
            BUILD_PATH = Path(BUILD_PATH).joinpath("_build", "_page", subdir)
        else:
            BUILD_PATH = Path(BUILD_PATH).joinpath("_build", "_page", PAGE_NAME)

        # Find all files that *aren't* the page we're building and exclude them
        to_exclude = [
            op.relpath(ifile, PATH_SRC_FOLDER)
            for ifile in iglob(str(PATH_SRC_FOLDER.joinpath("**", "*")), recursive=True)
            if ifile != str(PATH_SRC.absolute())
        ]
        to_exclude.extend(["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"])

        # Now call the Sphinx commands to build
        config_overrides = {
            "master_doc": PAGE_NAME,
            "exclude_patterns": to_exclude,
            # --individualpages option set to True for page call
            "latex_individualpages": True,
        }
    # Build Project
    else:
        build_type = "book"
        PAGE_NAME = None
        BUILD_PATH = Path(BUILD_PATH).joinpath("_build")

        # Table of contents
        toc = PATH_SRC_FOLDER.joinpath("_toc.yml") if toc is None else Path(toc)

        if not get_config_only:
            if not toc.exists():
                _error(
                    "Couldn't find a Table of Contents file. "
                    "To auto-generate one, run:"
                    f"\n\n\tjupyter-book toc from-project {path_source}"
                )

            # we don't need to read the toc here, but do so to control the error message
            try:
                parse_toc_yaml(toc)
            except MalformedError as exc:
                _error(
                    f"The Table of Contents file is malformed: {exc}\n"
                    "You may need to migrate from the old format, using:"
                    f"\n\n\tjupyter-book toc migrate {toc} -o {toc}"
                )
            # TODO could also check/warn if the format is not set to jb-article/jb-book?

        config_overrides["external_toc_path"] = (
            toc.relative_to(PATH_SRC_FOLDER).as_posix()
            if get_config_only
            else toc.as_posix()
        )

        # --individualpages option passthrough
        config_overrides["latex_individualpages"] = individualpages

    # Use the specified configuration file, or one found in the root directory
    path_config = config or (
        found_config[0].joinpath("_config.yml") if found_config[1] else None
    )
    if path_config and not Path(path_config).exists():
        raise IOError(f"Config file path given, but not found: {path_config}")

    if builder in ["html", "pdfhtml", "linkcheck"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("html")
    elif builder in ["latex", "pdflatex"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("latex")
    elif builder in ["dirhtml"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("dirhtml")
    elif builder in ["singlehtml"]:
        OUTPUT_PATH = BUILD_PATH.joinpath("singlehtml")
    elif builder in ["custom"]:
        OUTPUT_PATH = BUILD_PATH.joinpath(custom_builder)
        BUILDER_OPTS["custom"] = custom_builder

    if nitpick:
        config_overrides["nitpicky"] = True

    # If we only want config (e.g. for printing/validation), stop here
    if get_config_only:
        return (path_config, PATH_SRC_FOLDER, config_overrides)

    # print information about the build
    click.echo(
        click.style("Source Folder: ", bold=True, fg="blue")
        + click.format_filename(f"{PATH_SRC_FOLDER}")
    )
    click.echo(
        click.style("Config Path: ", bold=True, fg="blue")
        + click.format_filename(f"{path_config}")
    )
    click.echo(
        click.style("Output Path: ", bold=True, fg="blue")
        + click.format_filename(f"{OUTPUT_PATH}")
    )

    # Now call the Sphinx commands to build
    result = build_sphinx(
        PATH_SRC_FOLDER,
        OUTPUT_PATH,
        use_external_toc=use_external_toc,
        noconfig=True,
        path_config=path_config,
        confoverrides=config_overrides,
        builder=BUILDER_OPTS[builder],
        warningiserror=warningiserror,
        keep_going=keep_going,
        freshenv=freshenv,
        verbosity=verbose,
        quiet=quiet > 0,
        really_quiet=quiet > 1,
    )

    builder_specific_actions(
        result, builder, OUTPUT_PATH, build_type, PAGE_NAME, click.echo
    )


@main.command()
@click.argument("path-book", type=click.Path(file_okay=False, exists=False))
@click.option(
    "--cookiecutter",
    is_flag=True,
    help="Use cookiecutter to interactively create a Jupyter Book template.",
)
@click.option(
    "--no-input",
    is_flag=True,
    help="If using cookiecutter, do not prompt the user for input.",
)
def create(path_book, cookiecutter, no_input):
    """Create a Jupyter Book template that you can customize."""
    book = Path(path_book)
    if not cookiecutter:  # this will be the more common option
        template_path = Path(__file__).parent.parent.joinpath("book_template")
        sh.copytree(template_path, book)
    else:
        cc_url = "gh:executablebooks/cookiecutter-jupyter-book"
        try:
            from cookiecutter.main import cookiecutter
        except ModuleNotFoundError as e:
            _error(
                f"{e}. To install, run\n\n\tpip install cookiecutter",
                kind=e.__class__,
            )

        book = cookiecutter(cc_url, output_dir=Path(path_book), no_input=no_input)
    _message_box(f"Your book template can be found at\n\n    {book}{os.sep}")


@main.command()
@click.argument("path-book")
@click.option("-a", "--all", "all_", is_flag=True, help="Remove build directory.")
@click.option("--html", is_flag=True, help="Remove html directory.")
@click.option("--latex", is_flag=True, help="Remove latex directory.")
def clean(path_book, all_, html, latex):
    """Empty the _build directory except jupyter_cache.
    If the all option has been flagged, it will remove the entire _build. If html/latex
    option is flagged, it will remove the html/latex subdirectories."""

    def remove_option(path, option, rm_both=False):
        """Remove folder specified under option. If rm_both is True, remove folder and
        skip message_box."""
        option_path = path.joinpath(option)
        if not option_path.is_dir():
            return

        sh.rmtree(option_path)
        if not rm_both:
            _message_box(f"Your {option} directory has been removed")

    def remove_html_latex(path):
        """Remove both html and latex folders."""
        print_msg = False
        for opt in ["html", "latex"]:
            if path.joinpath(opt).is_dir():
                print_msg = True
            remove_option(path, opt, True)

        if print_msg:
            _message_box("Your html and latex directories have been removed")

    def remove_all(path):
        """Remove _build directory entirely."""
        sh.rmtree(path)
        _message_box("Your _build directory has been removed")

    def remove_default(path):
        """Remove all subfolders in _build except .jupyter_cache."""
        to_remove = [
            dd for dd in path.iterdir() if dd.is_dir() and dd.name != ".jupyter_cache"
        ]
        for dd in to_remove:
            sh.rmtree(path.joinpath(dd.name))
        _message_box("Your _build directory has been emptied except for .jupyter_cache")

    PATH_OUTPUT = Path(path_book).absolute()
    if not PATH_OUTPUT.is_dir():
        _error(f"Path to book isn't a directory: {PATH_OUTPUT}")

    build_path = PATH_OUTPUT.joinpath("_build")
    if not build_path.is_dir():
        return

    if all_:
        remove_all(build_path)
    elif html and latex:
        remove_html_latex(build_path)
    elif html:
        remove_option(build_path, "html")
    elif latex:
        remove_option(build_path, "latex")
    else:
        remove_default(build_path)


@main.group()
def myst():
    """Manipulate MyST markdown files."""
    pass


@myst.command()
@click.argument("path", nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--kernel", help="The name of the Jupyter kernel to attach to this markdown file."
)
def init(path, kernel):
    """Add Jupytext metadata for your markdown file(s), with optional Kernel name."""
    from jupyter_book.utils import init_myst_file

    for ipath in path:
        init_myst_file(ipath, kernel, verbose=True)


@main.group()
def config():
    """Inspect your _config.yml file."""
    pass


@config.command()
@click.argument("path-source", type=click.Path(exists=True, file_okay=True))
@click.option(
    "--config",
    default=None,
    help="Path to the YAML configuration file (default: PATH_SOURCE/_config.yml)",
)
@click.option(
    "--toc",
    default=None,
    help="Path to the Table of Contents YAML file (default: PATH_SOURCE/_toc.yml)",
)
@click.option(
    "--output-dir",
    default=None,
    help="Path to the output directory for resulting conf.py"
    " (default: same folder as the yaml config file)",
)
@click.pass_context
def sphinx(ctx, path_source, config, toc, output_dir):
    """Generate a Sphinx conf.py representation of the build configuration."""
    from jupyter_book.config import get_final_config

    path_config, full_path_source, config_overrides = ctx.invoke(
        build, path_source=path_source, config=config, toc=toc, get_config_only=True
    )
    sphinx_config, _ = get_final_config(
        user_yaml=Path(path_config) if path_config else None,
        sourcedir=Path(full_path_source),
        cli_config=config_overrides,
    )
    lines = [
        "###############################################################################",
        "# Auto-generated by `jupyter-book config`",
        "# If you wish to continue using _config.yml, make edits to that file and",
        "# re-generate this one.",
        "###############################################################################",
    ]
    for key in sorted(sphinx_config):
        lines.append(f"{key} = {sphinx_config[key]!r}")
    content = "\n".join(lines).rstrip() + "\n"

    print(output_dir)

    out_folder = (
        Path(output_dir).absolute()
        if output_dir
        else Path(path_config).parent
        if path_config
        else Path(full_path_source)
    )
    out_folder.joinpath("conf.py").write_text(content, encoding="utf8")
    click.secho(f"Wrote conf.py to {out_folder}", fg="green")


# utility functions


def find_config_path(path: Path) -> Tuple[Path, bool]:
    """checks for any _config.yml file in current/parent dirs.
    if found then returns the path which has _config.yml,
    else returns the present dir as the path.
    """
    if path.is_dir():
        current_dir = path
    else:
        current_dir = path.parent

    if (current_dir / "_config.yml").is_file():
        return (current_dir, True)

    while current_dir != current_dir.parent:
        if (current_dir / "_config.yml").is_file():
            return (current_dir, True)
        current_dir = current_dir.parent

    if not path.is_dir():
        return (path.parent, False)
    return (path, False)


def builder_specific_actions(
    result, builder, output_path, cmd_type, page_name=None, print_func=print
):
    """Run post-sphinx-build actions.

    :param result: the result of the build execution; a status code or and exception
    """
    from jupyter_book.pdf import html_to_pdf
    from jupyter_book.sphinx import REDIRECT_TEXT

    if isinstance(result, Exception):
        msg = (
            f"There was an error in building your {cmd_type}. "
            "Look above for the cause."
        )
        # TODO ideally we probably only want the original traceback here
        raise RuntimeError(_message_box(msg, color="red", doprint=False)) from result
    elif result:
        msg = (
            f"Building your {cmd_type}, returns a non-zero exit code ({result}). "
            "Look above for the cause."
        )
        _message_box(msg, color="red", print_func=click.echo)
        sys.exit(result)

    # Builder-specific options
    if builder == "html":
        path_output_rel = Path(op.relpath(output_path, Path()))
        if cmd_type == "page":
            path_page = path_output_rel.joinpath(f"{page_name}.html")
            # Write an index file if it doesn't exist so we get redirects
            path_index = path_output_rel.joinpath("index.html")
            if not path_index.exists():
                path_index.write_text(REDIRECT_TEXT.format(first_page=path_page.name))

            _message_box(
                dedent(
                    f"""
                    Page build finished.
                        Your page folder is: {path_page.parent}{os.sep}
                        Open your page at: {path_page}
                    """
                )
            )

        elif cmd_type == "book":
            path_output_rel = Path(op.relpath(output_path, Path()))
            path_index = path_output_rel.joinpath("index.html")
            _message_box(
                f"""\
            Finished generating HTML for {cmd_type}.
            Your book's HTML pages are here:
                {path_output_rel}{os.sep}
            You can look at your book by opening this file in a browser:
                {path_index}
            Or paste this line directly into your browser bar:
                file://{path_index.resolve()}\
            """
            )
    if builder == "pdfhtml":
        print_func(f"Finished generating HTML for {cmd_type}...")
        print_func(f"Converting {cmd_type} HTML into PDF...")
        path_pdf_output = output_path.parent.joinpath("pdf")
        path_pdf_output.mkdir(exist_ok=True)
        if cmd_type == "book":
            path_pdf_output = path_pdf_output.joinpath("book.pdf")
            html_to_pdf(output_path.joinpath("index.html"), path_pdf_output)
        elif cmd_type == "page":
            path_pdf_output = path_pdf_output.joinpath(page_name + ".pdf")
            html_to_pdf(output_path.joinpath(page_name + ".html"), path_pdf_output)
        path_pdf_output_rel = Path(op.relpath(path_pdf_output, Path()))
        _message_box(
            f"""\
        Finished generating PDF via HTML for {cmd_type}. Your PDF is here:
            {path_pdf_output_rel}\
        """
        )
    if builder == "pdflatex":
        print_func(f"Finished generating latex for {cmd_type}...")
        print_func(f"Converting {cmd_type} latex into PDF...")
        # Convert to PDF via tex and template built Makefile and make.bat
        if sys.platform == "win32":
            makecmd = os.environ.get("MAKE", "make.bat")
        else:
            makecmd = os.environ.get("MAKE", "make")
        try:
            output = subprocess.run([makecmd, "all-pdf"], cwd=output_path)
            if output.returncode != 0:
                _error("Error: Failed to build pdf")
                return output.returncode
            _message_box(
                f"""\
            A PDF of your {cmd_type} can be found at:
                {output_path}
            """
            )
        except OSError:
            _error("Error: Failed to run: %s" % makecmd)
            return 1
