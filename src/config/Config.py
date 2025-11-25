import os
import dotenv

dotenv.load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') or None
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL') or "https://api.openai.com/v1/"
    DOWNLOAD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))),'downloads')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL') or 'gpt-5.1-mini'