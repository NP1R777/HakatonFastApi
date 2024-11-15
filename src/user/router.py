import hashlib
from jose import jwt, JWTError
from database.models import User
from sqlalchemy import and_, select
from core.settings import AppSettings
from core.session import get_db, get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from src.user.schemas import UserIn, UserOut, TokenResponse
from src.user.auth import create_refresh_token, create_access_token
from src.dependencies.autentification import get_token_payload, get_current_user


router = APIRouter()

@router.post(
    '/user/registration',
    response_model=UserOut.Create,
    description="Регистрация нового пользователя системы.",
    summary="Регистрация нового пользователя системы.",
    responses={
        200: {"description": "Пользователь создан"},
        500: {
            "description": "Ошибка создания пользователя",
        },
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
        phone=user_data["phone"],
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
        phone=user_add.phone,
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
        500: {
            "description": "Ошибка обновление токена",
        },
        401: {
            "description": "Невалидный refresh token",
        },
    }
)
async def refresh(
        refresh_token: str,
        db_connect: AsyncSession = Depends(get_db),
        settings: AppSettings = Depends(get_settings)
) -> TokenResponse:
    try:
        payload = jwt.decode(refresh_token, settings.jwt_key, algorithms=settings.jwt_algorithm)
        user = (await db_connect.execute(select(User).filter(User.id == payload.get("user_id")))).scalar()
        if not user:
            raise HTTPException(status_code=401, detail="Невалидный refresh token")
        new_access_token = create_access_token(user.id, settings=settings)
        return TokenResponse(
            user_id=user.id,
            username=user.username,
            access_token=new_access_token,
            refresh_token=user.refresh_token,
            token_type='bearer'
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный refresh token")
