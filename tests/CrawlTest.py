from src.crawl.ArxivDailyCrawlService import ArxivDailyCrawlService


async def main():
    service = ArxivDailyCrawlService(category='cs.AI')
    res = await service.crawl()
    print(res)
    print(len(res.articles))
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
