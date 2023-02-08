from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.models import APIMethodEnum, ORDER_SUB_STATUS, RECHARGE_PROCESSING, RECHARGE_FAILED, \
    RECHARGE_COMPLETED, DU_POSTPAID, MBME

from apps.orders.utils.api_call_wrapper import sync_api_caller
from apps.orders.utils.process_response import process_mbme_response
from apps.orders.utils.utils import get_transaction_id
from config.config import NOL_TOPUP_MIN, NOL_TOPUP_MAX
from utils.exceptions import APIException500, APIException503, APIException400


class NOLTopupAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def verify_customer_card(self, number, amount):
        """API Method to check the validity of nol card and topup amount must be
            called with unique txn id."""
        transaction_id = get_transaction_id()
        payload = {
            "transactionId": transaction_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.NOL_TOPUP_SERVICE_ID,
            "method": "checkvalidity",
            "reqField1": number,
            "reqField2": amount,
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
            print("Error in balance API call ...")
            raise APIException503()

        return self.__get_response_message(resp, number, transaction_id)

    def __get_response_message(self, resp, recharge_number, transaction_id):
        """
        """
        if resp.get("responseCode") == "000":
            data = {
                "recharge_transaction_id": transaction_id,
                "recharge_number": recharge_number,
                "min_recharge": NOL_TOPUP_MIN,
                "max_recharge": NOL_TOPUP_MAX
            }
            return "Card is Valid", data
        else:
            raise APIException400({
                "error": "Invalid card number"
            })
        # elif resp.get("responseCode") == "302":
        #     raise APIException400({
        #         "error": "Invalid card number"
        #     })
        # else:
        #     raise APIException503({
        #         "error": "Service is not available. Please try after some time"
        #     })

    def do_recharge(self, number, amount, recharge_transaction_id):
        """
        API Method to pay for nol top up must be called with the same
        transaction id used in check validity request.
        """
        payload = {
            "transactionId": recharge_transaction_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.NOL_TOPUP_SERVICE_ID,
            "method": "pay",
            "reqField1": number,
            "reqField2": "6",
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

        process_mbme_response(resp)

        status, recharge_status = self.__get_response_status(resp)
        return status, recharge_status, resp

    def __get_response_status(self, response):
        print("Response resolution start ..")
        if response.get("responseCode") == "000":  # success
            return True, RECHARGE_COMPLETED
        elif response.get("responseCode") == "111":
            return True, RECHARGE_PROCESSING  # processing
        else:
            return False, RECHARGE_FAILED  # failed

