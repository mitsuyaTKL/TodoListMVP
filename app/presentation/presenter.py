from datetime import datetime

from app.domain.entities import Priority, TodoEditData
from app.domain.services import TodoService
from app.presentation.interfaces import ITodoView


class TodoPresenter:
    def __init__(self, view: ITodoView, service: TodoService) -> None:
        self._view = view
        self._service = service
        self._filter = "all"

    def initialize(self) -> None:
        self.refresh()


    def on_add_clicked(self) -> None:
        try:
            title = self._view.get_input_title()
            priority = self._view.get_input_priority()
            deadline = self._view.get_input_deadline()
            item = self._service.create_todo(title, priority, deadline)
        except ValueError as e:
            self._view.show_error(str(e))
            return
        self._view.clear_input()
        if self._matches_filter(item):
            self._view.add_todo(item)


    def on_toggle_clicked(self) -> None:
        todo_id = self._view.get_selected_id()
        if todo_id is None:
            self._view.show_error("Выберите задачу")
            return
        try:
            item = self._service.toggle_completed(todo_id)
        except ValueError as e:
            self._view.show_error(str(e))
            return
        if self._filter != "all":
            self.refresh()
        else:
            self._view.update_todo(item)


    def on_edit_clicked(self) -> None:
        todo_id = self._view.get_selected_id()
        if todo_id is None:
            self._view.show_error("Выберите задачу")
            return
        try:
            item = self._service.get_todo(todo_id)
        except ValueError as e:
            self._view.show_error(str(e))
            return
        self._view.show_edit_panel(item)


    def on_edit_save(self, todo_id: int, data: TodoEditData) -> None:
        try:
            updated = self._service.edit_todo(todo_id, data)
        except ValueError as e:
            self._view.show_error(str(e))
            return
        self._view.hide_edit_panel()
        self._view.update_todo(updated)

    def on_edit_cancel(self) -> None:
        self._view.hide_edit_panel()

    def on_delete_clicked(self) -> None:
        todo_id = self._view.get_selected_id()
        if todo_id is None:
            self._view.show_error("Выберите задачу")
            return
        try:
            self._service.delete_todo(todo_id)
        except ValueError as e:
            self._view.show_error(str(e))
            return
        self._view.remove_todo(todo_id)


    def on_clear_completed_clicked(self) -> None:
        self._service.clear_completed()
        self.refresh()


    def on_filter_changed(self, filter_mode: str) -> None:
        self._filter = filter_mode
        self.refresh()

    def refresh(self) -> None:
        todos = self._service.get_all_todos()
        filtered = [t for t in todos if self._matches_filter(t)]
        self._view.show_todos(filtered)

    def _matches_filter(self, item) -> bool:
        if self._filter == "active":
            return not item.is_completed
        if self._filter == "completed":
            return item.is_completed
        return True