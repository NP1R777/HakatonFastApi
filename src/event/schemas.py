from pydantic import BaseModel
from src.event.enums import Location


class Event(BaseModel):
    name: str
    description: str
    location: Location
