<!-- START_GENERAL_DOCS -->
# Service-Kit Documentation

![License](https://img.shields.io/github/license/guardicode/service-kit)


 📌 Service-Kit is a collection of functions and objects designed to help the
Monkey team bootstrap, build, and maintain various services efficiently.

## Features

- **Service Bootstrapping**: Provides templates and utilities to stand up
new services quickly.
- **Common Utilities**: Provides common utilities for logging, configuration,
and error handling.
- **Service Configuration**: Provides a base class for service
configuration that can be easily extended.
- **Testing Support**: Provides utilities for testing services.

### Submodules

- **api**: Provides components for setting up an API with FastAPI
- **base_model**: Provides a Pydantic BaseModel with extra features
- **configuration**: Provides models, types, and utilities for configuring a service
- **errors**: Enables exceptions using structured errors
- **logging**: Provides a logger that enables structured logging
- **testing**: Provides useful pytest fixtures


## Getting started

### Installation

You can install Service-Kit using [poetry](https://python-poetry.org/):

```bash
$ poetry add git+https://github.com/guardicode/service-kit.git
```

or by using pip:

```bash
$ pip install git+https://github.com/guardicode/service-kit.git
```

### Usage

After installation, you can start using Service-Kit like any other Python package.
For a more detailed example and usage patterns, refer to the
`template_service.py` file included in the repository.

<!-- END_GENERAL_DOCS -->
<!-- START_DEV_DOCS -->
## Development

### Setting up your development environment

Run the following commands to install the necessary prerequisites:

```bash
$ pip install poetry pre-commit
$ poetry install --all-extras
$ pre-commit install -t pre-commit -t prepare-commit-msg
```

### Running unit tests

Run automated tests with:

```bash
$ poetry run pytest
```


#### Test coverage

To run automated tests with test coverage, run:

```bash
$ poetry run pytest --cov-report=html --cov=service-kit
$ firefox ./htmlcov/index.html
```

### Sphinx Documentation

The `docs` directory contains the needed file to automatically generate code documentation using Sphinx.

#### Configuration

To change the Sphinx configuration, change the attributes in `source/conf.py`.
The documentation uses `source/_static` to keep the custom media, stylesheets, js scripts etc.
`source/index.rst` is the main rst file in which the look of the index HTML page is defined.

#### Build

The make script generates the documentation using sphinx-build.
The generated documentation is stored in `build/html/`.

##### Linux

1. From `service-kit`, install python dependencies:

```bash
$ poetry install
```

1. Activate the python venv

```bash
$ poetry env activate
```

1. Generate the documentation:

```bash
$ cd docs
$ make html
```


##### Windows

1. From `service-kit`, install python dependencies:

```bash
$ poetry install
```

1. Activate the python venv

```bash
$ poetry env activate
```

1. Generate the documentation:

```bash
$ cd docs
$ make html
```


#### Deployment

To deploy the documentation locally, `build/html/index.html`
<!-- END_DEV_DOCS -->
