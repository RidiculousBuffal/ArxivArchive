from datetime import datetime
from typing import Optional, List

from pydantic import HttpUrl, BaseModel, Field
from src.models.Content import FigureB64,Text




class Tex(Text):
    pass

class ArxivMetaData(BaseModel):
    figures: List[FigureB64]
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
    url: Optional[HttpUrl] = None
    scraped_at: Optional[datetime] = None
    articles: Optional[List[ArxivArticle]] = []
