import logging
from datetime import datetime, timedelta, timezone, date
import asyncio
from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.models import AccessTokens, SERVICES_PROVIDER, MBME

logger = logging.getLogger(__name__)


class GeneralAPIService:

    def save_access_token(self):
        resp, status = asyncio.run(GeneralAPIClient().generate_token())
        logger.debug(resp)
        if status:
            valid_upto = datetime.now(tz=timezone.utc) + timedelta(minutes=4, seconds=50)
            AccessTokens.objects.create(
                access_token=resp["accessToken"],
                valid_upto=valid_upto,
                service_provide=MBME,
                wallet_balance=resp["walletBalance"]
            )

