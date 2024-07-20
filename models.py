from pydantic import BaseModel

class URLRequest(BaseModel):
    url: str
    custom_alias: str = None

