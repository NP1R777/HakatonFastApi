from pydantic import BaseModel
from src.event.enums import Location
from pydantic import AnyUrl
from datetime import date, time

class EventIn(BaseModel):
    name: str
    description: str
    location: str
    group_id: int
    external_url: str
    date_event: date
    duration: time
    price: int
    address: str
    city: str
    age_limit: str
