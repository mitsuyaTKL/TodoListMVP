from __future__ import annotations
from abc import ABC, abstractmethod
from app.domain.entities import TodoItem


class ITodoRepository(ABC):

    @abstractmethod
    async def add(self, item: TodoItem) -> TodoItem:
        ...

    @abstractmethod
    async def get_all(self) -> list[TodoItem]:
        ...

    @abstractmethod
    async def delete(self, item_id: int) -> None:
        ...

    @abstractmethod
    async def update(self, item: TodoItem) -> None:
        ...