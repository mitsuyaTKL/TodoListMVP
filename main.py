from app.data.database import create_session_factory
from app.data.repository import SqlAlchemyTodoRepo
from app.domain.services import TodoService
from app.presentation.presenter import TodoPresenter
from app.presentation.view import TodoView


def main() -> None:
    DB_PATH = "todo.sqlite3"

    session_factory = create_session_factory(DB_PATH)
    repo = SqlAlchemyTodoRepo(session_factory)
    service = TodoService(repo)

    view = TodoView()
    presenter = TodoPresenter(view, service)
    view.presenter = presenter

    presenter.initialize()
    view.mainloop()


if __name__ == "__main__":
    main()