# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath("../"))


# -- Project information -----------------------------------------------------

project = 'Pyscandl'
copyright = '2020, Thomas MONTERO | _Ara0n_'
author = 'Thomas MONTERO | _Ara0n_'

# The full version, including alpha/beta/rc tags
release = '2.0.0'


# -- General configuration ---------------------------------------------------

# sets the good master doc
master_doc = 'index'
source_suffix = ".rst"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "venv/*"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'nature'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# generate the help the help toggle it on when you changed stuff in the docstrings
def generate():
    import argparse

    from modules.arg_parser import get_parser

    parser = get_parser()
    parser.prog = "main.py"

    subparsers = [
        subparser
        for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
        for _, subparser in action.choices.items()
    ]
    subsubparsers = []
    for subparser in subparsers:
        subsubparsers += [
            subsubparser
            for action in subparser._actions
            if isinstance(action, argparse._SubParsersAction)
            for _, subsubparser in action.choices.items()
        ]

    with open("CLI help/main.txt", "w") as file:
        parser.print_help(file)

    for subparser in subparsers:
        with open(f"CLI help/{subparser.prog.split()[1]}.txt", "w") as file:
            subparser.print_help(file)

    for subsubparser in subsubparsers:
        with open(f"CLI help/{' '.join(subsubparser.prog.split()[1:])}.txt", "w") as file:
            subsubparser.print_help(file)


generate()
