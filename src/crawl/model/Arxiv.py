from datetime import datetime
from typing import Optional, List

from pydantic import HttpUrl, BaseModel, Field


class PDFFigureB64(BaseModel):
    name: str
    b64: str


class Tex(BaseModel):
    name: str
    text: str


class ArxivMetaData(BaseModel):
    figures: List[PDFFigureB64]
    texts: List[Tex]


class ArxivArticle(BaseModel):
    index: int
    arxiv_id: str
    category: str

    abs_url: HttpUrl
    pdf_url: Optional[HttpUrl] = None
    html_url: Optional[HttpUrl] = None
    other_url: Optional[HttpUrl] = None

    title: str
    authors: List[str]

    comments: Optional[str] = None
    subjects_primary: Optional[str] = None
    subjects_other: List[str] = []

    abstract: str

    scraped_at: datetime
    metadata: Optional[ArxivMetaData] = Field(default=ArxivMetaData(figures=[], texts=[]))


class ArxivPageResult(BaseModel):
    category: str
    url: HttpUrl
    scraped_at: datetime
    articles: List[ArxivArticle]
