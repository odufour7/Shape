"""Shapes project documentation build configuration file."""

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))
smartquotes = False

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "shapes"
copyright = "2025, The SHAPE project"
author = "Oscar Maxime Alexandre"
# release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Google style docstrings. Please, ensure that napoleon is loaded before autodoc-typehints
    "sphinx_autodoc_typehints",  # Type hints are rendered as links
    "sphinx.ext.intersphinx",  # For linking to other projects' documentation
    "nbsphinx",  # For Jupyter notebook support
    "myst_nb",  # Optional: For MyST Markdown notebooks
    "nbsphinx_link",  # Optional: For linking to notebooks
]

templates_path = ["_templates"]
# exclude_patterns = []
language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_logo = "_static/README/art_light.png"

suppress_warnings = ["config.cache"]

napoleon_use_param = True  # Enable parameter type annotations in docstrings
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
