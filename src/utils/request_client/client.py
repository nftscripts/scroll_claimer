from typing import Dict, Any
from loguru import logger

from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector


class RequestClient:
    def __init__(self, proxy: str | None):
        self.session = ClientSession(
            connector=ProxyConnector.from_url(proxy, ) if proxy else TCPConnector(
                verify_ssl=False
            )
        )

    async def make_request(
            self,
            method: str = 'GET',
            url: str = None,
            headers: Dict[str, Any] = None,
            data: str = None,
            json: Dict[str, Any] = None,
            params: Dict[str, Any] = None,
            cookies = None
    ):
        async with self.session.request(
                method=method, url=url, headers=headers, data=data, params=params, json=json, cookies=cookies
        ) as response:
            try:
                response_json = await response.text()
                if response.status == 200:
                    return response_json

            except Exception as ex:
                logger.error(f'Something went wrong {ex}')
