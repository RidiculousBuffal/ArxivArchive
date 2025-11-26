import asyncio

from src.config.Config import Config
from src.workflows.ArxivDailyPublishWorkflow import ArxivDailyPublishWorkflow
from src.workflows.ArxivDailyWorkflow import ArxivDailyWorkflow


async def task(x):
    return await ArxivDailyWorkflow(x).run(without_analyze=True)


async def main():
    tasks = [task(x) for x in Config.PREFER_CATEGORY]
    await asyncio.gather(*tasks)
    ArxivDailyPublishWorkflow().publish_markdown()


if __name__ == '__main__':
    asyncio.run(main())
