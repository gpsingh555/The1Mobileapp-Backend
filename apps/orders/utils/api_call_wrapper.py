import asyncio
import time

import aiohttp.web
from django.conf import settings

from apps.orders.models import APIMethodEnum
from apps.orders.utils.api_caller_utils import request_url


def sync_api_caller(url: str, method: APIMethodEnum, params: dict = None,
                    data=None, headers={}, retry=settings.ERROR_RETRY_COUNT):
    print(f"payload for request POST==>URL- {url}method=>{method} params=>{params} data=>{data} headers=>{headers}")
    # TODO : can switch server if server realted issue
    if retry <= 0: return
    resp = {}
    status = False

    try:
        resp, status = request_url(url, method, params, data, headers)
    # except aiohttp.web.HTTPTooManyRequests as e:
    #     print(e)
    #     print(f"Error - Remaining retry count => {retry-1}")
    #     time.sleep(settings.HTTP_TOO_MANY_REQ_SLEEP)
    #     return sync_api_caller(url, method, params, data, retry-1)
    #
    # except (aiohttp.web.HTTPRequestTimeout, aiohttp.web.HTTPGone,
    #         aiohttp.web.HTTPServerError) as e:
    #     print(e)
    #     print(f"Error -Remaining retry count => {retry-1}")
    #     time.sleep(settings.HTTP_REQ_TIMEOUT_SLEEP)
    #     resp, status = sync_api_caller(url, method, params, data, retry-1)
    #
    # except (asyncio.TimeoutError, aiohttp.http.HttpProcessingError,
    #         aiohttp.client_exceptions.ClientConnectorError) as e:
    #     print(e)
    #     print(f"Error -Remaining retry count => {retry-1}")
    #     time.sleep(settings.ASYNC_TIMEOUT_SLEEP)
    #     resp, status = sync_api_caller(url, method, params, data, retry-1)

    except Exception as e:
        print('Unknown exception Not handled in API caller wrapper - ', e)

    finally:
        print(f"Return from finally block==>{resp} {status}")
        return resp, status
