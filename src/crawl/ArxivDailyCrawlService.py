import os
from datetime import datetime, timezone
from typing import Literal, List, Optional
from urllib.parse import urljoin

import bs4
from bs4 import BeautifulSoup
from pydantic import HttpUrl

from src.crawl.BaseCrawlService import BaseCrawlService
from src.crawl.model.Arxiv import ArxivArticle, ArxivPageResult, ArxivMetaData, Tex
from src.models.Content import FigureB64


class ArxivDailyCrawlService(BaseCrawlService):
    BASE_URL = "https://arxiv.org"

    def __init__(self, category: Literal[
        "cs.AI",
        "cs.AR",
        "cs.CC",
        "cs.CE",
        "cs.CG",
        "cs.CL",
        "cs.CR",
        "cs.CV",
        "cs.CY",
        "cs.DB",
        "cs.DC",
        "cs.DL",
        "cs.DM",
        "cs.DS",
        "cs.ET",
        "cs.FL",
        "cs.GL",
        "cs.GR",
        "cs.GT",
        "cs.HC",
        "cs.IR",
        "cs.IT",
        "cs.LG",
        "cs.LO",
        "cs.MA",
        "cs.MM",
        "cs.MS",
        "cs.NA",
        "cs.NE",
        "cs.NI",
        "cs.OH",
        "cs.OS",
        "cs.PF",
        "cs.PL",
        "cs.RO",
        "cs.SC",
        "cs.SD",
        "cs.SE",
        "cs.SI",
        "cs.SY",
    ]):
        super().__init__()
        self.category = category
        self.api_path = f"/list/{category}/new"
        self.full_path = f"{self.BASE_URL}{self.api_path}"

    def parse_single_article(self, dt:bs4.element.Tag, dd:bs4.element.Tag, category: str, scraped_at: datetime) -> ArxivArticle:
        # --- 解析 dt 部分 ---
        a_tags = dt.find_all("a")

        # index: [1]
        index = None
        if a_tags:
            index_text = a_tags[0].get_text(strip=True)
            index = int(index_text.strip("[]"))

        abs_url = None
        arxiv_id = None
        pdf_url = None
        html_url = None
        other_url = None

        for a in a_tags:
            href = a.get("href", "")
            title = a.get("title", "").lower()
            aid = a.get("id", "")

            # Abstract 链接
            if "abstract" in title or href.startswith("/abs/"):
                abs_url = urljoin(self.BASE_URL, href)
                if aid:
                    arxiv_id = aid
                else:
                    arxiv_id = href.split("/")[-1]

            # pdf / html / other
            if aid.startswith("pdf-") or "pdf" in title:
                pdf_url = urljoin(self.BASE_URL, href)
            elif aid.startswith("html-") or "html" in title:
                html_url = urljoin(self.BASE_URL, href)
            elif aid.startswith("oth-") or "other formats" in title:
                other_url = urljoin(self.BASE_URL, href)

        if abs_url is None or arxiv_id is None or index is None:
            raise ValueError("Failed to parse index/arxiv_id/abs_url from dt.")

        # --- 解析 dd 部分 ---
        meta = dd.find("div", class_="meta")
        if not meta:
            raise ValueError("No .meta div in dd.")

        # title
        title_div = meta.find("div", class_="list-title")
        if not title_div:
            raise ValueError("No .list-title div.")
        title_text = title_div.get_text(" ", strip=True)
        if "Title:" in title_text:
            title_text = title_text.replace("Title:", "", 1).strip()

        # authors
        authors_div = meta.find("div", class_="list-authors")
        authors: List[str] = []
        if authors_div:
            for a in authors_div.find_all("a"):
                name = a.get_text(strip=True)
                if name:
                    authors.append(name)

        # comments
        comments_div = meta.find("div", class_="list-comments")
        comments: Optional[str] = None
        if comments_div:
            comments_text = comments_div.get_text(" ", strip=True)
            if "Comments:" in comments_text:
                comments_text = comments_text.replace("Comments:", "", 1).strip()
            if comments_text:
                comments = comments_text

        # subjects
        subjects_div = meta.find("div", class_="list-subjects")
        subjects_primary: Optional[str] = None
        subjects_other: List[str] = []
        if subjects_div:
            primary_span = subjects_div.find("span", class_="primary-subject")
            if primary_span:
                subjects_primary = primary_span.get_text(strip=True)

            full_text = subjects_div.get_text(" ", strip=True)
            if "Subjects:" in full_text:
                full_text = full_text.replace("Subjects:", "", 1).strip()
            if subjects_primary and subjects_primary in full_text:
                full_text = full_text.replace(subjects_primary, "", 1).strip()

            for part in full_text.replace(";", ",").split(","):
                t = part.strip()
                if t:
                    subjects_other.append(t)

        # abstract
        abstract_p = meta.find("p", class_="mathjax")
        if not abstract_p:
            raise ValueError("No abstract <p class='mathjax'>.")
        abstract_text = abstract_p.get_text(" ", strip=True)

        return ArxivArticle(
            index=index,
            arxiv_id=arxiv_id,
            category=category,
            abs_url=HttpUrl(abs_url),
            pdf_url=pdf_url,
            html_url=html_url,
            other_url=other_url,
            title=title_text,
            authors=authors,
            comments=comments,
            subjects_primary=subjects_primary,
            subjects_other=subjects_other,
            abstract=abstract_text,
            scraped_at=scraped_at,
        )

    def parse_articles(self, html: str, list_url: str) -> ArxivPageResult:
        soup = BeautifulSoup(html, "html.parser")

        dl = soup.find("dl", id="articles")
        if not dl:
            raise RuntimeError("Could not find <dl id='articles'> in the page.")

        dts = dl.find_all("dt", recursive=False)
        dds = dl.find_all("dd", recursive=False)
        if len(dts) != len(dds):
            n = min(len(dts), len(dds))
            dts = dts[:n]
            dds = dds[:n]

        scraped_at = datetime.now(timezone.utc)
        category = self.category

        articles: List[ArxivArticle] = []
        for dt, dd in zip(dts, dds):
            try:
                article = self.parse_single_article(dt, dd, category, scraped_at)
                articles.append(article)
            except Exception as e:
                # 可换成 logging.warning
                print(f"Failed to parse one article: {e}")

        return ArxivPageResult(
            category=category,
            url=HttpUrl(list_url),
            scraped_at=scraped_at,
            articles=articles,
        )

    async def crawl(self):
        html = await self.fetch_page_async(self.api_path)
        page_result = self.parse_articles(html, self.full_path)
        return page_result

    async def _process_tex_file(self, tex_path: str):
        name, ext = os.path.splitext(os.path.basename(tex_path))
        text = await self.read_text(tex_path)
        return Tex(name=name, text=text)

    async def process_file_lists(self, paths: List[str]) -> ArxivMetaData:
        figures = []
        texts = []
        # only extract .tex and .pdf(figure)

        for path in paths:
            if path.endswith(".pdf"):
                figures.extend(self.pdf_to_base64_pymupdf(path, 1, 'PNG'))
            elif path.endswith(".tex"):
                tex = await self._process_tex_file(path)
                texts.append(tex)
            else:
                res = self._get_minetype_and_b64(path)
                if res:
                    mime,b64 = res
                    if not mime.startswith('image'):
                        continue
                    if not b64:
                        continue
                    name, ext = os.path.splitext(os.path.basename(path))
                    figures.append(FigureB64(mime=mime, b64=b64,name=name))

        return ArxivMetaData(figures=figures, texts=texts)
