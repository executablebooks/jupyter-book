"""Commands to facilitate conversion to PDF."""

import asyncio
import os
from copy import copy
from pathlib import Path

from .utils import _error, _message_box

# LaTeX Documents Tuple Spec
LATEX_DOCUMENTS = (
    "startdocname",
    "targetname",
    "title",
    "author",
    "theme",
    "toctree_only",
)


def html_to_pdf(html_file, pdf_file):
    """
    Convert arbitrary HTML file to PDF using pyppeteer.

    Parameters
    ----------
    html_file : str
        A path to an HTML file to convert to PDF
    pdf_file : str
        A path to an output PDF file that will be created
    """
    asyncio.get_event_loop().run_until_complete(_html_to_pdf(html_file, pdf_file))


async def _html_to_pdf(html_file, pdf_file):
    try:
        from pyppeteer import launch
    except ImportError:
        _error(
            "Generating PDF from book HTML requires the pyppeteer package. "
            "Install it first.",
            ImportError,
        )
    browser = await launch(args=["--no-sandbox"])
    page = await browser.newPage()

    # Absolute path is needed
    html_file = Path(html_file).resolve()

    # Waiting for networkidle0 seems to let mathjax render
    await page.goto(f"file:///{html_file}", {"waitUntil": ["networkidle2"]})
    # Give it *some* margins to make it look a little prettier
    # I just made these up
    page_margins = {"left": "0in", "right": "0in", "top": ".5in", "bottom": ".5in"}
    await page.addStyleTag(
        {
            "content": """
                div.cell_input {
                    -webkit-column-break-inside: avoid;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                div.cell_output {
                    -webkit-column-break-inside: avoid;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
         """
        }
    )
    await page.pdf({"path": pdf_file, "margin": page_margins})
    await browser.close()


def update_latex_documents(latex_documents, latexoverrides):
    """
    Apply latexoverrides from _config.yml to latex_documents tuple
    """

    if len(latex_documents) > 1:
        _message_box(
            "Latex documents specified as a multi element list in the _config",
            "This suggests the user has made custom settings to their build",
            "[Skipping] processing of automatic latex overrides",
        )
        return latex_documents

    # Extract latex document tuple
    latex_document = latex_documents[0]
    # Apply single overrides from _config.yml
    updated_latexdocs = []
    for loc, item in enumerate(LATEX_DOCUMENTS):
        # the last element toctree_only seems optionally included
        if loc >= len(latex_document):
            break
        if item in latexoverrides.keys():
            updated_latexdocs.append(latexoverrides[item])
        else:
            updated_latexdocs.append(latex_document[loc])
    return [tuple(updated_latexdocs)]


def latex_document_components(latex_documents):
    """Return a dictionary of latex_document components by name"""
    latex_tuple_components = {}
    for idx, item in enumerate(LATEX_DOCUMENTS):
        # skip if latex_documents doesn't doesn't contain all elements
        # of the LATEX_DOCUMENT specification tuple
        if idx >= len(latex_documents):
            continue
        latex_tuple_components[item] = latex_documents[idx]
    return latex_tuple_components


def latex_document_tuple(components):
    """Return a tuple for latex_documents from named components dictionary"""
    latex_doc = []
    for item in LATEX_DOCUMENTS:
        if item not in components.keys():
            continue
        else:
            latex_doc.append(components[item])
    return tuple(latex_doc)


def autobuild_singlepage_latexdocs(app):
    """
    Build list of tuples for each document in the Project

    [((startdocname, targetname, title, author, theme, toctree_only))]

    https://www.sphinx-doc.org/en/3.x/usage/configuration.html#confval-latex_documents
    """
    latex_documents = app.config.latex_documents
    if len(latex_documents) > 1:
        _message_box(
            "Latex documents specified as a multi element list in the _config",
            "This suggests the user has made custom settings to their build",
            "[Skipping] --individualpages option",
        )
        return latex_documents

    # Extract latex_documents updated tuple
    latex_documents = latex_documents[0]

    titles = app.env.titles
    master_doc = app.config.master_doc
    sourcedir = os.path.dirname(master_doc)

    # Construct Tuples
    DEFAULT_VALUES = latex_document_components(latex_documents)
    latex_documents = []
    for doc, title in titles.items():
        latex_doc = copy(DEFAULT_VALUES)

        # if doc has a subdir relative to src dir
        docname = None
        parts = Path(doc).parts

        latex_doc["startdocname"] = doc
        if DEFAULT_VALUES["startdocname"] == doc:
            targetdoc = DEFAULT_VALUES["targetname"]
        else:
            if sourcedir in parts:
                parts = list(parts)
                # assuming we need to remove only the first instance
                parts.remove(sourcedir)
            docname = "-".join(parts)
            targetdoc = docname + ".tex"

        latex_doc["targetname"] = targetdoc
        latex_doc["title"] = title.astext()
        latex_doc = latex_document_tuple(latex_doc)
        latex_documents.append(latex_doc)

    return latex_documents
