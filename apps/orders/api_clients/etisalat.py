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


class EtisalatAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def verify_customer_account(self, number, service_offered):
        """API Method to check the validity of nol card and topup amount must be
            called with unique txn id."""
        trans_id = get_transaction_id()
        payload = {
            "transactionId": trans_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.ETISALAT_SERVICE_ID,
            "method": "balance",
            "reqField1": str(number),
            "reqField2": service_offered
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

        return self.__get_response_message(resp, number, trans_id)

    def __get_response_message(self, resp, recharge_number, trans_id):
        """
        """
        if resp.get("responseCode") == "000":
            data = {
                "recharge_transaction_id": trans_id,
                "recharge_number": recharge_number,
                "service_offered": resp.get("responseData", {}).get("resField1"),
                "current_balance": resp.get("responseData", {}).get("amount"),
                "min_recharge": resp.get("responseData", {}).get("resField5"),
                "max_recharge": resp.get("responseData", {}).get("resField6"),
                "provider_transaction_id": resp.get("responseData", {}).get("providerTransactionId")

            }
            return resp.get("responseMessage"), data

        # elif resp.get("responseCode") == "302":
        #     raise APIException400({
        #         "error": resp.get("billerMessage")
        #     })
        else:
            raise APIException400({
                "error": "Invalid number"
            })

    def do_recharge(self, number, service_offered, current_balance, amount,
                    recharge_transaction_id, provider_transaction_id):
        payload = {
            "transactionId": recharge_transaction_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.ETISALAT_SERVICE_ID,
            "method": "pay",
            "reqField1": number,
            "reqField2": service_offered,
            "reqField3": provider_transaction_id,
            "reqField4": current_balance,
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

