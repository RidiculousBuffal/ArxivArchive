from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

from src.ai.BaseAI import BaseAI
from src.ai.prompts.JudgerPrompt import JudgerPrompt
from src.config.Config import Config
from src.models.Arxiv import ArxivArticle


class JudgeResult(BaseModel):
    chinese_name:str = Field(description='论文中文标题')
    chinese_abstract:str = Field(description='中文摘要')
    worth_read:bool = Field(description='根据我们的研究方向判断是否值得继续阅读')
    comment:str = Field(description='你的评价,为什么认为他值得阅读,和我们的领域有什么关系')

class ArxivJudger(BaseAI):
    systemMessage = SystemMessage(content=JudgerPrompt)
    def __init__(self):
        self.model.model_name = Config.JUDGER_MODEL
        self.judgeAgent = create_agent(self.model,response_format=JudgeResult)
    async def judge(self,article:ArxivArticle)->JudgeResult:
        humanMessage = HumanMessage(content = f"""文章元信息:\n{article.model_dump_json(ensure_ascii=False)}""")
        res =  await self.judgeAgent.ainvoke({"messages":[self.systemMessage,humanMessage]}) # type: ignore
        return res['structured_response']
