from distutils.command.config import config
from pathlib import Path

from pytest import mark

test_data_dir = Path(__file__).parent / "test_data"

# Apparently pytest does not load the service file directly, which leads to failure on a
# local environment, so we make it here explicit
django_postgresql_db = mark.django_db(transaction=True, reset_sequences=True)

from django.conf import settings

if not settings.DATABASES["default"]["NAME"]:
    import configparser
    import os

    # Look for the location of the .pg_service.conf filepath
    config = configparser.ConfigParser()
    config.read(os.environ["PGSERVICEFILE"])
    db_svc = settings.DATABASES["default"]["OPTIONS"]["service"]
    if db_svc not in config.sections():
        raise ValueError("Error configuring database for testing.")
    for db_setting in config[db_svc]:
        settings.DATABASES["default"][db_setting.upper()] = config[db_svc][db_setting]
