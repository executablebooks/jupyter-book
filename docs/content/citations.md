(content:citations)=
# Citations and bibliographies

:::{warning}
If you are using `docutils>=0.18,<20` then the page containing the `bibliography` directive
will not have the correct layout. While `docutils` is patched we recommend using `docutils==0.17.1`
which can be installed by:

```bash
pip install docutils==0.17.1
```

This is due to [this issue](https://sourceforge.net/p/docutils/patches/195/)
:::


You can add citations and bibliographies using references that are stored in a `bibtex` file that is in your book's folder. You can then add a citation in-line in your Markdown with the `{cite}` role, and include the bibliography from your bibtex file with the `{bibliography}` directive.

```{seealso}
This functionality uses the excellent [sphinxcontrib-bibtex](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/) extension.
```

## Basic citations

To get started with citations in Jupyter Book, check out [](tutorials:references).

## Change the in-line citation style

There are a few alternatives roles that you can use to change the in-line citation style. Below are a few examples:

- The citation `` {cite:p}`perez2011python` `` results in {cite:p}`perez2011python`
- The citation `` {cite:t}`perez2011python` `` results in {cite:t}`perez2011python`
- The citation `` {cite:ps}`perez2011python` `` results in {cite:ps}`perez2011python`
- The citation `` {cite:ts}`perez2011python` `` results in {cite:ts}`perez2011python`

:::{seealso}
For a more complete list of in-line citation styles, check out [the `sphinxcontrib-bibtex` docs](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#roles-and-directives).
:::

## Select your bibliography style

You can also optionally customize the style of your references.
By default, references are displayed in the `alpha` style.
Other currently supported styles include `plain`, `unsrt`, and `unsrtalpha`.
These styles create the following bibliography formatting:

* `alpha`: Use alphanumeric reference labels, citations are sorted by author, year.
* `plain`: Use numeric reference labels, citations are sorted by author, year.
* `unsrt`: Use numeric reference labels, citations are sorted by order of appearance.
* `unsrtalpha`: Use alphanumeric reference labels, citations are sorted by order of appearance.

To set your reference style, use the style option:

````md
```{bibliography}
:style: unsrt
```
````

## Change the reference style

To set the reference style, use the `bibtex_reference_style` field in your book's `_config.yml` file.

```yaml
# In _config.yml
sphinx:
  config:
    bibtex_reference_style: author_year
    bibtex_bibfiles: "your_reference_file.bib"
```

There are a few options for your in-line citation style such as `label`, `super`, and `author-year`.

:::{seealso}
For a list of configuration options and more detail about this, see [the `sphinxcontrib-bibtex` docs](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#referencing-style)
:::

## Local bibliographies

You may wish to include a bibliography listing at the end of each document
rather than having a single bibliography contained in a separate document.
Having multiple bibliography directives, however, can cause `sphinx` to issue
`duplicate citation warnings`.

A common fix is to add a filter to the bibliography directives:

````md
```{bibliography}
:filter: docname in docnames
```
````

See `sphinxcontrib-bibtex` documentation on [local bibliographies](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#section-local-bibliographies).

### Citing a work in different documents
When you want cite a document in several documents then the Sphinx `keyprefix` system should be used.

As an example, suppose you wish to cite `Orwell1984` in two documents and have the bibliography entries showing in both documents. In one document you could use:

````md
..."If you want to keep a secret, you must also hide it from yourself"{cite}`a-Orwell1984`
````

with the following bibliography section code:

````md
```{bibliography}
:filter: docname in docnames
:labelprefix: A
:keyprefix: a-
```
````
In the second document you could use:

````md
..."Freedom is slavery."{cite}`b-Orwell1984`


...

```{bibliography}
:filter: docname in docnames
:labelprefix: B
:keyprefix: b-
```
````

See `sphinxcontrib-bibtex` documentation on [Key Prefixing](https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#section-key-prefixing).

(citations/bibliography)=
## Example Bibliography

An example bibliography, for reference:

```{bibliography}
```
