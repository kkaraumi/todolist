from abc import ABC, abstractmethod
from datetime import date, datetime


class Task(ABC):
    _next_id = 1

    def __init__(self, title):
        title = title.strip()
        if not title:
            raise ValueError("Название задачи не может быть пустым.")
        self._id = Task._next_id
        Task._next_id += 1
        self._title = title
        self._is_finished = False

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def is_finished(self):
        return self._is_finished

    def complete(self):
        self._is_finished = True

    def reopen(self):
        self._is_finished = False

    def _status_text(self):
        return "выполнена" if self._is_finished else "не выполнена"

    @abstractmethod
    def description(self):
        pass


class SimpleTask(Task):

    def description(self):
        return f"[{self._id}] {self._title} | статус: {self._status_text()}"


class DeadlineTask(Task):

    def __init__(self, title, deadline):
        super().__init__(title)
        if not isinstance(deadline, date):
            raise ValueError("Срок должен быть датой.")
        self._deadline = deadline

    @property
    def deadline(self):
        return self._deadline

    def description(self):
        return (
            f"[{self._id}] {self._title} | статус: {self._status_text()} "
            f"| срок: {self._deadline.strftime('%d.%m.%Y')}"
        )


class TaskNotFoundError(Exception):
    pass


class TodoList:
    def __init__(self):
        self._tasks = {}

    def add_task(self, task):
        self._tasks[task.id] = task

    def _get(self, task_id):
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Задача с id {task_id} не найдена.")
        return task

    def get_all(self):
        return list(self._tasks.values())

    def get_unfinished(self):
        return [t for t in self._tasks.values() if not t.is_finished]

    def complete_task(self, task_id):
        self._get(task_id).complete()

    def reopen_task(self, task_id):
        self._get(task_id).reopen()

    def remove_task(self, task_id):
        self._get(task_id) 
        del self._tasks[task_id]


class ConsoleApp:
    MENU = (
        "\nВыберите действие:\n"
        "1: Добавить обычную задачу\n"
        "2: Добавить задачу со сроком\n"
        "3: Показать все задачи\n"
        "4: Показать незавершённые задачи\n"
        "5: Отметить задачу выполненной\n"
        "6: Вернуть задачу в незавершённые\n"
        "7: Удалить задачу\n"
        "0: Выход"
    )

    def __init__(self, todo_list):
        self._todo_list = todo_list

    def run(self):
        actions = {
            "1": self._add_simple,
            "2": self._add_deadline,
            "3": lambda: self._show(self._todo_list.get_all()),
            "4": lambda: self._show(self._todo_list.get_unfinished()),
            "5": lambda: self._change(self._todo_list.complete_task, "Задача выполнена."),
            "6": lambda: self._change(self._todo_list.reopen_task, "Задача возвращена в незавершённые."),
            "7": lambda: self._change(self._todo_list.remove_task, "Задача удалена."),
        }
        while True:
            print(self.MENU)
            choice = input("Введите номер: ").strip()
            if choice == "0":
                print("До свидания!")
                break
            action = actions.get(choice)
            if action is None:
                print("Ошибка: нет такого пункта меню.")
                continue
            try:
                action()
            except (ValueError, TaskNotFoundError) as error:
                print(f"Ошибка: {error}")

    def _add_simple(self):
        title = input("Введите название задачи: ")
        self._todo_list.add_task(SimpleTask(title))
        print("Задача добавлена.")

    def _add_deadline(self):
        title = input("Введите название задачи: ")
        raw = input("Введите срок (ДД.ММ.ГГГГ): ").strip()
        try:
            deadline = datetime.strptime(raw, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неверный формат даты, нужен ДД.ММ.ГГГГ.")
        self._todo_list.add_task(DeadlineTask(title, deadline))
        print("Задача добавлена.")

    def _show(self, tasks):
        if not tasks:
            print("Список пуст.")
            return
        for task in tasks:
            print(task.description()) 

    def _change(self, operation, success_message):
        raw = input("Введите id задачи: ").strip()
        try:
            task_id = int(raw)
        except ValueError:
            raise ValueError("id должен быть целым числом.")
        operation(task_id)
        print(success_message)


ConsoleApp(TodoList()).run()