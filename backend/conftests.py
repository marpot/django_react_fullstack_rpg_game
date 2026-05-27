import pytest
from django.db import connection

@pytest.fixture(autouse=True)
def _django_db_all_access(db):
    """
    Wymusza dostęp do DB we wszystkich testach.
    Fix dla:
    - psycopg2 InvalidCursorName
    - Channels + pytest + Django transaction issues
    """
    pass

@pytest.fixture(autouse=True)
def _reset_db_connection():
    connection.close()