# Service-Kit Code Documentation

This directory contains the needed file to automatically generate code documentation using Sphinx.

# Configuration

To change the sphinx configuration change the attributes at `source/conf.py`.
The documentation uses `source/_static` as a folder where we keep the custom media, stylesheets, js scripts etc.
`source/index.rst` is the main rst file in which we define the look of the index HTML page.

# Building Documentation

The make script generates the documentation using sphinx-build
The generated documentation is stored in `build/html` folder.

## Linux

1. From `service-kit`, install python dependencies:
    - `poetry install`

1. Activate the python venv

    - `poetry shell`

1. Generate the documentation:
    - `cd docs`
    - `make html`


## Windows

1. From `service-kit`, install python dependencies:
    - `poetry install`

1. Activate the python venv

    - `poetry shell`

1. Generate the documentation:
   - `cd docs`
   - `make.bat html`


# Deployment

To deploy the documentation locally open the `index.html` file in the `build/html` folder.
