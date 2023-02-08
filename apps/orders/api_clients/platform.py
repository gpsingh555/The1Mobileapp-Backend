import datetime

from django.conf import settings
from django.utils import timezone

from apps.orders.models import APIMethodEnum, AccessTokens, SERVICES_PROVIDER, MBME, RECHARGE_FAILED
from apps.orders.utils.api_call_wrapper import sync_api_caller
from apps.orders.utils.utils import get_transaction_id


class GeneralAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def __generate_token(self):
        print("Start generating new token")
        payload = {
            "username": settings.MBME_PAY_USERNAME,
            "password": settings.MBME_PAY_PASSWORD
        }
        resp, status = sync_api_caller(
            url=settings.MBME_BASE_URL + settings.MBME_AUTH_TOKEN,
            method=APIMethodEnum.POST,
            data=payload,
            retry=1
        )
        print(f"Get response form MBME for token {resp}, {status}")
        if status:
            resp_status = self.__get_response_status(resp)
            if resp_status:
                valid_upto = datetime.datetime.now() + datetime.timedelta(minutes=4, seconds=50)
                AccessTokens.objects.create(
                    access_token=resp["accessToken"],
                    valid_upto=valid_upto,
                    service_provider=MBME,
                    wallet_balance=resp["walletBalance"]
                )
                return resp["accessToken"]
            return None
        return None

    def get_access_token(self):
        print("Trying to get access token")
        qs = AccessTokens.objects.filter(
            service_provider=MBME,
            valid_upto__gt=datetime.datetime.now()
        )
        if qs.exists():
            print("found token in DB")
            return qs[0].access_token
        else:
            return self.__generate_token()

    def __get_response_status(self, response):
        """
        120	TRANSACTIONID NOT FOUND FOR PREVIOUS REQUEST
        301	DUPLICATE TRANSACTIONID PROVIDED

        303	SERVICE NOT ENABLED FOR THE MERCHANT
        304	SERVICE NOT AVAILABLE.PLEASE CONTACT SUPPORT.
        305	MERCHANT NOT ENABLED
        888	INSUFFICIENT WALLET BALANCE

        901	REMOTE SERVER UNREACHABLE. TRY AGAIN LATER
        902	INVALID AUTHORIZATION

        991	PLEASE CONTACT MBME SUPPORT
        997	ERROR, PLEASE CONTACT MBME SUPPORT
        """
        if response.get("responseCode") == "000":
            return True
        elif response.get("responseCode") in ("120", "301", "304"):
            return False
        else:
            return False

    def get_all_transaction_report(self, from_date, to_date):
        pass

    def process_pending_recharge(self, unique_id):
        payload = {
            "transId": get_transaction_id(),
            "uniqueId": unique_id
        }

        token = GeneralAPIClient().get_access_token()
        if not token:
            print("Error while getting access token")
            return False, None

        headers = {"Authorization": token}
        resp, status = sync_api_caller(
            url=self.base_url + settings.MBME_PROCESS_PENDING_TRAN,
            method=APIMethodEnum.POST,
            data=payload,
            headers=headers,
            retry=3
        )
        if not status:
            print("Error in Get transaction API call...")
            return False, resp

        if resp.get("responseCode") == "000":
            return True, resp
        else:
            return False, resp

    def get_recharge_status(self, transaction_id):
        payload = {
            "transactionId": transaction_id,
        }
        token = GeneralAPIClient().get_access_token()
        if not token:
            print("Error while getting access token")
            return False, None

        headers = {"Authorization": token}
        resp, status = sync_api_caller(
            url=self.base_url + settings.MBME_FIND_TRAN_BY_ID,
            method=APIMethodEnum.POST,
            data=payload,
            headers=headers,
            retry=3
        )
        if not status:
            print("Error in Get transaction API call...")
            return False, resp

        if resp.get("responseCode") == "000":
            return True, resp
        else:
            return False, resp
