# from pathlib import Path

import jsonschema
import pytest
import sphinx as sphinx_build

from jupyter_book.cli.main import sphinx
from jupyter_book.config import get_final_config, validate_yaml

pytest_plugins = "pytester"
SPHINX_VERSION = f".sphinx{sphinx_build.version_info[0]}"


@pytest.mark.parametrize(
    "user_config",
    [
        {},
        {"title": "hallo"},
        {"html": {"extra_footer": ""}},
        {"execute": {"execute_notebooks": "cache"}},
        {
            "parse": {
                "myst_enable_extensions": ["linkify"],
                "myst_dmath_double_inline": True,
            }
        },
        {"latex": {"latex_documents": {"targetname": "book.tex", "title": "other"}}},
        {"launch_buttons": {"binderhub_url": "other"}},
        {"repository": {"url": "other"}},
        {"exclude_patterns": ["new"]},
        {
            "sphinx": {
                "extra_extensions": ["other"],
                "local_extensions": {"helloworld": "./ext"},
                "config": {
                    "html_theme_options": {
                        "launch_buttons": {"binderhub_url": "other"},
                        "analytics": {"google_analytics_id": ""},
                    },
                    "html_theme": "other",
                    "new": "value",
                },
            }
        },
        {
            "sphinx": {
                "extra_extensions": ["other"],
                "local_extensions": {"helloworld": "./ext"},
                "recursive_update": True,
                "config": {
                    "html_theme_options": {
                        "launch_buttons": {"binderhub_url": "other"}
                    },
                    "html_theme": "other",
                    "new": "value",
                },
            }
        },
    ],
    ids=[
        "empty",
        "title",
        "html.extra_footer",
        "execute.method",
        "extended_syntax",
        "latex_doc",
        "launch_buttons",
        "repository",
        "exclude_patterns",
        "sphinx-default",
        "sphinx-recurse",
    ],
)
def test_get_final_config(user_config, data_regression):
    cli_config = {"latex_individualpages": False}
    final_config, metadata, _ = get_final_config(
        user_yaml=user_config,
        cli_config=cli_config,
        validate=True,
        raise_on_invalid=True,
    )
    data_regression.check(
        {"_user_config": user_config, "final": final_config, "metadata": metadata}
    )


def test_validate_yaml():
    with pytest.raises(jsonschema.ValidationError):
        validate_yaml({"title": 1}, raise_on_errors=True)
    assert "Warning" in validate_yaml({"title": 1}, raise_on_errors=False)
    assert validate_yaml({"title": ""}, raise_on_errors=False) is None


def test_config_sphinx_command_only_build_toc_files(
    cli, temp_with_override, file_regression
):
    temp_with_override.joinpath("_config.yml").write_text(
        "only_build_toc_files: True\n", encoding="utf8"
    )
    temp_with_override.joinpath("_config.yml").write_text(
        "exclude_patterns: [test_config/*]\n", encoding="utf8"
    )

    temp_with_override.joinpath("_toc.yml").write_text("root: intro\n", encoding="utf8")
    cli.invoke(sphinx, temp_with_override.as_posix())

    assert temp_with_override.joinpath("conf.py").exists()
    output = temp_with_override.joinpath("conf.py").read_text(encoding="utf8")
    file_regression.check(output, encoding="utf8")


def test_config_sphinx_command(cli, temp_with_override, file_regression):
    temp_with_override.joinpath("_config.yml").write_text(
        "title: test\n", encoding="utf8"
    )
    temp_with_override.joinpath("_toc.yml").write_text("root: intro\n", encoding="utf8")
    cli.invoke(sphinx, temp_with_override.as_posix())
    assert temp_with_override.joinpath("conf.py").exists()
    output = temp_with_override.joinpath("conf.py").read_text(encoding="utf8")
    file_regression.check(output, encoding="utf8")


def test_tags_sphinx_command(cli, build_resources):
    books, _ = build_resources
    path_b = books.joinpath("config")
    path_c = path_b.joinpath("_config_twotag.yml")
    result = cli.invoke(sphinx, arg=[path_b.as_posix(), path_c.as_posix()])
    assert result
    assert path_b.joinpath("conf.py").exists()
    output = path_b.joinpath("conf.py").read_text(encoding="utf8")
    assert "tags.add('cowboy')" in output
    assert "tags.add('cowgirl')" in output
    assert "tags.remove('rustler')" in output


# TODO sphinx-external-toc now handles appending to exclude_patterns
# but we may want to add similar tests there, checking the output of exclude_patterns

# @pytest.mark.parametrize(
#     "toc_file, filename",
#     [("p.md", "p.md"), ("p", "p.md"), ("[]p", "[]p.md"), ("[t]p.md", "[t]p.md")],
# )
# def test_only_build_toc_files(testdir, toc_file, filename):
#     cli_config = {"latex_individualpages": False}
#     toc = Path("toc.yml")
#     toc.write_text(f"- file: '{toc_file}'\n")
#     Path(filename).write_text("")
#     Path("exclude.md").write_text("")
#     user_config = {"only_build_toc_files": True}

