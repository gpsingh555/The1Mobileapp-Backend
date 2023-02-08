from rest_framework.response import Response


def response(data=None, message="Failed", error=None, status_code: int = 200):
    return Response({
                     "message": message,
                     "data": data,
                     "errors": error,
                     "status_code": status_code},
                    status=status_code)
