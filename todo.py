from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Iterable
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        status = "✓" if self.done else "•"
        ts = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{status}] #{self.id} {self.title}  ({ts})"


class ToDoManager:
    """Simple in-memory ToDo manager."""
    def __init__(self) -> None:
        self._tasks: List[Task] = []
        self._next_id: int = 1

    # Create
    def add_task(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        task = Task(id=self._next_id, title=title)
        self._tasks.append(task)
        self._next_id += 1
        return task

    # Read
    def list_tasks(self, show_done: bool = True) -> List[Task]:
        if show_done:
            return list(self._tasks)
        return [t for t in self._tasks if not t.done]

    def get(self, task_id: int) -> Task:
        task = next((t for t in self._tasks if t.id == task_id), None)
        if task is None:
            raise KeyError(f"No task with id {task_id}.")
        return task

    def search(self, query: str, show_done: Optional[bool] = None) -> List[Task]:
        q = query.strip().lower()
        items = self._tasks
        if show_done is not None:
            items = [t for t in items if t.done == show_done]
        return [t for t in items if q in t.title.lower()]

    # Update
    def complete_task(self, task_id: int, done: bool = True) -> Task:
        task = self.get(task_id)
        task.done = done
        return task

    def rename_task(self, task_id: int, new_title: str) -> Task:
        new_title = new_title.strip()
        if not new_title:
            raise ValueError("New title cannot be empty.")
        task = self.get(task_id)
        task.title = new_title
        return task

    def reorder(self, ids_in_order: Iterable[int]) -> None:
        id_to_task = {t.id: t for t in self._tasks}
        new_order: List[Task] = []
        seen = set()
        for i in ids_in_order:
            if i in id_to_task and i not in seen:
                new_order.append(id_to_task[i])
                seen.add(i)
        for t in self._tasks:
            if t.id not in seen:
                new_order.append(t)
        self._tasks = new_order

    # Delete
    def delete_task(self, task_id: int) -> Task:
        task = self.get(task_id)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        return task

    def clear_completed(self) -> int:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if not t.done]
        return before - len(self._tasks)

    # Stats
    def stats(self) -> dict:
        total = len(self._tasks)
        done = sum(1 for t in self._tasks if t.done)
        return {"total": total, "done": done, "pending": total - done}
