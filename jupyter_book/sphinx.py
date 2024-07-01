"""Tools for interacting with Sphinx."""

import os.path as op
import sys
from pathlib import Path
from typing import Union

from sphinx.application import Sphinx
from sphinx.cmd.build import handle_exception
from sphinx.util import logging
from sphinx.util.docutils import docutils_namespace, patch_docutils

from .config import get_final_config
from .pdf import update_latex_documents

REDIRECT_TEXT = """
<meta http-equiv="Refresh" content="0; url={first_page}" />
"""

ROOT = Path(__file__)
LOGGER = logging.getLogger(__name__)


def build_sphinx(
    sourcedir,
    outputdir,
    *,
    use_external_toc=True,
    confdir=None,
    path_config=None,
    noconfig=False,
    confoverrides=None,
    doctreedir=None,
    filenames=None,
    force_all=False,
    quiet=False,
    really_quiet=False,
    builder="html",
    freshenv=False,
    warningiserror=False,
    tags=None,
    verbosity=0,
    jobs=None,
    keep_going=False,
) -> Union[int, Exception]:
    """Sphinx build "main" command-line entry.

    This is a slightly modified version of
    https://github.com/sphinx-doc/sphinx/blob/3.x/sphinx/cmd/build.py#L198.

    """
    #######################
    # Configuration creation
    sphinx_config, config_meta = get_final_config(
        user_yaml=Path(path_config) if path_config else None,
        cli_config=confoverrides or {},
        sourcedir=Path(sourcedir),
        use_external_toc=use_external_toc,
    )

    ##################################
    # Preparing Sphinx build arguments

    # Configuration directory
    if noconfig:
        confdir = None
    elif not confdir:
        confdir = sourcedir

    # Doctrees directory
    if not doctreedir:
        doctreedir = Path(outputdir).parent.joinpath(".doctrees")

    if jobs is None:
        jobs = 1

    # Manually re-building files in filenames
    if filenames is None:
        filenames = []
    missing_files = []
    for filename in filenames:
        if not op.isfile(filename):
            missing_files.append(filename)
    if missing_files:
        raise IOError("cannot find files %r" % missing_files)

    if force_all and filenames:
        raise ValueError("cannot combine -a option and filenames")

    # Debug args (hack to get this to pass through properly)
    def debug_args():
        pass

    debug_args.pdb = False
    debug_args.verbosity = False
    debug_args.traceback = False

    # Logging behavior
    status = sys.stdout
    warning = sys.stderr
    error = sys.stderr
    if quiet:
        status = None
    if really_quiet:
        status = warning = None

    ###################
    # Build with Sphinx
    app = None  # In case we fail, this allows us to handle the exception
    try:
        # These patches temporarily override docutils global variables,
        # such as the dictionaries of directives, roles and nodes
        # NOTE: this action is not thread-safe and not suitable for asynchronous use!
        with patch_docutils(confdir), docutils_namespace():
            app = Sphinx(
                srcdir=sourcedir,
                confdir=confdir,
                outdir=outputdir,
                doctreedir=doctreedir,
                buildername=builder,
                confoverrides=sphinx_config,
                status=status,
                warning=warning,
                freshenv=freshenv,
                warningiserror=warningiserror,
                tags=tags,
                verbosity=verbosity,
                parallel=jobs,
                keep_going=keep_going,
            )

            # We have to apply this update after the sphinx initialisation,
            # since default_latex_documents is dynamically generated
            # see sphinx/builders/latex/__init__.py:default_latex_documents
            new_latex_documents = update_latex_documents(
                app.config.latex_documents, config_meta["latex_doc_overrides"]
            )
            app.config.latex_documents = new_latex_documents

            # set the below flag to always to enable maths in singlehtml builder
            if app.builder.name == "singlehtml":
                app.set_html_assets_policy("always")

            # setting up sphinx-multitoc-numbering
            if app.config["use_multitoc_numbering"]:
                # if sphinx-external-toc is used
                if "external_toc_path" in app.config:
                    import yaml

                    site_map = app.config.external_site_map
                    site_map_str = yaml.dump(site_map.as_json())

                    # only if there is at least one numbered: true in the toc file
                    if "numbered: true" in site_map_str:
                        app.setup_extension("sphinx_multitoc_numbering")
                else:
                    app.setup_extension("sphinx_multitoc_numbering")

            # Build latex_doc tuples based on --individualpages option request
            if config_meta["latex_individualpages"]:
                from .pdf import autobuild_singlepage_latexdocs

                # Ask Builder to read the source files to fetch titles and documents
                app.builder.read()
                latex_documents = autobuild_singlepage_latexdocs(app)
                app.config.latex_documents = latex_documents

            app.build(force_all, filenames)

            return app.statuscode

    except (Exception, KeyboardInterrupt) as exc:
        handle_exception(app, debug_args, exc, error)
        return exc
