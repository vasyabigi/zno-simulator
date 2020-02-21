import os
import requests

from django.core.exceptions import ImproperlyConfigured

from .common import *  # noqa F401


DEBUG = False


def get_env_variable(var_name):
    """
    Get the environment variable or return exception.

    """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise ImproperlyConfigured(error_msg)


def get_ec2_hostname():
    try:
        ipconfig = "http://169.254.169.254/latest/meta-data/local-ipv4"
        return requests.get(ipconfig, timeout=10).text
    except Exception:
        error = "You have to be running on AWS to use AWS settings"
        raise ImproperlyConfigured(error)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": get_env_variable("DATABASE_NAME"),
        "USER": get_env_variable("DATABASE_USER"),
        "PASSWORD": get_env_variable("DATABASE_PASSWORD"),
        "HOST": get_env_variable("DATABASE_HOST"),
        "PORT": "5432",
        "CONN_MAX_AGE": 0,
    }
}

ALLOWED_HOSTS = [
    get_ec2_hostname(),
    "znobot.tech",
]
