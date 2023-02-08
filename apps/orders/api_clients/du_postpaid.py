from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.models import APIMethodEnum, ORDER_SUB_STATUS, RECHARGE_PROCESSING, RECHARGE_FAILED, \
    RECHARGE_COMPLETED, DU_POSTPAID, MBME
from apps.orders.utils.api_call_wrapper import sync_api_caller
from apps.orders.utils.process_response import process_mbme_response
from apps.orders.utils.utils import get_transaction_id
from utils.exceptions import APIException500, APIException503, APIException400


class DUPostpaidAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def get_customer_balance(self, number):
        """Use API Method 'balance' to know the outstanding amount of the customer using
            unique transaction ID."""
        # data = self.get_balance_from_db(number)
        # if data:
        #     return data

        payload = {
            "transactionId": get_transaction_id(),
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.DU_POSTPAID_SERVICE_ID,
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
            print("Error in balance API call...")
            raise APIException503()

        return self.save_balance_in_db(resp, number)

    def save_balance_in_db(self, resp, recharge_number):
        """
        """
        if resp.get("responseCode") == "000":
            data = {"balance": resp.get("responseData").get("amount"),
                    "customer_name": resp.get("responseData").get("custName"),
                    "recharge_transaction_id": resp.get("responseData").get("resField1"),
                    "recharge_number": recharge_number}
            return data

        elif resp.get("responseCode") == "302" and resp.get("billerErrorCode") == "E02":
            raise APIException400({
                "error": resp.get("billerMessage")
            })

        elif resp.get("responseCode") == "302" and resp.get("billerErrorCode") == "E07":
            raise APIException400({
                "error": resp.get("billerMessage")
            })

        else:
            raise APIException503({
                "error": "Service is not available. Please try after some time"
            })

    def do_recharge(self, number, amount, recharge_transaction_id):
        payload = {
            "transactionId": recharge_transaction_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.DU_POSTPAID_SERVICE_ID,
            "method": "pay",
            "reqField1": number,
            "reqField2": "CREDIT_ACCOUNT_PAY",
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

