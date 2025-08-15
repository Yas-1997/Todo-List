from typing import Iterable
from todo import Task

def print_tasks(tasks: Iterable[Task]) -> None:
    items = list(tasks)
    if not items:
        print("No tasks.")
        return
    for t in items:
        print(repr(t))

def print_error(err: Exception) -> None:
    print(f"Error: {err}")

def ensure_positive_int(value: int, name: str = "id") -> int:
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return value
