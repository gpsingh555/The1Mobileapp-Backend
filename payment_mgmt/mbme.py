import json
import requests
from requests.auth import HTTPBasicAuth


def GenerateToken(token_key: str, format=None):
        username = "username"
        password = "password"
        try:
            print(f"fetching {token_key} with '{username}' credentials")
            url = f"https://qty.mbme.org:8080/v2/mbme/oauth/token/{token_key}"
            session = requests.Session()
            session.auth = username, password
            headers = {'Content-Type': 'application/json'}
            response = session.get(
                url, headers=headers)
            print(f"response: {response.status_code}")
            return response

        except Exception as e:
            message = {"error": "Uncaught error", "message": str(e)}
            return message


def balance_and_payment_request(request):
    if request.method == 'POST':
        data = request.POST.dict()
        print(data)
        payment_gateway_order_identifier = data['orderId']
        amount = data['orderAmount']

        order = Orders.objects.get(
            payment_gateway_order_identifier=payment_gateway_order_identifier)
        payment = Payments(orders=order, amount=amount,)
        payment.save()

        URL = "https://qty.mbme.org:8080/v2/api/payment"
        request_data = {
                       order: {
                       'id': order.id,
                       'payment_collection_status': transaction_status,
                       'payment_collection_message': transaction_message
                                         }
                                   }
        json_data = json.dumps(request_data)
        response = requests.post(url=URL, data=json_data)
        return Response(status=status.HTTP_200_OK)