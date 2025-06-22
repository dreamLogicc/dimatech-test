from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta

from sqlalchemy import select, insert
from user.schemas import Token, User
from user.models import user
from user.utils import authenticate_user, create_access_token, get_current_user
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session

from user.utils import verify_admin

router = APIRouter(
    prefix='/user',
    tags=['User']
)


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Аутентификация пользователя и получение JWT токена.

    Args:
        form_data (OAuth2PasswordRequestForm): Форма с данными для входа:
        session (AsyncSession): Асинхронная сессия БД

    Returns:
        dict: Объект с JWT токеном:
            - access_token: str - Токен для авторизации
            - token_type: str - Тип токена (bearer)

    Raises:
        HTTPException: 401 - При неверных учетных данных

    """
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/user")
async def get_user(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем аутентифицированном пользователе.

    Args:
        current_user (User): Данные текущего пользователя (автоматически извлекаются из JWT токена)

    Returns: dict - Информация о пользователе
    """
    return {'user_info': current_user}


@router.get("/admin/user_info/{user_id}")
async def user_info(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
    Получение информации о пользователе по ID (только для администраторов).

    Args:
        user_id (int): ID пользователя в системе
        session (AsyncSession): Асинхронная сессия подключения к БД
        _ (User): Проверка прав администратора

    Returns:
        dict: Детальная информация о пользователе в формате

    Raises:
        HTTPException: 404 - Если пользователь не найден
        HTTPException: 403 - Если запрашивающий не является администратором
    """

    query = select(user).where(user.c.id == user_id)
    result = await session.execute(query)
    user_info = [dict(r._mapping) for r in result]
    if not user_info:
        raise HTTPException(status_code=404, detail='User not found')
    return {'user_info': user_info[0]}


@router.post('/admin/add_user')
async def add_user(
        user_to_add: User,
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
        Создание нового пользователя (доступно только администраторам).

        Args:
            user_to_add (UserCreateSchema): Данные для создания пользователя
            session (AsyncSession): Сессия подключения к БД
            _ (User): Проверка прав администратора

        Returns:
            {'status': 'User added successfully'}

        Raises:
            HTTPException: 400 - При невалидных данных
            HTTPException: 403 - Если нет прав администратора
    """
    try:
        stmt = insert(user).values(**user_to_add.dict())
        await session.execute(stmt)
        await session.commit()
        return {'status': 'User added successfully'}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.delete('/admin/delete_user')
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
        Удаление пользователя по ID (только для администраторов).

        Args:
            user_id (int): ID пользователя для удаления
            session (AsyncSession): Асинхронная сессия подключения к БД
            _ (User): Проверка прав администратора (не используется напрямую)

        Returns:
            dict: Сообщение об успешном удалении в формате:
                {"message": f"User with id {user_id} deleted successfully"}

        Raises:
            HTTPException: 404 - Если пользователь не найден
            HTTPException: 403 - Если запрашивающий не является администратором
    """
    query = select(user).where(user.c.id == user_id)
    result = await session.execute(query)
    user_to_delete = result.scalar_one_or_none()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    await session.execute(
        user.delete().where(user.c.id == user_id)
    )
    await session.commit()

    return {"message": f"User with id {user_id} deleted successfully"}


@router.get('/admin/get_all_users')
async def get_all_users(
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
    Получение списка всех пользователей (только для администраторов).

    Args:
        session (AsyncSession): Асинхронная сессия подключения к БД
        _ (User): Проверка прав администратора (не используется напрямую)

    Returns:
        dict: Словарь с ключом 'users', содержащим список пользователей
        
    Raises:
        HTTPException: 403 - Если запрашивающий не является администратором
    """
    query = select(user)
    result = await session.execute(query)
    return {'users': [dict(r._mapping) for r in result]}
