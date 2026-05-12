from __future__ import annotations

from datetime import (
    datetime,  # noqa: TC003 (Pydantic requires this at runtime.)
)
from enum import StrEnum
from pathlib import Path
from tkinter import (
    END,
    BooleanVar,
    Button,
    Checkbutton,
    Frame,
    Label,
    OptionMenu,
    StringVar,
    Text,
    Tk,
    Widget,
)
from tkinter.font import BOLD, Font
from tkinter.messagebox import askyesno

from pydantic import BaseModel, TypeAdapter
from tkcalendar import DateEntry


class Priority(StrEnum):
    Critical = "Critical"
    High = "High"
    Medium = "Medium"
    Low = "Low"


class Task(BaseModel):
    content: str
    done: bool
    priority: Priority | None = None
    due_date: datetime | None = None


class TaskWidget(Frame):
    def __init__(self, master: Widget, task: Task, index: int) -> None:
        super().__init__(master)
        self.task = task
        self.construct()
        self.index = index

    def construct(self) -> None:
        self.columnconfigure(1, weight=1)
        self.done_var = BooleanVar(value=self.task.done)
        self.check = Checkbutton(
            self,
            variable=self.done_var,
            command=self.toggle_done,
        )
        self.check.grid(row=0, column=0, sticky="ew")

        self.content_label = Label(self, text=self.task.content)
        self.content_label.grid(row=0, column=1, sticky="ew")

        date_text = (
            self.task.due_date.strftime("%Y-%m-%d %H:%M")
            if self.task.due_date
            else ""
        )
        self.date_label = Label(self, text=date_text)
        self.date_label.grid(row=0, column=2, sticky="ew")

        priority_text = self.task.priority.value if self.task.priority else ""
        self.priority_label = Label(self, text=priority_text)
        self.priority_label.grid(row=0, column=3, sticky="ew")

        self.delete_button = Button(self, text="Delete", command=self.delete)
        self.delete_button.grid(row=0, column=4, sticky="w")

    def delete(self) -> None:
        if askyesno(message="Delete?"):
            self.event_generate("<<Delete>>")
            self.destroy()

    def toggle_done(self) -> None:
        self.task.done = self.done_var.get()


class App(Frame):
    ta = TypeAdapter(dict[int, Task])
    TASKS_FILE = "tasks.json"

    def __init__(self, master: Tk) -> None:
        super().__init__(master)
        self.tasks = self.load_tasks()

        self.font = Font(family="monospace", weight=BOLD, size=16)
        self.grid(row=0, column=0, sticky="nesw")
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.pack(fill="both", expand=True)

        self.bind("<Destroy>", lambda _e: self.save_tasks())

    def construct(self) -> None:
        self.new_priority = StringVar()

        self.input_frame = Frame(self)
        self.input_frame.grid(row=0, column=0, sticky="nesw", pady=10)
        self.input_frame.columnconfigure(1, weight=1)

        self.content_label = Label(self.input_frame, text="Task Content:")
        self.content_label.grid(row=0, column=0, sticky="ew")
        self.content_box = Text(
            self.input_frame,
            height=3,
            width=40,
        )
        self.content_box.grid(row=0, column=1, sticky="ew", padx=5)

        self.date_label = Label(
            self.input_frame,
            text="Due Date:",
        )
        self.date_label.grid(row=1, column=0, sticky="ew")
        self.date_box = DateEntry(self.input_frame)
        self.date_box.grid(row=1, column=1, sticky="ew", padx=5)

        self.priority_label = Label(self.input_frame, text="Priority:")
        self.priority_label.grid(row=2, column=0, sticky="ew")
        self.priority_options = OptionMenu(
            self.input_frame,
            self.new_priority,
            *(v.value for v in Priority),
        )
        self.priority_options.grid(row=2, column=1, sticky="ew", padx=5)

        self.button = Button(
            self.input_frame,
            text="Add Task",
            command=self.add_task,
        )
        self.button.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

        self.tasks_frame = Frame(self)
        self.tasks_frame.grid(row=1, column=0, sticky="nesw")
        self.tasks_frame.columnconfigure(0, weight=1)

        for index, task in self.tasks.items():
            task_widget = TaskWidget(self.tasks_frame, task, index)

            def idk(task_widget: TaskWidget = task_widget) -> None:
                print("deleted")
                del self.tasks[task_widget.index]

            task_widget.bind(
                "<<Delete>>",
                lambda _e: idk(),
            )
            task_widget.grid(sticky="ew")

    def add_task(self) -> None:
        content = self.content_box.get(1.0, END).strip()
        if not content:
            return
        priority = (
            Priority(self.new_priority.get())
            if self.new_priority.get()
            else None
        )
        task = Task(
            content=content,
            done=False,
            priority=priority,
            due_date=self.date_box.get_date(),
        )

        next_id = 0
        while next_id in self.tasks:
            next_id += 1
        self.tasks[next_id] = task

        task_widget = TaskWidget(self.tasks_frame, task, next_id)

        def idk(task_widget: TaskWidget = task_widget) -> None:
            print("deleted")
            del self.tasks[task_widget.index]

        task_widget.bind(
            "<<Delete>>",
            lambda _e: idk(),
        )
        task_widget.grid(sticky="ew")

        self.content_box.delete(1.0, END)

    def load_tasks(self) -> dict[int, Task]:
        if not Path(self.TASKS_FILE).exists():
            return {}
        with Path(self.TASKS_FILE).open() as file:
            return self.ta.validate_json(file.read())

    def save_tasks(self) -> None:
        with Path(self.TASKS_FILE).open("w") as file:
            file.buffer.write(self.ta.dump_json(self.tasks, indent=2))


def init_root() -> Tk:
    root = Tk(className="app.todo.some1rxndom")
    root.title("todo list app")
    root.geometry("1200x1400")

    return root


def main() -> None:
    app = App(init_root())
    app.construct()

    app.mainloop()


if __name__ == "__main__":
    main()
