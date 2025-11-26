from pathlib import Path

from pydantic import BaseModel

from src.config.Config import Config
from src.utils.AggUtils import AggregationUtils
from src.utils.TimeUtils import TimeUtils


class ArxivDailyPublishWorkflow:
    class PublishResult(BaseModel):
        arxiv_id: str
        english_title: str
        chinese_title: str
        chinese_abstract: str
        worth_read: str
        comment: str
        download_url: str

    def _combine_json_to_markdown(self):
        jsons = AggregationUtils().agg_all_today_json()
        finalMarkdown = ''
        for j in jsons:
            finalMarkdown += f"# {j.category}\n"
            for a in j.articles:
                finalMarkdown += f'## {a.title}\n'
                pr = self.PublishResult(
                    arxiv_id=a.arxiv_id,
                    english_title=a.title,
                    chinese_title=a.judgerResult.chinese_name,
                    chinese_abstract=a.judgerResult.chinese_abstract,
                    worth_read=str(a.judgerResult.worth_read),
                    comment=a.judgerResult.comment.replace('\n', '<br/>'),
                    download_url=str(a.pdf_url)
                ).model_dump()

                finalMarkdown += f"- 论文ID: {pr.get('arxiv_id', '')}\n"
                finalMarkdown += f"- 英文标题: {pr.get('english_title', '')}\n"
                finalMarkdown += f"- 中文标题: {pr.get('chinese_title', '')}\n"
                finalMarkdown += f"- 中文摘要: {pr.get('chinese_abstract', '')}\n"
                finalMarkdown += f"- 是否值得阅读: {pr.get('worth_read', '')}\n"
                finalMarkdown += f"- 评论: {pr.get('comment', '')}\n"
                finalMarkdown += f"- 下载链接: {pr.get('download_url', '')}\n"
                finalMarkdown += '\n'
            finalMarkdown += '---\n'
        return finalMarkdown

    def publish_markdown(self):
        markdown = self._combine_json_to_markdown()
        path = Path(Config.ANALYZE_REPORT_PATH)/TimeUtils.current_date_str()/f'{TimeUtils.current_date_str()}-Arxiv.md'
        with open(path,'w',encoding='utf-8') as f:
            f.write(markdown)
        return markdown

