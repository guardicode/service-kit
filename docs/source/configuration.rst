Service-Kit Configuration
=========================

The ``ServiceConfiguration`` class is a pydantic class that is used to configure the service
that is being built. The fields of the class are the ones that are common while setting
up a service.
If you want to extend the configuration class, you can do so by creating a new class that
inherits from the ``ServiceConfiguration`` class and add the needed fields.
The configuration class needs to be used in the ``setup`` method of the service similar to
what we have in the `template_service.py`_.

.. _template_service.py: https://github.com/guardicode/service-kit/blob/main/template_service.py

To set these fields for the service, you can provide the configuration options as
as environment variables or in a `.env` file. See
https://pypi.org/project/python-dotenv/#file-format for more details on `.env`
file format.


.. autopydantic_settings:: service_kit.configuration.service_configuration.ServiceConfiguration
   :no-index:
