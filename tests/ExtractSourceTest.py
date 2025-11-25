import asyncio
import json

from src.crawl.ArxivDailyCrawlService import ArxivDailyCrawlService


async def main():
    files = ['/Users/zhoulicheng/codes/ArxivArchive/downloads/arXiv-2511.16814v1.pdf']
    service = ArxivDailyCrawlService('cs.AI')
    res = await service.process_file_lists(files)
    with open('source.json', 'w',encoding='utf-8') as f:
        f.write(json.dumps(res.model_dump(), ensure_ascii=False, indent=4))
if __name__ == '__main__':
    asyncio.run(main())