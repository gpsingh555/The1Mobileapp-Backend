from utils.exceptions import APIException400


def process_mbme_response(response):
    if response.get("responseCode") == "120":
        raise APIException400({
            "error": "Invalid recharge_transaction_id passed at the time of creation of payment intent"
        })
    elif response.get("responseCode") == "301":
        raise APIException400({
            "error": "DUPLICATE TRANSACTION ID PROVIDED"
        })
