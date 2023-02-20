import json
import os
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

# from apps.orders.models import country
from account.models import state,country
from the1backend.settings import BASE_DIR


class Command(BaseCommand):
    """
    """

    def handle(self, *args, **options):
        with open(os.path.join(BASE_DIR , "apps/orders/management/commands/states.json"), "r") as f:
            data = json.loads(f.read())
            for records in data:
                print(records)
                if country.objects.filter(id=records["country_id"]).exists():
                    state.objects.update_or_create(
                        # name=records["name"],
                        # country=country.objects.get(id=records["country_id"]),
                        id=records["id"],
                        defaults={'name':records['name'],'country':country.objects.get(id=records["country_id"])},
                    )

        self.stdout.write("All States Saved Successfully")
