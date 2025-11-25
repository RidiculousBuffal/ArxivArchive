from typing import Literal

from src.ai.ArxivAnalyzer import ArxivAnalyzer
from src.config.Config import Config
from src.crawl.ArxivDailyCrawlService import ArxivDailyCrawlService
from src.crawl.model.Arxiv import ArxivPageResult, ArxivArticle


class ArxivDailyWorkflow:
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
        self.category = category
        self.crawlResult: ArxivPageResult = ArxivPageResult(category=self.category)
        self.crawlService = ArxivDailyCrawlService(self.category)
        self.aiService = ArxivAnalyzer()

    # 01 crawl the daily article
    async def crawl(self):
        self.crawlResult = await self.crawlService.crawl()
        return self.crawlResult

    async def _generate_metadata(self,article:ArxivArticle):
        pdf_url = str(article.pdf_url)
        if not pdf_url:
            return None
        paths = await self.crawlService.download_attachment_async(pdf_url.replace('pdf', 'src'))
        files = await self.crawlService.extract_tar_gz(paths)
        metadata = await self.crawlService.process_file_lists(files)
        # process image limit
        if len(metadata.figures) >Config.MAX_FIGURE_NUM:
            metadata.figures = metadata.figures[:Config.MAX_FIGURE_NUM]
        return metadata

    # 02 fill the metaData
    async def fillMetaData(self, ):
        for article in self.crawlResult.articles:
            metadata = await self._generate_metadata(article)
            if metadata:
                article.metadata = metadata

    async def _aiAnalyzeOne(self,article:ArxivArticle):
        return await self.aiService.analyze(article.metadata)
