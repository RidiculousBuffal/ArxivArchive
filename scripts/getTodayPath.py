from pathlib import Path

from src.config.Config import Config
from src.utils.TimeUtils import TimeUtils

if __name__ == '__main__':
    print(str(Path(Config.ANALYZE_REPORT_PATH)/TimeUtils.current_date_str()/f'{TimeUtils.current_date_str()}-Arxiv.md'))