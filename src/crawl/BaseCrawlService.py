import asyncio
import base64
import os
import tarfile
from abc import ABC
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import aiofiles
import pymupdf
import httpx

from src.config.Config import Config
from src.crawl.model.Arxiv import PDFFigureB64


class BaseCrawlService(ABC):
    BASE_URL = ""
    BASE_DOWNLOAD_PATH = Config.DOWNLOAD_PATH

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

    def _download_with_httpx_sync(self, url: str, target_folder: str) -> str:
        os.makedirs(target_folder, exist_ok=True)
        with httpx.stream("GET", url, timeout=60.0) as r:
            r.raise_for_status()
            filename = None
            cd = r.headers.get("content-disposition")
            if cd:
                import re
                m = re.search(r'filename="?([^"]+)"?', cd)
                filename = m.group(1) if m else None
            if not filename:
                filename = os.path.basename(urlparse(url).path) or "downloaded.file"
            dest = os.path.join(target_folder, filename)
            with open(dest, "wb") as f:
                for chunk in r.iter_bytes():
                    if chunk:
                        f.write(chunk)
        return os.path.abspath(dest)

    async def download_attachment_async(self, attachment_url: str) -> str:
        return self._download_with_httpx_sync(attachment_url, self.BASE_DOWNLOAD_PATH)

    async def extract_tar_gz(self, path: str) -> List[str]:
        p = Path(path)
        if not p.name.endswith(".tar.gz"):
            return []
        archive_name = p.name
        if archive_name.endswith(".tar.gz"):
            archive_name = archive_name[: -len(".tar.gz")]
        target_dir = Path(self.BASE_DOWNLOAD_PATH) / archive_name
        target_dir.mkdir(parents=True, exist_ok=True)

        def _extract():
            extracted_paths: List[Path] = []
            with tarfile.open(p, mode="r:gz") as tf:
                for member in tf.getmembers():
                    member_path = Path(member.name)
                    if member_path.is_absolute() or ".." in member_path.parts:
                        continue
                    tf.extract(member, path=target_dir)
                for fp in target_dir.rglob("*"):
                    if fp.is_file():
                        extracted_paths.append(fp.resolve())
            return extracted_paths

        extracted = await asyncio.to_thread(_extract)
        return [str(p) for p in extracted]

    def pdf_to_base64_pymupdf(self, pdf_path: str, zoom: float = 2.0, fmt: str = "PNG",
                              first_page: Optional[int] = None, last_page: Optional[int] = None) -> List[PDFFigureB64]:
        name, ext = os.path.splitext(os.path.basename(pdf_path))
        doc = pymupdf.open(pdf_path)
        start = (first_page - 1) if first_page else 0
        end = last_page if last_page else doc.page_count
        results = []
        mat = pymupdf.Matrix(zoom, zoom)
        for i in range(start, end):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat, alpha=(fmt.upper() == "PNG"))
            img_bytes = pix.tobytes(output=fmt.upper())
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            results.append(PDFFigureB64(name=f'{name}-{i}', b64=b64))
        doc.close()
        return results

    async def read_text(self,path, encoding='utf-8'):
        async with aiofiles.open(path, mode='r', encoding=encoding) as f:
            content = await f.read()
        return content
