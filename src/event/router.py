from asyncio import Event
from core.session import get_db
from typing import Optional, List
from database.models import Events
from src.event.schemas import EventIn
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Query

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
        location=event_data['location'],
        group_id=event_data['group_id'],
        external_url=event_data['external_url'],
        date_event=event_data['date_event'],
        duration=event_data['duration'],
        price=event_data['price'],
        address=event_data['address'],
        city=event_data['city'],
        age_limit=event_data['age_limit'],
    )
    db_connect.add(event_add)
    await db_connect.flush()
    await db_connect.refresh(event_add)
    return EventIn(
        name=event_add.name,
        description=event_add.description,
        location=event_add.location,
        group_id=event_add.group_id,
        external_url=event_add.external_url,
        date_event=event_add.date_event,
        duration=event_add.duration,
        price=event_add.price,
        address=event_add.address,
        city=event_add.city,
        age_limit=event_add.age_limit
    )


@router.post(
    '/event/get_all_events',
    description="Получение всех мероприятий из базы данных",
    summary="Получение всех мероприятий из базы данных",
    responses={
        200: {"description": "Мероприятия успешно получены!"},
        500: {"description": "Не удалось получить все мероприятия."}
    }
)
async def get_all_events(db_connect: AsyncSession = Depends(get_db)):
    events = (await db_connect.execute(select(Events))).scalars().all()
    if not events:
        raise HTTPException(status_code=404, detail="Мероприятия не были найдены!")
    else:
        return events


@router.post(
    '/event{id}/',
    description="Получение мероприятия по id",
    summary="Получение мероприятия по id",
    responses={
        200: {"description": "Мероприятие успешно получено!"},
        500: {"description": "При получении мероприятия произошла ошибка"}
    }
)
async def get_event_by_id(id: int,
                          db_connect: AsyncSession = Depends(get_db)):
    event = (await db_connect.execute(select(Events).filter(Events.id == id))).scalar()
    if not event:
        raise HTTPException(status_code=404, detail="Мероприятие не найдено!")
    else:
        return event


@router.post(
    '/event/sort_events',
    description="Сортировка мероприятий во выбранным параметрам",
    summary="Сортировка мероприятий по выбранным параметрам",
    responses={
        200: {"description": "Мероприятия отсортированы успешно!"},
        500: {"description": "Во время сортировки произошла ошибка"}
    }
)
async def sort_events(
        sort_param: str,
        up_or_down: bool,
        sort_by: str = Query(None, description="Параметры сортировки: Дата, Категория, Город"),
        db_connect: AsyncSession = Depends(get_db)):
    events = (await db_connect.execute(select(Events))).scalars()
    if not events:
        raise HTTPException(status_code=404, detail="Мероприятий нет!")
    else:
        sort_columns = {
            "Дата": Events.date_event,
            "Категория": Events.group_id,
            "Город": Events.city
        }

        num_city = {
            "Норильск": 0,
            "Талнах": 1,
            "Кайеркан": 2,
            "Оганер": 3,
            "Дудинка": 4
        }

        sort_for_params = {
            "Город": ["Норильск", "Талнах", "Кайеркан",  "Оганер", "Дудинка"]
        }

        if sort_by:
            valid_sort_columns = [sort_columns[param] for param in sort_by if param in sort_columns]
            if valid_sort_columns:
                events_sort = ((await db_connect.execute(select(
                    Events).order_by(desc(*valid_sort_columns)))).scalars().all())
                return events_sort
