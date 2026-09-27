from __future__ import annotations
from app.domain.entities import Priority, TodoItem, TodoEditData
from app.domain.repositories import ITodoRepository


class TodoService:
    def __init__(self, repository: ITodoRepository) -> None:
        self._repository = repository

    def create_todo(
        self,
        title: str,
        priority: Priority = Priority.MEDIUM,
        deadline = None,
    ) -> TodoItem:
        item = TodoItem(title = title, priority=priority, deadline=deadline)
        return self._repository.add(item)

    def delete_todo(self, todo_id: int) -> None:
        self._find_by_id(todo_id)
        self._repository.delete(todo_id)

    def get_all_todos(self) -> list[TodoItem]:
        return self._repository.get_all()

    def get_todo(self, todo_id: int) -> TodoItem:
        return self._find_by_id(todo_id)

    def edit_todo(
        self,
        todo_id: int,
        data: TodoEditData,
    ) -> TodoItem:
        item = self._find_by_id(todo_id)
        item.change_title(data.title)
        item.change_priority(data.priority)
        item.change_deadline(data.deadline)
        self._repository.update(item)
        return item

    def toggle_completed(self, todo_id: int) -> TodoItem:
        item = self._find_by_id(todo_id)
        item.toggle_completed()
        self._repository.update(item)
        return item

    def clear_completed(self) -> None:
        for item in self._repository.get_all():
            if item.is_completed:
                self._repository.delete(item.id)

    def _find_by_id(self, todo_id: int) -> TodoItem:
        for item in self._repository.get_all():
            if item.id == todo_id:
                return item
        raise ValueError(f"Задача с id = {todo_id} не найдена")