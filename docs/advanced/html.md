# Advanced HTML outputs


(custom-assets)=
## Custom CSS or JavaScript

If you'd like to include custom CSS rules or JavaScript scripts in your book, add them to a folder called `_static` in your book's folder.
Any files that end in `.css` or `.js` in this folder will automatically be copied into your built book HTML and linked in the header of each page.

For example, to include a custom CSS file `myfile.css` in a Jupyter Book folder with the following structure:

```
mybook/
├── _config.yml
├── _toc.yml
└── page1.md
```

Add the static file here:

```
├── _config.yml
├── _toc.yml
├── page1.md
└── _static
    └── myfile.css
```

The rules should then automatically be applied to your site. In general, these
CSS and JS files will be loaded *after* others are loaded on your page, so they
should overwrite pre-existing rules and behaviour.

### An Example: justify the text

If you want the text of your book to be justified instead of left aligned then create `myfile.css` under `mybook/_static` with the following CSS:

```css
p {
    text-align: justify;
}
```

(custom-admonitions)=
### An Example: custom admonitions

:::{warning}
Styling custom admonitions in this way is not officially supported by Jupyter Book or Sphinx, so its behavior may change unexpectedly.
A more verbose but "stable" approach is to use the `:class:` keyword argument when creating your admonitions, and defining CSS rules for that class.
:::

Currently, using the `{admonition}` directive with a title creates a CSS class based on the title of the admonition.
For example, an admonition title of `Here's my title` will result in a class name of `admonition-here-s-my-title`.

On the other hand, by using the `:class:` keyword argument, it will create a class with the keyword previously chosen.
For example, a custom class defined as `my-custom-class` will result in a class named as `my-custom-class`.

You can leverage either of these patterns to quickly create custom admonitions.
There is an example of each below.
In each case, begin by creating a `myadmonitions.css` file under `mybook/_static` and add CSS rules to it.

**Using the `{admonition}` directive with a title**

```css
div.admonition-extra-credit {
    border-left-color: rgba(0, 246, 16, 1);
}
div.admonition-extra-credit .admonition-title {
    background-color: rgba(0, 246, 16, .1);
}
div.admonition-extra-credit .admonition-title:before {
    color: rgba(0, 246, 16, 1);
    content: '\f19d';
}
```

Then, in your book, define an admonition like so:

````md
```{admonition} Extra credit
An "extra credit" exercise is presented here.
```
````

**Using the `:class:` keyword argument**

```css
div.extra-credit {
    border-left-color: rgba(var(--pst-color-success), 1);
}
div.extra-credit .admonition-title {
    background-color: rgba(var(--pst-color-success), .1)
}
div.extra-credit .admonition-title:before {
    color: rgba(var(--pst-color-success), 1);
    content: '\f19d';
}
```

Then, in your book, define an admonition like so:

````md
```{admonition} An extra exercise
:class: extra-credit
An "extra credit" exercise is presented here.
```
````

In both cases the admonitions should be styled according to your CSS rules when you build your book.

### An Example: add structured data for site name and search path

For HTML builds, structured data allows machines to better understand the content of your pages.
For instance Google Search can use structured data to understand your overall site's name, provide a search box that directly searches into your site, provide interactive experiences for flash cards or quizzes, etc.: see [Structured data markup that Google Search supports](https://developers.google.com/search/docs/appearance/structured-data/search-gallery).

You can easily provide structured data for your site's name using the [JSON for Linking Data (JSON-LD)](https://json-ld.org/) format and a few lines of Javascript to inject the JSON-LD data into your page. These can be directly added as a single file in the `_static` directory, as described in [](#custom-assets). For instance, you could name the file `structured_data.js`. Here is an example showing the site name and search path information for jupyterbook.org:

```javascript
var structuredData = {
"@context" : "https://schema.org",
"@type" : "WebSite",
"name" : "jupyter{book}",
"alternateName" : "JB",
"url" : "https://jupyterbook.org/",
"potentialAction": {
"@type": "SearchAction",
"target": {
  "@type": "EntryPoint",
  "urlTemplate": "https://jupyterbook.org/en/stable/search.html?q={search_term_string}"
},
"query-input": "required name=search_term_string"
}
};

const SDscript = document.createElement('script');
SDscript.setAttribute('type', 'application/ld+json');
SDscript.textContent = JSON.stringify(structuredData);
document.head.appendChild(SDscript);
```

To use this script for your own site, modify the `name`, `alternateName`, `url`, and `urlTemplate` based on your JupyterBook configuration. For the `urlTemplate`, it is easiest to conduct a search on your site and then extract the search path from the URL of the returned results.

## Enable Google Analytics

If you have a Google account, you can use Google Analytics to collect some
information on the traffic to your Jupyter Book. With this tool, you can find
out how many people are using your book, where they come from and how they
access it, whether they are using the desktop or the mobile version, etc.

