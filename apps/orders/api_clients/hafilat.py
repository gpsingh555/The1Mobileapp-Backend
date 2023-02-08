from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from apps.orders.api_clients.platform import GeneralAPIClient
from apps.orders.models import APIMethodEnum, ORDER_SUB_STATUS, RECHARGE_PROCESSING, RECHARGE_FAILED, \
    RECHARGE_COMPLETED, DU_POSTPAID, MBME, HAFILAT_PASS
from apps.orders.utils.api_call_wrapper import sync_api_caller
from apps.orders.utils.process_response import process_mbme_response
from apps.orders.utils.utils import get_transaction_id
from utils.exceptions import APIException500, APIException503, APIException400


class HafilatAPIClient:

    def __init__(self):
        self.base_url = settings.MBME_BASE_URL

    def verify_customer_card(self, number):
        """Method to check the balance amount/due amount."""
        trans_id = get_transaction_id()
        payload = {
            "transactionId": trans_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.HAFILAT_SERVICE_ID,
            "method": "balance",
            "reqField1": number,
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
        if resp.get("responseCode") == "000" and resp.get("responseData", {}).get("resField1"):
            data = {
                "recharge_number": recharge_number,
                "recharge_transaction_id": trans_id,
                "customer_name": resp.get("responseData", {}).get("custName"),
                "exp_date": resp.get("responseData", {}).get("resField2"),
                "card_status": resp.get("responseData", {}).get("resField3"),
                "available_recharge": resp.get("responseData", {}).get("arrayResponse"),
            }
            return resp.get("responseData", {}).get("resField4"), data

        elif resp.get("responseCode") == "000" and not resp.get("responseData", {}).get("resField1"):
            raise APIException400({
                "error": resp.get("responseData", {}).get("resField4")
            })

        elif resp.get("responseCode") == "302":
            raise APIException400({
                "error": "Invalid card number. Check your card and try again"
            })
        else:
            raise APIException503({
                "error": "Service is not available. Please try after some time"
            })

    def do_recharge(self, number, amount, product_code, item_code,
                    max_allowed, recharge_type, recharge_transaction_id):
        """
        reqField1	Card Number
        reqField2	Product Code received in balance response
        reqField3	Item Code received in balance response
        reqField4	Customer Mobile number
        reqField5	Customer email ID (optional)
        reqField6	For T-purse the value passed is 1 and for Pass(Weekly, Yearly, and monthly pass)
            the value passed is 0
        reqField7	If payment is made for T-purse then null value is passed.
            And if payment is made for Pass the maximum allowed limit/amount received
            in balance response needs to be passed.
        """
        if recharge_type == HAFILAT_PASS:
            reqField7 = max_allowed
            reqField6 = "0"
        else:
            reqField7 = "null"
            reqField6 = "1"

        payload = {
            "transactionId": recharge_transaction_id,
            "merchantId": settings.MBME_MERCHANT_ID,
            "serviceId": settings.HAFILAT_SERVICE_ID,
            "method": "pay",
            "paidAmount": amount,
            "reqField1": number,
            "reqField2": product_code,
            "reqField3": item_code,
            "reqField4": "",  # mobile number
            "reqField5": "",  # email
            "reqField6": reqField6,
            "reqField7": reqField7,
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
