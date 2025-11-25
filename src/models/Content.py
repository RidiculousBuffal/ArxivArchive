from pydantic import BaseModel

class FigureB64(BaseModel):
    name: str
    b64: str
    mime:str

class Text(BaseModel):
    name: str
    text: str