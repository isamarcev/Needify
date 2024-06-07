from pydantic import BaseModel


class CategorySchema(BaseModel):
    title: str
    description: str