#     final_config, metadata, _ = get_final_config(
#         user_yaml=user_config,
#         cli_config=cli_config,
#         validate=True,
#         raise_on_invalid=True,
#     )

#     assert "exclude.md" in final_config["exclude_patterns"]
#     assert filename not in final_config["exclude_patterns"]


# def test_only_build_toc_files_with_exclude_patterns(testdir):
#     cli_config = {"latex_individualpages": False}
#     toc = Path("toc.yml")
#     toc.write_text("- file: landing\n")
#     Path("landing.md").write_text("")
#     Path("exclude.md").write_text("")
#     user_config = {
#         "only_build_toc_files": True,
#         "exclude_patterns": ["my/*", "patterns"],
#     }

#     final_config, metadata, _ = get_final_config(
#         user_yaml=user_config,
#         cli_config=cli_config,
#         validate=True,
#         raise_on_invalid=True,
#     )

#     assert "exclude.md" in final_config["exclude_patterns"]
#     assert "my/*" in final_config["exclude_patterns"]
#     assert "patterns" in final_config["exclude_patterns"]
#     assert "landing.md" not in final_config["exclude_patterns"]


# def test_only_build_toc_files_non_default_source_dir(testdir):
#     cli_config = {"latex_individualpages": False}
#     toc = Path("toc.yml")
#     toc.write_text("- file: landing\n")
#     sourcedir = Path("s")
#     subdir = sourcedir / "subdir"
#     subdir.mkdir(parents=True)
#     Path(sourcedir / "landing.md").write_text("")
#     Path(sourcedir / "exclude.md").write_text("")
#     Path(subdir / "sub.md").write_text("")
#     user_config = {"only_build_toc_files": True}

#     final_config, metadata, _ = get_final_config(
#         user_yaml=user_config,
#         cli_config=cli_config,
#         validate=True,
#         raise_on_invalid=True,
#         sourcedir=sourcedir,
#     )

#     assert "exclude.md" in final_config["exclude_patterns"]
#     assert "subdir/sub.md" in final_config["exclude_patterns"]
#     assert "landing.md" not in final_config["exclude_patterns"]


# def test_only_build_toc_files_missing_toc(testdir):
#     cli_config = {"latex_individualpages": False}
#     user_config = {"only_build_toc_files": True}

#     with pytest.raises(ValueError, match=r".*you must have a toc.*"):
#         get_final_config(
#             user_yaml=user_config,
#             cli_config=cli_config,
#             validate=True,
#             raise_on_invalid=True,
#         )


def test_get_final_config_custom_myst_extensions(data_regression):
    cli_config = {"latex_individualpages": False}
    user_config = {"parse": {"myst_extra_extensions": ["linkify"]}}
    final_config, metadata, _ = get_final_config(
        user_yaml=user_config,
        cli_config=cli_config,
        validate=True,
        raise_on_invalid=True,
    )
    data_regression.check(
        {"_user_config": user_config, "final": final_config, "metadata": metadata}
    )


def test_get_final_config_bibtex(data_regression):
    cli_config = {"latex_individualpages": False}
    user_config = {"bibtex_bibfiles": ["tmp.bib"]}
    final_config, metadata, _ = get_final_config(
        user_yaml=user_config,
        cli_config=cli_config,
        validate=True,
        raise_on_invalid=True,
    )
    assert "sphinxcontrib.bibtex" in final_config["extensions"]


def test_mathjax_config_warning(data_regression):
    mathjax_config = {
        "sphinx": {
            "config": {
                "mathjax_config": {"TeX": {"Macros": {"argmax": "arg\\,max"}}},
            }
        }
    }
    cli_config = {"latex_individualpages": False}
    user_config = mathjax_config
    final_config, metadata, _ = get_final_config(
        user_yaml=user_config,
        cli_config=cli_config,
        validate=True,
        raise_on_invalid=True,
    )
    data_regression.check(
        {"_user_config": user_config, "final": final_config, "metadata": metadata},
        basename=f"test_mathjax_config_warning{SPHINX_VERSION}",
    )


def test_mathjax_config_warning_mathjax2path(data_regression):
    mathjax_config = {
        "sphinx": {
            "config": {
                "mathjax_config": {"TeX": {"Macros": {"argmax": "arg\\,max"}}},
                "mathjax_path": "https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS-MML_CHTML",  # noqa: E501
            }
        }
    }

    cli_config = {"latex_individualpages": False}
    user_config = mathjax_config
    final_config, metadata, _ = get_final_config(
        user_yaml=user_config,
        cli_config=cli_config,
        validate=True,
        raise_on_invalid=True,
    )
    data_regression.check(
        {"_user_config": user_config, "final": final_config, "metadata": metadata},
        basename=f"test_mathjax_config_warning_mathjax2path{SPHINX_VERSION}",
    )
