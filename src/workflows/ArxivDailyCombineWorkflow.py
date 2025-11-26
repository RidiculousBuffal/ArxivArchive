import pandas as pd
from pydantic import BaseModel

from src.utils.AggUtils import AggregationUtils


class ArxivDailyCombineWorkflow:
    class PublishResult(BaseModel):
        arxiv_id: str
        english_title: str
        chinese_title: str
        chinese_abstract: str
        worth_read: str
        comment: str
        download_url: str

    def combine_json_to_markdown(self):
        jsons = AggregationUtils().agg_all_today_json()
        finalMarkdown = ''
        for j in jsons:
            finalMarkdown += f"# {j.category}\n"
            prs = []
            for a in j.articles:
                prs.append(self.PublishResult(arxiv_id=a.arxiv_id, english_title=a.title,
                                              chinese_title=a.judgerResult.chinese_name,
                                              chinese_abstract=a.judgerResult.chinese_abstract,
                                              worth_read=str(a.judgerResult.worth_read),
                                              comment=a.judgerResult.comment.replace('\n','<br/>'),
                                              download_url=str(a.pdf_url)).model_dump())
            dataframe = pd.DataFrame(prs)
            finalMarkdown += f'{dataframe.to_markdown(index=False)}\n'
            finalMarkdown += '---\n'
        return finalMarkdown
