import hashlib
from datetime import datetime
from jose import jwt, JWTError
from database.models import User
from sqlalchemy import and_, select
from core.settings import AppSettings
from core.session import get_db, get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from src.user.auth import create_refresh_token, create_access_token
from src.user.schemas import UserIn, UserOut, TokenResponse, UserUpdate
from src.dependencies.autentification import get_token_payload, get_current_user


router = APIRouter()

@router.post(
    '/user/registration',
    response_model=UserOut.Create,
    description="Регистрация нового пользователя системы.",
    summary="Регистрация нового пользователя системы.",
    responses={
        200: {"description": "Пользователь создан"},
        500: {"description": "Ошибка создания пользователя"},
    }
)
async def register(
        user: UserIn.Create,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> UserIn.Create:
    user_data = user.dict()
    user_add = User(
        username=user_data["username"],
        password_hash=hashlib.sha256(user_data["password"].encode()).hexdigest(),
        email=user_data["email"],
        date_of_birth=user_data["date_of_birth"],
        preferences=user_data["preferences"],
    )
    db_connect.add(user_add)
    await db_connect.flush()
    await db_connect.refresh(user_add)
    user_add.refresh_token = create_refresh_token(user_add.id, settings=settings)
    return UserOut.Create(
        created_at=user_add.created_at,
        update_at=user_add.update_at,
        deleted_at=user_add.deleted_at,
        id=user_add.id,
        username=user_add.username,
        email=user_add.email,
        date_of_birth=user_add.date_of_birth,
        preferences=user_add.preferences,
    )



@router.post(
    '/user/login',
    response_model=TokenResponse,
    description="Авторизация пользователя.",
    summary="Авторизация пользователя.",
    responses={
        200: {"description": "Успешная авторизация"},
        500: {
            "description": "Ошибка авторизации пользователя",
        },
        404: {
            "description": "Пользователя с таким номером не существует",
        },
        401: {
            "description": "Пользователь не верифицирован",
        },
    }
)
async def login(
        user_in: UserIn.Login,
        response: Response,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> TokenResponse:
    user_data = user_in.dict()
    password_hash = hashlib.sha256(user_data["password"].encode()).hexdigest()
    user = (
        await db_connect.execute(
            select(User).filter(
                and_(
                    User.password_hash == password_hash,
                    User.username == user_data["username"]
                )
            )
        )
    ).scalar()
    if not user:
        raise HTTPException(status_code=404, detail="Не найден пользователь")
    access_token = create_access_token(user.id, settings=settings)
    user.refresh_token = create_refresh_token(user.id, settings=settings)
    response.set_cookie(
        key="refresh_token",
        value=user.refresh_token,
        httponly=True,
        max_age=3600,
        secure=True,
        samesite="Lax"
    )

    if access_token:
        return TokenResponse(
            user_id=user.id,
            username=user.username,
            access_token=access_token,
            refresh_token=user.refresh_token,
            token_type='bearer'
        )



@router.post(
    "/user/me",
    dependencies=[Depends(get_token_payload)]
)
async def me(
        current_user: User = Depends(get_current_user)
):
    return UserOut.Me(
        created_at=current_user.created_at,
        update_at=current_user.update_at,
        deleted_at=current_user.deleted_at,
        id=current_user.id,
        password=current_user.password_hash,
        username=current_user.username,
        refresh_token=current_user.refresh_token,
    )



@router.post(
    "/user/refresh",
    description="Обновление токена доступа.",
    summary="Обновление токена доступа.",
    response_model=TokenResponse,
    responses={
        200: {"description": "Успешное обновление токена"},
        500: {"description": "Ошибка обновление токена"},
        401: {"description": "Невалидный refresh token"}
    }
)
async def refresh(
        refresh_token: str,
        request: Request,
        response: Response,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> TokenResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Невалидный refresh token")
    try:
        payload = jwt.decode(refresh_token, settings.jwt_key, algorithms=settings.jwt_algorithm)
        user = (await db_connect.execute(select(User).filter(User.id == payload.get("user_id")))).scalar()
        if not user:
            raise HTTPException(status_code=401, detail="Невалидный refresh token")
        new_access_token = create_access_token(user.id, settings=settings)
        new_refresh_token = create_refresh_token(user.id, settings=settings)
        user.refresh_token = new_refresh_token

        response.set_cookie(
            key="refresh_token",
            value=user.refresh_token,
            httponly=True,
            max_age=3600,
            secure=True,
            samesite="Lax"
        )

        return TokenResponse(
            user_id=user.id,
            username=user.username,
            access_token=new_access_token,
            refresh_token=user.refresh_token,
            token_type='bearer'
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный refresh token")



@router.delete(
    "/user/delete_user",
    description="Удаление пользователя из базы данных",
    summary="Удаление пользователей из базы данных",
    responses = {
        200: {"description": "Мероприятие успешно удалено"},
        500: {"description": "Мероприятие не было найдено"}
    }
)
async def delete_user(
        id: int,
        db_connect: AsyncSession = Depends(get_db),
):
    user_data: User = (await db_connect.execute(select(User).filter(User.id == id,
                                                                    User.deleted_at.is_(None)))).scalar()
    if not user_data:
        return HTTPException(status_code=404, detail="Пользователь с таким id не найден или уже удалён")
    else:
        user_data.deleted_at = datetime.now()
        return {"message": "Пользователь успешно удалён!"}



@router.post(
    "/user/change_data",
    description="Изменение данных существующего пользователя",
    summary="Изменение данных существующего пользователя",
    responses={
        200: {"description": "Данные успешно изменены!"},
        500: {"description": "Данные изменить не удалось"}
    }
)
async def change_data(
        id: int,
        user_update: UserUpdate,
        db_connect: AsyncSession = Depends(get_db),
):
    user_data: User = (await db_connect.execute(select(User).filter(User.id == id))).scalar()
    if not user_data:
        return HTTPException(status_code=404, detail="Пользователь не найден!")
    else:
        if user_update.username != "string":
            user_data.username = user_update.username

        if user_update.password != "string":
            user_data.password_hash = hashlib.sha256(user_update.password.encode()).hexdigest()

        if user_update.email != "user@example.com":
            user_data.email = user_update.email

        if user_update.preferences != [0]:
            user_data.preferences = user_update.preferences

        user_data.update_at = datetime.now()

        await db_connect.commit()
        await db_connect.refresh(user_data)

        return {"message": "Данные пользователя успешно изменены!"}


@router.post(
    "/user/get_all_users",
    description="Получение всех пользователей из базы данных",
    summary="Получение всех пользователей из базы данных",
    responses={
        200: {"description": "Все пользователи получены!"},
        500: {"description": "Не удалось получить всех пользователей"}
    }
)
async def get_all_users(db_connect: AsyncSession = Depends(get_db)):
    user_data = (await db_connect.execute(select(User).filter(User.deleted_at.is_(None)))).scalars().all()
    if not user_data:
        raise HTTPException(status_code=404, detail="Пользователей нет в базе данных!")
    else:
        return user_data
