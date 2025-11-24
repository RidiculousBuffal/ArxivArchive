from src.crawl.ArxivDailyCrawlService import ArxivDailyCrawlService


async def main():
    service = ArxivDailyCrawlService(category='cs.AI')
    res = await service.crawl()
    print(res.model_dump_json(ensure_ascii=False))
    print(len(res.articles))
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
