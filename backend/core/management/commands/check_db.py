from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import time

class Command(BaseCommand):
    help = "Wait for db connection"

    def handle(self, *args, **kwargs):
        self.stdout.write("Waiting DB connection...")

        for i in range(30):
            try:
                conn = connections['default']
                conn.cursor().execute("SELECT 1")
                self.stdout.write(self.style.SUCCESS("DB is ready"))
                return
            except OperationalError:
                self.stdout.write(f"DB is not ready, retrying... ({i+1}/30)")
                time.sleep(2)

        raise Exception("DB not available after 60s")