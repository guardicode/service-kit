Service-Kit Configuration
=========================

The ``ServiceConfiguration`` class is a Pydantic model that defines common configuration fields
for setting up a service. This configuration class can be extended by creating a new class that
inherits from ``ServiceConfiguration``, and adding the required fields. The configuration class
should be used in the service's ``setup`` method, as demonstrated in
[`template_service.py`](https://github.com/guardicode/service-kit/blob/main/template_service.py).

.. _template_service.py: https://github.com/guardicode/service-kit/blob/main/template_service.py

You can set these configuration fields via environment variables or a `.env` file. For details on
the `.env` file format, refer to
[python-dotenv documentation](https://pypi.org/project/python-dotenv/#file-format).

.. autopydantic_settings:: service_kit.configuration.service_configuration.ServiceConfiguration
   :no-index:
