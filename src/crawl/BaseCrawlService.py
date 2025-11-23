from abc import ABC

import httpx


class BaseCrawlService(ABC):
    BASE_URL = ""

    def __init__(self):
        limits = httpx.Limits(max_connections=1000, max_keepalive_connections=200)
        timeout = httpx.Timeout(None, connect=40.0)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
        }
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=timeout, limits=limits, headers=headers)

    async def fetch_page_async(self, url) -> str:
        resp = await self.client.get(url, timeout=20.0)
        resp.raise_for_status()
        return resp.text
