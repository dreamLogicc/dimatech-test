from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from user.utils import get_current_user
from user.schemas import User
from account.models import account
from transactions.models import transaction

from user.utils import verify_admin

router = APIRouter(
    prefix='/account',
    tags=['Account']
)


@router.get('/my_account_info')
async def get_account_info(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """
    Получает информацию о всех счетах текущего авторизованного пользователя.

    Args:
        session (AsyncSession): Асинхронная сессия для работы с БД.
        current_user (User): Данные текущего пользователя.

    Returns:
        dict: Словарь с ключом 'account_info', содержащим список счетов пользователя.

    Raises:
        HTTPException: 404 если у пользователя нет счетов.
    """
    query = select(account).where(account.c.user_id == current_user['id'])
    result = await session.execute(query)
    account_info = [dict(r._mapping) for r in result]
    if not account_info:
        raise HTTPException(status_code=404, detail='This user has no accounts')
    return {'account_info': account_info}


@router.get('/admin/user_account_info/{user_id}')
async def get_user_account_info(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
    Получает информацию о всех счетах указанного пользователя.
    Доступно только для администраторов (проверяется через verify_admin).

    Args:
        user_id (int): ID пользователя в БД, для которого запрашиваются счета
        session (AsyncSession): Асинхронная сессия БД
        _ (User): Параметр для проверки прав администратора

    Returns:
        dict: Словарь с ключом 'account_info', содержащим список счетов

    Raises:
        HTTPException: 404 - Если у пользователя нет счетов
        HTTPException: 403 - Если запрашивающий не является администратором
    """
    query = select(account).where(account.c.user_id == user_id)
    result = await session.execute(query)
    account_info = [dict(r._mapping) for r in result]
    if not account_info:
        raise HTTPException(status_code=404, detail='This user has no accounts')
    return {'account_info': account_info}


@router.get('/admin/get_all_accounts')
async def get_all_accounts(
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
    Получает информацию о всех существующих счетах в системе.
    Требует административных прав доступа.

    Args:
        session (AsyncSession): Асинхронная сессия подключения к БД
        _ (User): Параметр для проверки прав администратора

    Returns:
        dict: Словарь с ключом 'accounts', содержащим список всех счетов

    Raises:
        HTTPException: 403 - Если запрашивающий не имеет прав администратора
    """
    query = select(account)
    result = await session.execute(query)
    return {'accounts': [dict(r._mapping) for r in result]}
