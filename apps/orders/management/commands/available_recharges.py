import json
import os
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.orders.models import AvailableRecharge
from the1backend.settings import BASE_DIR


class Command(BaseCommand):
    """
    """

    def handle(self, *args, **options):
        with open(os.path.join(BASE_DIR , "apps/orders/management/commands/recharges.json"), "r") as f:
            data = json.loads(f.read())
            for records in data:
                AvailableRecharge.objects.update_or_create(
                    amount=records["amount"],
                    service_type=records["service_type"],
                    recharge_type=records["recharge_type"],
                    currency=records["currency"],
                    defaults={'detail': records["detail"]}
                )

        self.stdout.write("All Recharge saved successfully")
