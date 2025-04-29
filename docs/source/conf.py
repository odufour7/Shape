"""Shapes project documentation build configuration file."""

# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# Add the source directory to sys.path so Sphinx can find your modules
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
    "sphinx.ext.todo",  # Support for TODO comments
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.autodoc",  # Automatically document modules/classes/functions
    "sphinx.ext.napoleon",  # Support for NumPy/Google style docstrings
    "sphinx_autodoc_typehints",  # Render type hints as links in docs
    "sphinx.ext.intersphinx",  # Link to external documentation (e.g., Python)
    "nbsphinx",  # Support for Jupyter notebooks
    "myst_parser",
    "sphinx.ext.mathjax",
    "nbsphinx_link",  # Optional: Linking to external notebooks
    "breathe",  # For C++ documentation via Doxygen
    "exhale",  # For automatic API documentation tree with c++
]

templates_path = ["_templates"]
# exclude_patterns = []  # List of patterns to ignore when looking for source files
language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # Use the Read the Docs theme
html_static_path = ["_static"]  # Path to custom static files (e.g., CSS)
html_css_files = ["custom.css"]  # Custom CSS file for styling
html_logo = "_static/logo/art_light.png"  # Logo for the documentation

suppress_warnings = ["config.cache"]

# -- Napoleon settings -------------------------------------------------------
napoleon_use_param = True  # Enable parameter type annotations in docstrings

# -- Intersphinx settings ----------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),  # Link to Python standard library docs
    "shapely": ("https://shapely.readthedocs.io/en/stable/", None),  # Link to Shapely documentation
    "plotly": ("https://plotly.com/python-api-reference/", None),  # Link to Plotly documentation
    "numpy": ("https://numpy.org/doc/stable/", None),  # Link to NumPy documentation
    "cppreference": ("https://en.cppreference.com/w/", None),  # Link to C++ reference
}

# -- Autodoc settings --------------------------------------------------------
autodoc_default_options = {
    "members": True,  # Include class members (methods, attributes)
    "undoc-members": True,  # Include undocumented members in the output
    "private-members": False,  # Exclude private members (those starting with _)
}

autodoc_typehints = "description"  # Render type hints in the description instead of signatures

# # -- Breathe configuration ---------------------------------------------------

# breathe_projects = {"shapes_cpp": os.path.abspath("../doxyoutput/xml")}
# breathe_default_project = "shapes_cpp"

# # -- Exhale configuration ----------------------------------------------------

# exhale_args = {
#     # Folder where API .rst files will be generated
#     "containmentFolder": "./api",
#     "rootFileName": "library_root.rst",
#     "rootFileTitle": "C++ API Reference",
#     "doxygenStripFromPath": "..",
#     "createTreeView": True,
# }

# # -- Sphinx C++ domain settings ----------------------------------------------

# primary_domain = "cpp"
# highlight_language = "cpp"
