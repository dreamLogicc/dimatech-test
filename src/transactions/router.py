from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session
from user.utils import get_current_user
from user.schemas import User
from transactions.models import transaction
from transactions.utils import verify_signature
from transactions.schemas import Payment
from config import TRANSACTION_SECRET_KEY
from account.schemas import Account
from account.models import account

from user.utils import verify_admin

router = APIRouter(
    prefix='/transaction',
    tags=['Transaction']
)


@router.get('/transactions_info')
async def transactions_info(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    """
    Получает историю транзакций для текущего авторизованного пользователя.

    Args:
        session (AsyncSession): Асинхронная сессия подключения к БД
        current_user (User): Данные текущего аутентифицированного пользователя

    Returns:
        dict: Словарь с ключом 'transaction_info', содержащим список транзакций пользователя.

    Raises:
        HTTPException: 404 - Если у пользователя нет транзакций
        HTTPException: 401 - Если пользователь не авторизован
    """
    query = select(transaction).where(transaction.c.user_id == current_user['id'])
    result = await session.execute(query)
    transaction_info = [dict(r._mapping) for r in result]
    if not transaction_info:
        raise HTTPException(status_code=404, detail='No transactions')
    return {'transaction_info': transaction_info}


@router.get('/admin/user_transactions_info')
async def transactions_info(
        user_id: int,
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
    Получает историю транзакций для указанного пользователя.
    Требует административных прав доступа.

    Args:
        user_id (int): ID пользователя, для которого запрашиваются транзакции
        session (AsyncSession): Асинхронная сессия подключения к БД
        _ (User): Параметр для проверки прав администратора

    Returns:
        dict: Словарь с информацией о транзакциях пользователя

    Raises:
        HTTPException: 403 - Если запрашивающий не имеет прав администратора
        HTTPException: 404 - Если пользователь не найден (опционально)
    """
    query = select(transaction).where(transaction.c.user_id == user_id)
    result = await session.execute(query)
    return {'user_id': user_id, 'transactions': [dict(r._mapping) for r in result]}


@router.get('/admin/get_all_transactions')
async def get_all_transactions(
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(verify_admin),
):
    """
    Получает полный список всех транзакций в системе.
    Требует административных прав доступа.

    Args:
        session (AsyncSession): Асинхронная сессия подключения к БД
        _ (User): Параметр для проверки прав администратора

    Returns:
        dict: Словарь с ключом 'transactions', содержащим список всех транзакций

    Raises:
        HTTPException: 403 - Если запрашивающий не имеет прав администратора
    """
    query = select(transaction)
    result = await session.execute(query)
    return {'transactions': [dict(r._mapping) for r in result]}


@router.post('/make_transaction')
async def make_transaction(
        data: Payment,
        session: AsyncSession = Depends(get_async_session),
        _: User = Depends(get_current_user)
):
    """
        Обрабатывает новую финансовую транзакцию и обновляет баланс счета.

        Args:
            transaction_data (Payment): Данные транзакции
            session (AsyncSession): Сессия подключения к БД
            current_user (User): Текущий аутентифицированный пользователь

        Returns:
            {
                "message": str
                "new_balance": float - Новый баланс счета,
            }

        Raises:
            HTTPException: 403 - При невалидной подписи транзакции
            HTTPException: 400 - При попытке повторной обработки транзакции
        """
    if not verify_signature(data, TRANSACTION_SECRET_KEY):
        raise HTTPException(
            status_code=403,
            detail="Invalid signature"
        )

    existing_transaction = await session.execute(
        select(transaction).where(transaction.c.transaction_id == data.transaction_id)
    )
    if existing_transaction.scalar():
        raise HTTPException(
            status_code=400,
            detail="Transaction already processed"
        )

    account_exists = await session.execute(
        select(account).where(
            and_(
                account.c.user_id == data.user_id,
                account.c.id == data.account_id
            )
        )
    )

    if account_exists.scalar() is None:
        await session.execute(
            insert(account).values(
                user_id=data.user_id,
                account_id=data.account_id,
                amount=data.amount
            )
        )
    else:
        await session.execute(
            update(account)
            .where(
                and_(
                    account.c.user_id == data.user_id,
                    account.c.id == data.account_id
                )
            )
            .values(amount=account.c.amount + data.amount)
        )

    await session.execute(
        insert(transaction).values(
            transaction_id=data.transaction_id,
            user_id=data.user_id,
            account_id=data.account_id,
            amount=data.amount,
            signature=data.signature
        )
    )

    await session.commit()

    updated_balance = await session.execute(
        select(account.c.amount).where(
            and_(
                account.c.user_id == data.user_id,
                account.c.id == data.account_id
            )
        )
    )

    return {
        "message": "Transaction processed",
        "new_balance": updated_balance.scalar()
    }
