import json
from pathlib import Path

from src.config.Config import Config
from src.models.Arxiv import ArxivPageResult
from src.utils.TimeUtils import TimeUtils


class AggregationUtils:
    def __init__(self):
        pass
    def agg_all_today_json(self)->list[ArxivPageResult]:
        root = Path(Config.ANALYZE_REPORT_PATH)/TimeUtils.current_date_str()
        files = list(root.rglob('*.json'))
        res = []
        for file in files:
            text = file.read_text(encoding='utf-8')
            arxivPageResult = ArxivPageResult.model_validate_json(text)
            res.append(arxivPageResult)
        return res
