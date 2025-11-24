import asyncio

from src.crawl.ArxivDailyCrawlService import ArxivDailyCrawlService


async def main():
    service = ArxivDailyCrawlService('cs.AI')
    src = 'https://arxiv.org/src/2511.16837'
    p = await service.download_attachment_async(src)
    print(p)
    files = await service.extract_tar_gz(p)
    print(files)
if __name__ == '__main__':
    asyncio.run(main())