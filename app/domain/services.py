from __future__ import annotations
from app.domain.entities import Priority, TodoItem
from app.domain.exceptions import TodoNotFoundError
from app.domain.repositories import ITodoRepository
from datetime import datetime

PRIORITY_ORDER = {p.value: i for i, p in enumerate(Priority)}

class TodoService:
    def __init__(self, repository: ITodoRepository) -> None:
        self._repository = repository

    async def create_todo(
        self,
        title: str,
        priority: Priority = Priority.MEDIUM,
        deadline = None,
    ) -> TodoItem:
        item = TodoItem(title = title, priority=priority, deadline=deadline)
        return await self._repository.add(item)

    async def delete_todo(self, todo_id: int) -> None:
        await self._find_by_id(todo_id)
        await self._repository.delete(todo_id)

    async def get_todos(
        self,
        *,
        filter_mode: str = "all",
        sort: str = "created_at",
    ) -> list[TodoItem]:
        items = await self._repository.get_all()

        if filter_mode == "active":
            items = [i for i in items if not i.is_completed]
        elif filter_mode == "completed":
            items = [i for i in items if i.is_completed]

        reverse = sort.startswith("-")
        field = sort.lstrip("-")
        items = self._sort_items(items, field, reverse)

        return items

    async def get_todo(self, todo_id: int) -> TodoItem:
        return await self._find_by_id(todo_id)

    async def edit_todo(
        self,
        todo_id: int,
        *,
        title: str | None = None,
        priority: Priority | None = None,
        deadline: datetime | None = None,
        update_deadline: bool = False,
    ) -> TodoItem:
        item = await self._find_by_id(todo_id)
        if title is not None:
            item.change_title(title)
        if priority is not None:
            item.change_priority(priority)
        if update_deadline:
            item.change_deadline(deadline)
        await self._repository.update(item)
        return item

    async def toggle_completed(self, todo_id: int) -> TodoItem:
        item = await self._find_by_id(todo_id)
        item.toggle_completed()
        await self._repository.update(item)
        return item

    async def clear_completed(self) -> None:
        items = await self._repository.get_all()
        for item in items:
            if item.is_completed:
                await self._repository.delete(item.id)

    async def _find_by_id(self, todo_id: int) -> TodoItem:
        items = await self._repository.get_all()
        for item in items:
            if item.id == todo_id:
                return item
        raise TodoNotFoundError(f"Задача с id = {todo_id} не найдена")

    @staticmethod
    def _sort_items(items: list[TodoItem], field: str, reverse: bool) -> list[TodoItem]:
        extractors = {
            "created_at": lambda i: i.created_at,
            "title": lambda i: i.title.lower(),
            "priority": lambda i: PRIORITY_ORDER[i.priority.value],
            "deadline": lambda i: (i.deadline is None, i.deadline or datetime.max),
        }
        key = extractors.get(field, extractors["created_at"])
        return sorted(items, key=key, reverse=reverse)