from pydantic import BaseModel
from src.event.enums import Location


class EventIn(BaseModel):
    name: str
    description: str
    location: Location
    group_id: int
