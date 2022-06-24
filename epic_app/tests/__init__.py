from pathlib import Path

from pytest import mark

test_data_dir = Path(__file__).parent / "test_data"

django_postgresql_db = mark.django_db(transaction=True, reset_sequences=True)
