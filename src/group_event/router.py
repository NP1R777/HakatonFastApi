from core.session import get_db
from fastapi import APIRouter, Depends
from database.models import GroupsEvent
from sqlalchemy.ext.asyncio import AsyncSession
from src.group_event.schemas import GroupEventIn

router = APIRouter()


@router.post(
    "/event/create_group_event",
    response_model=GroupEventIn,
    description="Создание групп мероприятий в базе данных",
    summary="Создание групп мероприятий в базе данных"
)
async def create_group_event(
        group_event: GroupEventIn,
        db_connect: AsyncSession = Depends(get_db)
):
    group_event_data = group_event.dict()
    group_event_add = GroupsEvent(**group_event_data)
    db_connect.add(group_event_add)
    await db_connect.flush()
    await db_connect.refresh(group_event_add)
    return GroupEventIn(**group_event_data)
