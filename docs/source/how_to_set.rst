How to Set Up a GitHub Repository with `service-kit`
====================================================

This guide will show you how to set up a GitHub repository with the `service-kit` package.
You can either use the **cookiecutter** template or set up the project manually.
We will also cover how to create a project with Cookiecutter, how to install `service-kit` in `pyproject.toml`,
modify `template_service.py`, and run the project to verify that the "hello-world" feature is present.

Prerequisites
-------------
- Python 3.8 or higher
- Poetry installed
- Git installed

Steps
-----

Set up project using Cookiecutter Template
--------------------------------------------

1. **Install** ``cookiecutter`` **if you don’t have it:**

   If you don’t have ``cookiecutter`` installed, you can install it with:

   .. code-block:: bash

      pip install cookiecutter


   If you have any issues with the installation, refer to the ``cookiecutter`` documentation for more information:
   https://cookiecutter.readthedocs.io/en/stable/index.html

2. **Create a New Repository Using the Template**:

   Run the following command to generate the new project structure:

   .. code-block:: bash

      cookiecutter https://github.com/guardicode/infection-monkey-cookiecutter

   During the process, you will be asked to fill in some prompts (such as project name, description, etc.). Fill these in as needed.

3. **Navigate to the Newly Created Repository**:

   .. code-block:: bash

      cd <your-project-name>


4. **Install Service-Kit**:

   Install the `service-kit` package using `poetry`:

   .. code-block:: bash

      poetry add git+https://github.com/guardicode/service-kit.git


Modify `template_service.py`
-----------------------------

1. **Copy** ``template_service.py`` **to your Project**:

   In Service-Kit project, there is a file named `template_service.py`_.
   Copy this file to your project package directory.

   .. _template_service.py: https://github.com/guardicode/service-kit/blob/main/template_service.py

2. **Modify the Template**:

   Open ``template_service.py`` in your preferred editor. It is a Jinja template, so you can modify it as needed.
   Modify the following:

      - **PROJECT_NAME**: Replace this with your project name.
      - **ENTRYPOINT**: Choose the entrypoint for your project.
      - **POST /echo/{customer_id}**: Remove the Jinja conditional statement and leave the endpoint as is.

Run the Project
---------------

1. **Run the template service**:

   Now, you should be able to run your project. From the root of the project directory, run the following:

   .. code-block:: bash

      poetry run python <project_name>/template_service.py

   This will execute the script and you should see output like:

   .. code-block::

      2025-02-28 16:09:36.890 | INFO     | service_kit.api.api_utils:launch_uvicorn:44 - Starting service-how-to...
      INFO:     Started server process [37206]
      INFO:     Waiting for application startup.
      2025-02-28 16:09:36.914 | CRITICAL | service_kit_how_to.template_service:setup:60 - bind_address=IPv4Address('127.0.0.1') debug=False enable_hot_reload=False log_directory=None log_level=<LogLevel.INFO: 'INFO'> port=8080 pretty_print_logs=True ssl_certfile=None ssl_keyfile=None

2. **Verify the** ``POST /echo/{customer_id}`` **endpoint**:

   Open a new terminal and run the following command:

   .. code-block:: bash

      curl -X POST 'http://127.0.0.1:8080/echo/hello-world'

   You should see the following output:

   .. code-block::

      "hello-world"%

Conclusion
----------

You’ve now successfully set up a GitHub repository for your project using either the **cookiecutter template**.
You installed `service-kit` via `pyproject.toml` using a GitHub link, modified `template_service.py`, and ran the project successfully with the "Hello-World" output.
