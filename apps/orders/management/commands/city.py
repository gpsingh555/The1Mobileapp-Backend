import json
import os
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

# from apps.orders.models import country
from account.models import city,state
from the1backend.settings import BASE_DIR


class Command(BaseCommand):
    """
    """

    def handle(self, *args, **options):
        with open(os.path.join(BASE_DIR , "apps/orders/management/commands/cities.json"), "r") as f:
            data = json.loads(f.read())
            
            for records in data:
                print(records["name"])
                if state.objects.filter(id=records["state_id"]).exists():
                    st=state.objects.get(id=records["state_id"])
                    print(records["name"])
                    city.objects.update_or_create(
                        name=records["name"],
                        state=st,
                        country_id=st.country
                    )

        self.stdout.write("All City Saved Successfully")
