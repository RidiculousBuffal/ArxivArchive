from datetime import datetime
from typing import Optional, List

from pydantic import HttpUrl, BaseModel, Field
from src.models.Content import FigureB64, Text


class Tex(Text):
    pass


class ArxivMetaData(BaseModel):
    figures: List[FigureB64]
    texts: List[Tex]


class JudgeResult(BaseModel):
    chinese_name: str = Field(description='论文中文标题')
    chinese_abstract: str = Field(description='中文摘要')
    worth_read: bool = Field(description='根据我们的研究方向判断是否值得继续阅读')
    comment: str = Field(description='你的评价,为什么认为他值得阅读,和我们的领域有什么关系,请勿使用任何的markdown语法')


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
    judgerResult: Optional[JudgeResult] = None


class ArxivPageResult(BaseModel):
    category: str
    url: Optional[HttpUrl] = None
    scraped_at: Optional[datetime] = None
    articles: Optional[List[ArxivArticle]] = []
