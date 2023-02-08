import datetime

from django.conf import settings
from django.utils import timezone

from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.models import APIMethodEnum, ORDER_SUB_STATUS, RECHARGE_PROCESSING, RECHARGE_FAILED, \
    RECHARGE_COMPLETED, VerifiedAccounts, MBME, DU_PREPAID, DATA
from apps.orders.utils.api_call_wrapper import sync_api_caller
from apps.orders.utils.utils import get_transaction_id
from utils.exceptions import APIException500, APIException503


class DUPrepaidAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def verify_customer_account(self, number):
        """Use API Method balance to verify the consumer's account using the unique
            transaction Id."""
        status, is_valid = self.__check_from_db(number)
        if status:
            if is_valid:
                return True, "Number verified successfully"
            else:
                return False, "Invalid Mobile Number"

        payload = {
            "transactionId": get_transaction_id(),
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.DU_PREPAID_SERVICE_ID,
            "method": "balance",
            "reqField1": number
        }
        token = GeneralAPIClient().get_access_token()
        if not token:
            print("Error while getting access token")
            raise APIException503()

        headers = {"Authorization": token}
        resp, status = sync_api_caller(
            url=self.base_url + settings.MBME_PAY_BAL,
            method=APIMethodEnum.POST,
            data=payload,
            headers=headers,
            retry=1
        )
        if not status:
            raise APIException503()

        status, msg = self.__get_response_message(resp)
        # save in db
        self.__save_in_db(number, status)

        return status, msg

    def __save_in_db(self, recharge_number, is_valid):
        # save in DB
        VerifiedAccounts.objects.update_or_create(
            service_type=DU_PREPAID,
            recharge_number=recharge_number,
            service_provider=MBME,
            defaults={"valid_upto": timezone.now() + datetime.timedelta(days=10),
                    "is_valid": is_valid}
        )

    def __check_from_db(self, recharge_number):
        # check first in DB
        qs = VerifiedAccounts.objects.filter(
            service_type=DU_PREPAID,
            service_provider=MBME,
            recharge_number=recharge_number,
            valid_upto__gte=timezone.now()
        )
        if qs.exists():
            return True, qs[0].is_valid
        return False, None

    def do_recharge(self, number, recharge_type, amount):
        payload = {
            "transactionId": get_transaction_id(),
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.DU_PREPAID_SERVICE_ID,
            "method": "pay",
            "reqField1": number,
            "reqField2": recharge_type,
            "paidAmount": amount
        }
        token = GeneralAPIClient().get_access_token()
        if not token:
            print("Error while getting access token")
            return False, RECHARGE_FAILED, None

        headers = {"Authorization": token}
        resp, status = sync_api_caller(
            url=self.base_url + settings.MBME_PAY_BAL,
            method=APIMethodEnum.POST,
            data=payload,
            headers=headers,
            retry=1
        )
        if not status:
            print("Error in recharge API call...")
            return False, RECHARGE_FAILED, resp

        status, recharge_status = self.__get_response_status(resp)
        return status, recharge_status, resp

    def __get_response_status(self, response):
        print("Response resolution start ..")
        if response.get("responseCode") == "000":  # success
            return True, RECHARGE_COMPLETED
        elif response.get("responseCode") == "111":
            return True, RECHARGE_PROCESSING  # processing
        elif response.get("responseCode") in ("302", "905", "999", "997"):
            return False, RECHARGE_FAILED  # failed
        else:
            return False, RECHARGE_FAILED  # failed

    def __get_response_message(self, response):
        if response.get("responseCode") == "000":
            return True, "Number verified successfully"
        elif response.get("responseCode") in ("302", "905", "906", "907"):
            return False, "Invalid Mobile Number"
        else:
            raise APIException503()