To add Google Analytics to your Jupyter Book, navigate to [Google Analytics](https://analytics.google.com/analytics/web/), create a new Google Analytics account and create a new *property* for your Jupyter Book.
The next steps depend on the version of Google Analytics you are using:

- If using [Google Analytics 4](https://support.google.com/analytics/answer/10089681?hl=en) (GA4):
  - You will also have to create a *stream* associated with your property.
  - Choose to make a web stream and provide the URL of your Jupyter book.
  - Copy the **Measurement ID** associated with that stream.
  This is an alphanumeric code that looks like **`G-XXXXXXX`**.
- If using older versions of Google Analytics, such as Google Analytics 3:
  - You will provide your Jupyter Book's URL when you create your property.
  - Copy the analytics "**tracking ID**" for your property. This is a numeric code that looks like **`UA-XXXXXX-X`**.

Paste the measurement ID (GA4) or tracking ID (previous versions of Google
Analytics) into the following directive in your configuration file:

```yaml
html:
  analytics:
    google_analytics_id: G-XXXXXXX
```

:::{seealso}
- For more about Google Analytics, see [the Google Analytics documentation](https://analytics.google.com/analytics/web/) for more information.
:::


## Use Plausible Analytics

[Plausible Analytics](https://plausible.io) is a lightweight, open source, [privacy-focused](https://plausible.io/privacy-focused-web-analytics) analytics service that can be used as a more ethical alternative (or, in addition to) to Google Analytics.

Plausible Analytics requires a _domain_, which is given by the `plausible_analytics_domain` property:
```yaml
html:
  analytics:
    plausible_analytics_domain: my-domain
```
You can specify the analytics script that is loaded; by default, the bundle from <https://plausible.io> is used:
```yaml
html:
  analytics:
    plausible_analytics_domain: my-domain
    plausible_analytics_url: https://plausible.io/js/script.js
```

This should inject the appropriate code into the built site, and you will be able to get analytics on your website through either the commercial company-hosted dashboard, or a [self-hosted instance](https://plausible.io/docs/self-hosting).


(html:link-check)=
## Check external links in your book

If you'd like to make sure that the links outside of your book are valid,
run the Sphinx link checker with Jupyter Book. This will check each of your
external links and ensure that they resolve.

```{margin}
Note that you must ensure each link is
the *right* target, the link checker will only ensure that it resolves.
```

To run the link checker, use the following command:

```bash
jupyter-book build mybookname/ --builder linkcheck
```

It will print the status of each link in your book so that you may resolve
any incorrect links later on.

(raw-html-in-markdown)=
## Use raw HTML in Markdown

Jupyter Notebook Markdown allows you to use raw HTML in Markdown cells.
This is discouraged in most cases,
because it will usually just be passed through the build process as raw text, and so will not be subject to processes like:

- relative path corrections
- copying of assets to the build folder
- multiple output type formatting (e.g. it will not show in PDFs!).

So, for instance, below we add:

```md
<a href="../intro.md">Go Home HTML!</a>

[Go Home Markdown!](../intro.md)
```

and you will find that the HTML link is broken:

<a href="../intro.md">Go Home HTML!</a>

[Go Home Markdown!](../intro.md)

:::{tip}
Note that MyST Markdown now has some extended syntax features,
which can allow you to use certain HTML elements in the correct manner.

For example, the raw HTML image tag

```html
<img src="../images/fun-fish.png" alt="the fun fish!" width="200px"/>
```

becomes

<img src="../images/fun-fish.png" alt="the fun fish!" width="200px"/>

See the [image section](content-blocks-images) for details.
:::

## Adding extra HTML to your book

There are a few places in Jupyter Book where you can add extra arbitrary HTML.
In all cases, this is done with a configuration value in your `_config.yml` file.

### Extra HTML in your footer

To add extra HTML in your book's footer, use the following configuration:

```yaml
html:
    extra_footer: |
        <div>
            your html
        </div>
```

The contents of `extra_footer` will be inserted into your page's HTML after
all other footer content.

### Extra HTML to your left navbar

To add extra HTML in your book's left navbar, use the following configuration:

```yaml
html:
    extra_navbar: |
        <div>
            your html
        </div>
```

The contents of `extra_navbar` will be inserted into your page's HTML after
all other HTML content.

## Adding a license to your HTML footer

If you'd like to add a more detailed license for your book, or would like to
add a link to an external page for a license, the easiest way to do so is to
use a custom footer for this. You can disable the "copyright" text that is
automatically added to each footer, and add whatever footer HTML you'd like.

For example, see this configuration:

```yaml
html:
  extra_footer: |
    <p>
    ... Add license info here...
    </p>
sphinx:
  config:
    html_show_copyright: false
```

Note that this may not work in PDF builds of your page generated by LaTeX.


(sphinx:manual-assets)=
## Manually specify extra files/folders to be included in a website

Jupyter Book will copy over any files that are linked from within its pages so that the links work in the built website.
However, sometimes you'd like to manually ensure that files and folders are included in your built website.
For example, if you'd like to link to them from *outside* your built documentation, but not from within your built documentation.

To manually specify items to copy over, use the [`html_extra_path` Sphinx configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_extra_path).
You can configure this with Jupyter Book like so:

```yaml
sphinx:
  config:
    html_extra_path: ['folder1', 'folder2']
```

When you build your book's HTML, Jupyter Book will ensure that all files and folders _inside_ the folders specified in `html_extra_path` will be copied over to your built website.

For example, if you have a folder structure in your book like so:

```bash
assets
└── data
    └── mydataset.csv
```

and the following Jupyter Book configuration:

```yaml
sphinx:
  config:
    html_extra_path: ['assets']
```

Then the dataset will be accessible at `yourwebsite.com/data/mydataset.csv`.

## Configuring to Improve Accessibility

Declaring the primary language used in your book assists screen reader and browser translation tools.

Language can be configured by providing the appropriate [language code](https://www.w3schools.com/tags/ref_language_codes.asp) to the `language` option, under `sphinx` configuration in your `_config.yml` file:

```yaml
sphinx:
  config:
    language: en
```

This example will set the book language to English, which would be represented in your book's HTML as `<html lang="en">...</html>`.
