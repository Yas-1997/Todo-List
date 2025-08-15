from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Iterable, Dict, Any
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        status = "-" if self.done else "•"
        ts = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{status}] #{self.id} {self.title}  ({ts})"

    # ---helpers ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "created_at": self.created_at.isoformat(timespec="seconds"),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
        created = d.get("created_at")
        try:
            dt = datetime.fromisoformat(created) if created else datetime.now()
        except Exception:
            dt = datetime.now()
        return Task(
            id=int(d["id"]),
            title=str(d["title"]),
            done=bool(d.get("done", False)),
            created_at=dt,
        )


class ToDoManager:
    def __init__(self) -> None:
        self._tasks: List[Task] = []
        self._next_id: int = 1

    # ---------- Create ----------
    def add_task(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        task = Task(id=self._next_id, title=title)
        self._tasks.append(task)
        self._next_id += 1
        return task

    # ---------- Read ----------
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

    # ---------- Update ----------
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

    # ---------- Delete ----------
    def delete_task(self, task_id: int) -> Task:
        task = self.get(task_id)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        return task

    def clear_completed(self) -> int:
        before = len(self._tasks)
        self._tasks = [t for t in self._tasks if not t.done]
        return before - len(self._tasks)

    # ---------- Stats ----------
    def stats(self) -> dict:
        total = len(self._tasks)
        done = sum(1 for t in self._tasks if t.done)
        return {"total": total, "done": done, "pending": total - done}

    # ---------- Persistence ----------
    def _to_store(self) -> Dict[str, Any]:
        return {
            "next_id": self._next_id,
            "tasks": [t.to_dict() for t in self._tasks],
        }

    def _from_store(self, store: Dict[str, Any]) -> None:
        self._next_id = int(store.get("next_id", 1))
        raw_tasks = store.get("tasks", [])
        self._tasks = [Task.from_dict(rt) for rt in raw_tasks]

    def load_from_file(self, path: "Path") -> None:
        """Load tasks from JSON file if it exists; otherwise start fresh."""
        try:
            if not path.exists():
                self._tasks = []
                self._next_id = 1
                return
            import json
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Invalid data format.")
            self._from_store(data)
        except Exception:
            # Corrupt/invalid file: start fresh
            self._tasks = []
            self._next_id = 1

    def save_to_file(self, path: "Path") -> None:
        """Atomically write current state to JSON file."""
        import json
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        data = self._to_store()
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        # Atomic-ish replace
        tmp.replace(path)
