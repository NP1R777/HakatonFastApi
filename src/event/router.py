from core.session import get_db
from database.models import Events
from src.event.schemas import EventIn
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post(
    '/event/create_event',
    response_model=EventIn,
    description="Заполнения мероприятия в базе данных",
    summary="Заполнение мероприятия в базе данных",
    responses={
        200: {"description": "Мероприятие создано!"},
        500: {"description": "Ошибка создания мероприятия"}
    }
)
async def create_event(
        event: EventIn,
        db_connect: AsyncSession = Depends(get_db)
):
    event_data = event.dict()
    event_add = Events(
        name=event_data['name'],
        description=event_data['description'],
        location=event_data['location']
    )
    db_connect.add(event_add)
    await db_connect.flush()
    await db_connect.refresh(event_add)
    return EventIn(
        name=event_add.name,
        description=event_add.description,
        location=event_add.location
    )
