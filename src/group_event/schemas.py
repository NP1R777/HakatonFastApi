from pydantic import BaseModel

class GroupEvent(BaseModel):
    name: str
    description: str
