from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class APIException400(APIException):
    status_code = 400


class APIException404(APIException):
    status_code = 404
    detail = "resource nat found"


class APIException500(APIException):
    status_code = 500
    detail = "Internal server error. Please try after some time"


class APIException503(APIException):
    status_code = 503
    detail = "Service is not available. Please try after some time"


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        payload = dict()
        payload['status_code'] = response.status_code
        payload["data"] = response.data.get("data", None)
        if response.data.get("message"):
            payload["message"] = response.data.get("message")
        elif response.data.get("error"):
            payload["message"] = response.data.get("error")
        elif response.data.get("detail"):
            payload["message"] = response.data.get("detail")
        else:
            payload["message"] = "Failed"

        payload["errors"] = response.data
        response.data = payload
    return response

