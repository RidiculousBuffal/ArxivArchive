import base64

from langchain_core.messages import ImageContentBlock
from langchain_core.messages.content import create_image_block, create_text_block
from langchain_openai import ChatOpenAI

from src.config.Config import Config
from src.models.Content import FigureB64, Text


class BaseAI:
    model = ChatOpenAI(api_key=Config.OPENAI_API_KEY, base_url=Config.OPENAI_BASE_URL, model=Config.OPENAI_MODEL,
                       use_responses_api=True)

    def buildB64ImageContent(self, image: FigureB64):
        return create_image_block(mime_type=image.mime, base64=image.b64)

    def buildTextContentBlock(self, text: Text):
        return create_text_block(text=f"""------- TITLE: {text.title} --------\n{text.text}\n""")


