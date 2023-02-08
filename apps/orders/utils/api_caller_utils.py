import asyncio
from typing import List, Dict
import requests
import aiohttp

from apps.orders.models import APIMethodEnum


async def get_url(session: aiohttp.ClientSession, url: str) -> Dict:
    async with session.get(url) as response:
        return await response.json()


async def request_multiple_urls(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks: List[asyncio.Task] = []
        for url in urls:
            tasks.append(
                asyncio.ensure_future(
                    get_url(session, url)
                )
            )
        return await asyncio.gather(*tasks)


def request_url(url: str, method: APIMethodEnum, params: dict = None, data=None, headers={}):
    """
    """
    json_response = None
    status_code = 0
    if method == APIMethodEnum.GET:
        resp = requests.get(url=url, params=params, headers=headers)
        json_response = resp.json()
        if resp.ok:
            return json_response, resp.ok
        status_code = resp.status_code

    elif method == APIMethodEnum.POST:
        resp = requests.post(url = url, data = data, headers=headers)
        json_response = resp.json()
        if resp.ok:
            return json_response, resp.ok
        status_code = resp.status_code

    if status_code == 429:
        print(f"Error response => {json_response}")
        raise requests.exceptions.RequestException
    # elif status_code == 408:
    #     print(f"Error response => {json_response}")
    #     raise aiohttp.web.HTTPRequestTimeout
    # elif status_code == 410:
    #     print(f"Error response => {json_response}")
    #     raise aiohttp.web.HTTPGone
    # elif status_code >= 500:
    #     print(f"Error response => {json_response}")
    #     raise aiohttp.web.HTTPServerError
    else:
        print(json_response)
        return json_response, False
