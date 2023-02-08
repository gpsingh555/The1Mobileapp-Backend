from django.conf import settings

from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.models import APIMethodEnum, ORDER_SUB_STATUS, RECHARGE_PROCESSING, RECHARGE_FAILED, \
    RECHARGE_COMPLETED, DU_POSTPAID, MBME
from apps.orders.utils.api_call_wrapper import sync_api_caller
from apps.orders.utils.process_response import process_mbme_response
from apps.orders.utils.utils import get_transaction_id
from config.config import SALIK_DIRECT_MIN, SALIK_DIRECT_MAX
from utils.exceptions import APIException500, APIException503, APIException400


class SalikDirectAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def verify_customer_card(self, number, account_pin):
        """Method to check account details by entering SALIK account Number."""
        trans_id = get_transaction_id()
        payload = {
            "transactionId": trans_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.SALIK_DIRECT_SERVICE_ID,
            "method": "balance",
            "reqField1": number,  # Account ID / Number to identify the user account
            "reqField2": account_pin  # Account Pin / Pin to validate the user
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

        return self.__get_response_message(resp, number, trans_id)

    def __get_response_message(self, resp, recharge_number, trans_id):
        """
        """
        if resp.get("responseCode") == "000":
            data = {
                "recharge_transaction_id": trans_id,
                "recharge_number": recharge_number,
                "customer_name": resp["responseData"].get("cusName"),
                "customer_balance": resp["responseData"].get("amount"),
                "min_recharge": SALIK_DIRECT_MIN,
                "max_recharge": SALIK_DIRECT_MAX,
                "provider_transaction_id": resp["responseData"].get("providerTransactionId"),
                "multiple_of": 50
            }
            return True, "Account Verified successfully", data

        elif resp.get("responseCode") == "302":
            raise APIException400({
                "error": "Invalid Account Number/PIN Code"
            })
        else:
            raise APIException503({
                "error": "Service is not available. Please try after some time"
            })

    def do_recharge(self, number, amount, account_pin, recharge_transaction_id, provider_transaction_id):
        payload = {
            "transactionId": recharge_transaction_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.SALIK_DIRECT_SERVICE_ID,
            "method": "pay",
            "paidAmount": amount,
            "reqField1": number,
            "reqField2": account_pin,
            "reqField3": provider_transaction_id
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
        elif response.get("responseCode") == '01':
            raise APIException400({"error": response.get("responseMessage")})
        else:
            return False, RECHARGE_FAILED  # failed
