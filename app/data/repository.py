from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import  sessionmaker

from app.data.models import TodoModel
from app.domain.entities import TodoItem
from app.domain.repositories import ITodoRepository


class SqlAlchemyTodoRepo(ITodoRepository):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def add(self, item: TodoItem) -> TodoItem:
        with self._session_factory() as session:
            model = self._to_model(item)
            session.add(model)
            session.commit()
            session.refresh(model)
            item.assign_id(model.id)
            return item

    def get_all(self) -> list[TodoItem]:
        with self._session_factory() as session:
            stmt = select(TodoModel).order_by(TodoModel.created_at)
            models = session.scalars(stmt).all()
            return [self._to_domain(m) for m in models]

    def delete(self, item_id: int) -> None:
        with self._session_factory() as session:
            model = session.get(TodoModel, item_id)
            if model is not None:
                session.delete(model)
                session.commit()

    def update(self, item: TodoItem) -> None:
        if item.id is None:
            raise ValueError("Нельзя обновить задачу без ID")
        with self._session_factory() as session:
            model = session.get(TodoModel, item.id)
            if model is None:
                raise ValueError("Задача с таким ID не найдена в БД")
            model.title = item.title
            model.priority = item.priority
            model.is_completed = item.is_completed
            model.created_at = item.created_at
            model.deadline = item.deadline
            session.commit()

    @staticmethod
    def _to_model(item: TodoItem) -> TodoModel:
        model = TodoModel()
        model.title = item.title
        model.is_completed = item.is_completed
        model.priority = item.priority
        model.created_at = item.created_at
        model.deadline = item.deadline
        return model

    @staticmethod
    def _to_domain(model: TodoModel) -> TodoItem:
        return TodoItem(
            title=model.title,
            priority=model.priority,
            item_id=model.id,
            is_completed=model.is_completed,
            created_at=model.created_at,
            deadline=model.deadline,
        )