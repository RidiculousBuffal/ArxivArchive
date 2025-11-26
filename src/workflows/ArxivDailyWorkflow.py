import json
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from tqdm.asyncio import tqdm_asyncio

from src.ai.ArxivAnalyzer import ArxivAnalyzer
from src.ai.ArxivJudger import ArxivJudger
from src.config.Config import Config
from src.crawl.ArxivDailyCrawlService import ArxivDailyCrawlService
from src.models.Arxiv import ArxivPageResult, ArxivArticle
from src.models.Encoder import CustomEncoder
from src.utils.TimeUtils import TimeUtils


# ------------------------------------------------------------------
# 日志配置
# ------------------------------------------------------------------
def _setup_logger(category: str) -> logging.Logger:
    """
    为指定 category 创建一个带滚动文件的 logger
    """
    today_str = TimeUtils.current_date_str()
    log_dir = Path(Config.ANALYZE_REPORT_PATH) / today_str / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"arxiv_daily.{category}")
    logger.setLevel(logging.DEBUG)

    # 避免重复 handler
    if logger.handlers:
        return logger

    fmt = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"

    # 控制台
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter(fmt, date_fmt))
    logger.addHandler(console)

    # 文件，按天滚动，最大 10 MB
    file_handler = RotatingFileHandler(
        log_dir / f"{category}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt, date_fmt))
    logger.addHandler(file_handler)

    return logger


# ------------------------------------------------------------------
# 进度条友好的日志 handler（防止 tqdm 抖动）
# ------------------------------------------------------------------
class AsyncTqdmLoggingHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm_asyncio.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


# ------------------------------------------------------------------
# 主流程
# ------------------------------------------------------------------
class ArxivDailyWorkflow:
    def __init__(
            self,
            category: Literal[
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
            ],
            batchsize: int = 5,
    ):
        self.category = category
        self.batchsize = batchsize

        self.crawlResult: ArxivPageResult = ArxivPageResult(category=self.category)
        self.crawlService = ArxivDailyCrawlService(self.category)
        self.judgeService = ArxivJudger()
        self.aiService = ArxivAnalyzer()

        today = TimeUtils.current_date_str()
        self.folder = Path(Config.ANALYZE_REPORT_PATH) / today / self.category
        self.folder.mkdir(parents=True, exist_ok=True)

        self.logger = _setup_logger(category)

    # ------------------------------------------------------------------
    # 01 爬取
    # ------------------------------------------------------------------
    async def crawl(self) -> ArxivPageResult:
        self.logger.info("📥 开始爬取 %s 今日文章...", self.category)
        start = time.perf_counter()

        try:
            self.crawlResult = await self.crawlService.crawl()
            elapsed = time.perf_counter() - start
            self.logger.info(
                "✅ 爬取完成，共 %d 篇文章，耗时 %.2f 秒",
                len(self.crawlResult.articles),
                elapsed,
            )
            return self.crawlResult
        except Exception as e:
            self.logger.exception("❌ 爬取失败：%s", e)
            raise

    # ------------------------------------------------------------------
    # 02 粗筛
    # ------------------------------------------------------------------
    async def _judge_one_article(self, article: ArxivArticle):
        try:
            return await self.judgeService.judge(article)
        except Exception as e:
            self.logger.error("⚠️ 判断文章 %s 失败：%s", article.id, e)
            return None

    async def judge_articles(self):
        articles = self.crawlResult.articles
        if not articles:
            self.logger.warning("⚠️ 无文章可筛选，跳过 judge 阶段")
            return

        self.logger.info("🔍 开始筛选文章，共 %d 篇...", len(articles))

        start = time.perf_counter()
        tasks = [
            self._judge_one_article(a) for a in articles
        ]
        results = await tqdm_asyncio.gather(*tasks, desc="Judging")

        succeed = 0
        for article, res in zip(articles, results):
            if res is None:
                continue
            article.judgerResult = res
            succeed += 1

        elapsed = time.perf_counter() - start
        self.logger.info(
            "✅ 筛选完成：%d/%d 成功，耗时 %.2f 秒",
            succeed,
            len(articles),
            elapsed,
        )

    # ------------------------------------------------------------------
    # 03 拉取元数据（仅 worth_read）
    # ------------------------------------------------------------------
    async def _generate_metadata(self, article: ArxivArticle):
        try:
            pdf_url = str(article.pdf_url)
            if not pdf_url:
                return None
            src_url = pdf_url.replace("pdf", "src")
            paths = await self.crawlService.download_attachment_async(src_url)
            files = await self.crawlService.extract_tar_gz(paths)
            metadata = await self.crawlService.process_file_lists(files)
            if len(metadata.figures) > Config.MAX_FIGURE_NUM:
                metadata.figures = metadata.figures[: Config.MAX_FIGURE_NUM]
            return metadata
        except Exception as e:
            self.logger.warning("⚠️ 获取 %s 元数据失败：%s", article.id, e)
            return None

    async def fill_meta_data(self):
        articles = [a for a in self.crawlResult.articles if a.judgerResult and a.judgerResult.worth_read]
        if not articles:
            self.logger.warning("⚠️ 没有值得阅读的文章，跳过元数据拉取")
            return

        self.logger.info("🗂  开始拉取元数据，共 %d 篇...", len(articles))

        start = time.perf_counter()
        tasks = [self._generate_metadata(a) for a in articles]
        results = await tqdm_asyncio.gather(*tasks, desc="Meta")

        succeed = 0
        for article, meta in zip(articles, results):
            if meta:
                article.metadata = meta
                succeed += 1

        elapsed = time.perf_counter() - start
        self.logger.info(
            "✅ 元数据拉取完成：%d/%d 成功，耗时 %.2f 秒",
            succeed,
            len(articles),
            elapsed,
        )

    # ------------------------------------------------------------------
    # 04 AI 深度分析
    # ------------------------------------------------------------------
    async def _ai_analyze_one(self, article: ArxivArticle):
        try:
            return await self.aiService.analyze(article.metadata)
        except Exception as e:
            self.logger.error("⚠️ AI 分析 %s 失败：%s", article.id, e)
            return None

    async def _write_and_analyze_one(self, article: ArxivArticle):
        try:
            analyzeResult = await self._ai_analyze_one(article)
            if not analyzeResult:
                return None
            filename = f"{article.title}.md"
            safe_filename = "".join(c for c in filename if c.isalnum() or c in " ._-")
            out_path = self.folder / safe_filename
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# {article.title}\n")
                f.write(analyzeResult.text)
            return analyzeResult
        except Exception as e:
            self.logger.exception("❌ 保存分析报告 %s 失败：%s", article.id, e)
            return None

    async def analyze(self):
        articles = [
            a for a in self.crawlResult.articles
            if a.judgerResult and a.judgerResult.worth_read and a.metadata
        ]
        if not articles:
            self.logger.warning("⚠️ 无可分析的文章，跳过 AI 分析阶段")
            return

        self.logger.info("🤖 开始 AI 分析，共 %d 篇...", len(articles))

        start = time.perf_counter()
        tasks = [self._write_and_analyze_one(a) for a in articles]
        await tqdm_asyncio.gather(*tasks, desc="Analyze")

        elapsed = time.perf_counter() - start
        self.logger.info("✅ AI 分析完成，耗时 %.2f 秒", elapsed)

    # ------------------------------------------------------------------
    # 05 导出 JSON
    # ------------------------------------------------------------------
    async def save_json(self):
        outfile = self.folder / f"{self.category}.json"
        self.logger.info("💾 导出 JSON 到 %s ...", outfile)
        try:
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(
                    self.crawlResult.model_dump(exclude={
                        "articles": {
                            "__all__": {"metadata"}
                        }
                    }),
                    f,
                    ensure_ascii=False,
                    cls=CustomEncoder,
                    indent=2,
                )
            self.logger.info("✅ JSON 导出完成")
        except Exception as e:
            self.logger.exception("❌ JSON 导出失败：%s", e)

    async def run(self, without_analyze: bool = False):
        self.logger.info("🚀 开始完整工作流，category=%s", self.category)
        try:
            await self.crawl()
            await self.judge_articles()
            if not without_analyze:
                await self.fill_meta_data()
                await self.analyze()
            await self.save_json()
            self.logger.info("🎉 全部流程完成！")
        except Exception as e:
            self.logger.exception("💥 工作流异常终止：%s", e)
            raise
