from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories import ITodoRepository
from app.domain.services import TodoService
from app.infrastructure.database import async_session_maker
from app.infrastructure.repository import SqlAlchemyTodoRepo


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_repository(session: AsyncSession = Depends(get_session)) -> ITodoRepository:
    return SqlAlchemyTodoRepo(session)

def get_service(repository: ITodoRepository = Depends(get_repository)) -> TodoService:
    return TodoService(repository)