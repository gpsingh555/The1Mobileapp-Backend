import json
import os
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

# from apps.orders.models import country
from account.models import country
from the1backend.settings import BASE_DIR


class Command(BaseCommand):
    """
    """

    def handle(self, *args, **options):
        with open(os.path.join(BASE_DIR , "apps/orders/management/commands/countries.json"), "r") as f:
            data = json.loads(f.read())
            for records in data:
                print(records["name"])
                country.objects.update_or_create(
                    name=records["name"]
                )

        self.stdout.write("All Country Saved Successfully")
