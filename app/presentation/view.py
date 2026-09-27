import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from app.domain.entities import Priority, TodoEditData, TodoItem
from app.presentation.interfaces import ITodoView

DEADLINE_FORMAT = "%d.%m.%Y %H:%M"
PRIORITY_ORDER = {p.value: i for i, p in enumerate(Priority)}
STATUS_ORDER = {"Активна": 0, "Выполнена": 1}

HEADINGS = {
    "id": "ID",
    "title": "Задача",
    "status": "Статус",
    "priority": "Приоритет",
    "created": "Создана",
    "deadline": "Дедлайн",
}

class TodoView(tk.Tk, ITodoView):
    def __init__(self) -> None:
        super().__init__()
        self.presenter = None
        self._editing_id: int | None = None

        self._sort_column: int | None = None
        self._sort_reverse: bool = False
        self.title("TodoList by Mitsuya ")
        self.geometry("1000x600")
        self.minsize(775, 400)

        self._build_ui()


    def _build_ui(self) -> None:
        row1 = ttk.Frame(self, padding=(8, 8, 8, 4))
        row1.pack(fill=tk.X)

        ttk.Label(row1, text="Задача:", width=9, anchor="w").pack(side=tk.LEFT)
        self._entry_title = ttk.Entry(row1)
        self._entry_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        self._entry_title.bind("<Return>", lambda e: self._on_enter())

        ttk.Label(row1, text="Приоритет:").pack(side=tk.LEFT, padx=(0, 4))
        self._priority_var = tk.StringVar(value=Priority.MEDIUM.value)
        self._priority_combo = ttk.Combobox(
            row1,
            textvariable=self._priority_var,
            values=[p.value for p in Priority],
            state="readonly",
            width=10,
        )
        self._priority_combo.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row1, text="Дедлайн:").pack(side=tk.LEFT, padx=(0, 4))
        self._entry_deadline = ttk.Entry(row1, width=18)
        self._entry_deadline.pack(side=tk.LEFT, padx=(0, 12))

        self._btn_add = ttk.Button(row1, text="Добавить", command=self._on_add)
        self._btn_add.pack(side=tk.LEFT)

        row2 = ttk.Frame(self, padding=(8, 0, 8, 8))
        row2.pack(fill=tk.X)

        ttk.Label(row2, text="Фильтр:", width=9, anchor="w").pack(side=tk.LEFT)
        self._filter_var = tk.StringVar(value="all")
        self._filter_combo = ttk.Combobox(
            row2,
            textvariable=self._filter_var,
            values=["all", "active", "completed"],
            state="readonly",
            width=10,
        )
        self._filter_combo.pack(side=tk.LEFT, padx=(0, 16))
        self._filter_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

        self._btn_toggle = ttk.Button(
            row2, text="Выполнить / вернуть", command=self._on_toggle
        )
        self._btn_toggle.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_edit = ttk.Button(
            row2, text="Редактировать", command=self._on_edit
        )
        self._btn_edit.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_delete = ttk.Button(
            row2, text="Удалить", command=self._on_delete
        )
        self._btn_delete.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_save = ttk.Button(row2, text="Сохранить", command=self._on_save)
        self._btn_cancel = ttk.Button(row2, text="Отмена", command=self._on_cancel)

        self._btn_clear = ttk.Button(
            row2, text="Очистить завершённые", command=self._on_clear_completed
        )
        self._btn_clear.pack(side=tk.RIGHT)

        tree_frame = ttk.Frame(self, padding=(8, 0, 8, 0))
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "status", "priority", "created", "deadline")
        self._tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )

        for col, width in (
                ("id", 50),
                ("title", 350),
                ("status", 100),
                ("priority", 100),
                ("created", 140),
                ("deadline", 140),
        ):
            self._tree.heading(
                col,
                text=HEADINGS[col],
                command=lambda c=col: self._on_heading_click(c),
            )
            self._tree.column(
                col,
                width=width,
                anchor=tk.W if col == "title" else tk.CENTER,
                stretch=(col == "title"),
            )

        scrollbar = ttk.Scrollbar(
            tree_frame, orient=tk.VERTICAL, command=self._tree.yview
        )
        self._tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._tree.bind("<Double-1>", self._on_double_click)

        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill=tk.X)

        self._label_count = ttk.Label(bottom, text="Всего: 0")
        self._label_count.pack(side=tk.LEFT)

        ttk.Label(
            bottom, text="Двойной щелчок по задаче переключает статус"
        ).pack(side=tk.RIGHT)


    def show_todos(self, todos: list[TodoItem]) -> None:
        for iid in self._tree.get_children():
            self._tree.delete(iid)
        for item in todos:
            self._tree.insert("", "end", iid=str(item.id), values=self._row(item))
        self._update_counter()
        if self._sort_column is not None:
            self._resort_tree()

    def add_todo(self, item: TodoItem) -> None:
        self._tree.insert("", "end", iid=str(item.id), values=self._row(item))
        self._update_counter()

    def update_todo(self, item: TodoItem) -> None:
        iid = str(item.id)
        if self._tree.exists(iid):
            self._tree.item(iid, values=self._row(item))

    def remove_todo(self, todo_id: int) -> None:
        iid = str(todo_id)
        if self._tree.exists(iid):
            self._tree.delete(iid)
            self._update_counter()

    def show_error(self, message: str) -> None:
        messagebox.showerror("Ошибка", message)

    def get_input_title(self) -> str:
        return self._entry_title.get()

    def get_input_priority(self) -> Priority:
        return Priority(self._priority_var.get())

    def get_input_deadline(self) -> datetime | None:
        raw = self._entry_deadline.get().strip()
        if not raw:
            return None
        try:
            return datetime.strptime(raw, DEADLINE_FORMAT)
        except ValueError:
            raise ValueError(
                f"Неверный формат дедлайна. Ожидается {DEADLINE_FORMAT}"
            )

    def get_selected_id(self) -> int | None:
        selection = self._tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def get_filter(self) -> str:
        return self._filter_var.get()

    def clear_input(self) -> None:
        self._entry_title.delete(0, tk.END)
        self._entry_deadline.delete(0, tk.END)
        self._priority_var.set(Priority.MEDIUM.value)
        self._entry_title.focus()

    def show_edit_panel(self, item: TodoItem) -> None:
        self._editing_id = item.id

        self._entry_title.delete(0, tk.END)
        self._entry_title.insert(0, item.title)

        self._entry_deadline.delete(0, tk.END)
        if item.deadline is not None:
            self._entry_deadline.insert(0, item.deadline.strftime(DEADLINE_FORMAT))

        self._priority_var.set(item.priority.value)

        self._btn_add.configure(state=tk.DISABLED)

        self._btn_save.pack(side=tk.LEFT, padx=(0, 4))
        self._btn_cancel.pack(side=tk.LEFT, padx=(0, 4))

        self._btn_toggle.configure(state=tk.DISABLED)
        self._btn_edit.configure(state=tk.DISABLED)
        self._btn_delete.configure(state=tk.DISABLED)
        self._btn_clear.configure(state=tk.DISABLED)
        self._filter_combo.configure(state=tk.DISABLED)

        self._entry_title.focus()
        self._entry_title.select_range(0, tk.END)

    def hide_edit_panel(self) -> None:
        self._editing_id = None

        self._entry_title.delete(0, tk.END)
        self._entry_deadline.delete(0, tk.END)
        self._priority_var.set(Priority.MEDIUM.value)

        self._btn_save.pack_forget()
        self._btn_cancel.pack_forget()

        self._btn_add.configure(state=tk.NORMAL)

        self._btn_toggle.configure(state=tk.NORMAL)
        self._btn_edit.configure(state=tk.NORMAL)
        self._btn_delete.configure(state=tk.NORMAL)
        self._btn_clear.configure(state=tk.NORMAL)
        self._filter_combo.configure(state="readonly")

        self._entry_title.focus()


    @staticmethod
    def _row(item: TodoItem) -> tuple:
        status = "Выполнена" if item.is_completed else "Активна"
        created = item.created_at.strftime(DEADLINE_FORMAT)
        deadline = item.deadline.strftime(DEADLINE_FORMAT) if item.deadline else "—"
        return (item.id, item.title, status, item.priority.value, created, deadline)

    def _update_counter(self) -> None:
        self._label_count.configure(text=f"Всего: {len(self._tree.get_children())}")

    def _on_heading_click(self, column: str) -> None:
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        self._update_heading_arrows()
        self._resort_tree()

    def _update_heading_arrows(self) -> None:
        for col, base in HEADINGS.items():
            if col == self._sort_column:
                arrow = " \u2228" if self._sort_reverse else " \u2227"
                self._tree.heading(col, text=base + arrow)
            else:
                self._tree.heading(col, text=base)

    def _resort_tree(self) -> None:
        if self._sort_column is None:
            return

        col_index = self._tree["columns"].index(self._sort_column)

        rows = [
            (iid, self._tree.item(iid, "values"))
            for iid in self._tree.get_children()
        ]
        rows.sort(key=lambda r: self._sort_key(r[1][col_index]), reverse=self._sort_reverse)

        for new_index, (iid, _) in enumerate(rows):
            self._tree.move(iid, "", new_index)

    def _sort_key(self, value):
        col = self._sort_column

        if col == "id":
            return int(value)
        if col == "priority":
            return PRIORITY_ORDER.get(value, 999)
        if col == "status":
            return STATUS_ORDER.get(value, 999)
        if col == "deadline":
            return (1, "") if value == "—" else (0, value)
        return str(value).lower()

    def _on_enter(self) -> None:
        if self._editing_id is not None:
            self._on_save()
        else:
            self._on_add()

    def _on_add(self) -> None:
        if self.presenter is not None:
            self.presenter.on_add_clicked()

    def _on_save(self) -> None:
        if self.presenter is None or self._editing_id is None:
            return
        try:
            data = TodoEditData(
                title=self._entry_title.get(),
                priority=Priority(self._priority_var.get()),
                deadline=self.get_input_deadline(),
            )
        except ValueError as e:
            self.show_error(str(e))
            return
        self.presenter.on_edit_save(self._editing_id, data)

    def _on_cancel(self) -> None:
        if self.presenter is not None:
            self.presenter.on_edit_cancel()

    def _on_toggle(self) -> None:
        if self.presenter is not None:
            self.presenter.on_toggle_clicked()

    def _on_edit(self) -> None:
        if self.presenter is not None:
            self.presenter.on_edit_clicked()

    def _on_delete(self) -> None:
        if self.presenter is not None:
            self.presenter.on_delete_clicked()

    def _on_clear_completed(self) -> None:
        if self.presenter is not None:
            self.presenter.on_clear_completed_clicked()

    def _on_filter_changed(self, event) -> None:
        if self.presenter is not None:
            self.presenter.on_filter_changed(self._filter_var.get())

    def _on_double_click(self, event) -> None:
        if self._tree.identify_region(event.x, event.y) != "cell":
            return
        self._on_toggle()