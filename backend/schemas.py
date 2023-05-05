from typing import List
from pydantic import BaseModel


class ImageScheme(BaseModel):
    img: str
    filename:str

class ImageData(BaseModel):
    images: List[ImageScheme]
    label: str