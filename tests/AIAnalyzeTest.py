import asyncio
import datetime

from pydantic import HttpUrl

from src.crawl.model.Arxiv import ArxivArticle, ArxivMetaData
from src.workflows.ArxivDailyWorkflow import ArxivDailyWorkflow


async def main():
    article = ArxivArticle(index=5, arxiv_id='2511.17673', category='cs.AI',
                 abs_url=HttpUrl('https://arxiv.org/abs/2511.17673'),
                 pdf_url=HttpUrl('https://arxiv.org/pdf/2511.17673'),
                 html_url=None,
                 other_url=HttpUrl('https://arxiv.org/format/2511.17673'),
                 title='Bridging Symbolic Control and Neural Reasoning in LLM Agents: The Structured Cognitive Loop',
                 authors=['Myung Ho Kim'],
                 comments='27 pages',
                 subjects_primary='Artificial Intelligence (cs.AI)',
                 subjects_other=['Computation and Language (cs.CL)'],
                 abstract='Large language model agents suffer from fundamental architectural problems: entangled reasoning and execution, memory volatility, and uncontrolled action sequences. We introduce Structured Cognitive Loop (SCL), a modular architecture that explicitly separates agent cognition into five phases: Retrieval, Cognition, Control, Action, and Memory (R-CCAM). At the core of SCL is Soft Symbolic Control, an adaptive governance mechanism that applies symbolic constraints to probabilistic inference, preserving neural flexibility while restoring the explainability and controllability of classical symbolic systems. Through empirical validation on multi-step conditional reasoning tasks, we demonstrate that SCL achieves zero policy violations, eliminates redundant tool calls, and maintains complete decision traceability. These results address critical gaps in existing frameworks such as ReAct, AutoGPT, and memory-augmented approaches. Our contributions are threefold: (1) we situate SCL within the taxonomy of hybrid intelligence, differentiating it from prompt-centric and memory-only approaches; (2) we formally define Soft Symbolic Control and contrast it with neuro-symbolic AI; and (3) we derive three design principles for trustworthy agents: modular decomposition, adaptive symbolic governance, and transparent state management. We provide a complete open-source implementation demonstrating the R-CCAM loop architecture, alongside a live GPT-4o-powered travel planning agent. By connecting expert system principles with modern LLM capabilities, this work offers a practical and theoretically grounded path toward reliable, explainable, and governable AI agents. Code: this https URL Demo: this https URL',
                 scraped_at=datetime.datetime(2025, 11, 25, 5, 53, 2, 351376, tzinfo=datetime.timezone.utc),
                 metadata=ArxivMetaData(figures=[], texts=[]))
    workflow = ArxivDailyWorkflow('cs.AI')
    metadata = await workflow._generate_metadata(article)
    article.metadata = metadata
    res = await workflow._aiAnalyzeOne(article)
    print(res)
if __name__ == '__main__':
    asyncio.run(main())