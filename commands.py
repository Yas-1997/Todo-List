import argparse
from todo import ToDoManager
from utils import print_tasks, print_error, ensure_positive_int

# ---- Handlers (called by argparse) ----

def cmd_add(manager: ToDoManager, args: argparse.Namespace) -> None:
    t = manager.add_task(args.title)
    print(f"Added: {t}")

def cmd_list(manager: ToDoManager, args: argparse.Namespace) -> None:
    items = manager.list_tasks(show_done=not args.pending)
    print_tasks(items)

def cmd_done(manager: ToDoManager, args: argparse.Namespace) -> None:
    ensure_positive_int(args.id)
    t = manager.complete_task(args.id, done=True)
    print(f"Marked done: {t}")

def cmd_undone(manager: ToDoManager, args: argparse.Namespace) -> None:
    ensure_positive_int(args.id)
    t = manager.complete_task(args.id, done=False)
    print(f"Marked undone: {t}")

def cmd_delete(manager: ToDoManager, args: argparse.Namespace) -> None:
    ensure_positive_int(args.id)
    t = manager.delete_task(args.id)
    print(f"Deleted: {t}")

def cmd_clear(manager: ToDoManager, args: argparse.Namespace) -> None:
    n = manager.clear_completed()
    print(f"Removed {n} completed task(s).")

def cmd_search(manager: ToDoManager, args: argparse.Namespace) -> None:
    items = manager.search(args.query, show_done=None if args.all else False)
    print_tasks(items)

def cmd_rename(manager: ToDoManager, args: argparse.Namespace) -> None:
    ensure_positive_int(args.id)
    t = manager.rename_task(args.id, args.title)
    print(f"Renamed: {t}")

def cmd_stats(manager: ToDoManager, args: argparse.Namespace) -> None:
    s = manager.stats()
    print(f"Total: {s['total']} | Done: {s['done']} | Pending: {s['pending']}")

def cmd_reorder(manager: ToDoManager, args: argparse.Namespace) -> None:
    try:
        ids = [int(x) for x in args.ids.split(",") if x.strip().isdigit()]
    except Exception:
        raise ValueError("Provide ids as comma-separated integers, e.g. 3,1,2")
    manager.reorder(ids)
    print("Order updated.")
    cmd_list(manager, argparse.Namespace(pending=False))


# ---- Wiring to argparse ----

def register_subcommands(parser: argparse.ArgumentParser, manager: ToDoManager) -> None:
    sub = parser.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("add", help="Add a new task")
    sp.add_argument("title", type=str)
    sp.set_defaults(run=lambda a: cmd_add(manager, a))

    sp = sub.add_parser("list", help="List tasks")
    sp.add_argument("--pending", action="store_true", help="Show only pending tasks")
    sp.set_defaults(run=lambda a: cmd_list(manager, a))

    sp = sub.add_parser("done", help="Mark a task as done")
    sp.add_argument("id", type=int)
    sp.set_defaults(run=lambda a: cmd_done(manager, a))

    sp = sub.add_parser("undone", help="Mark a task as not done")
    sp.add_argument("id", type=int)
    sp.set_defaults(run=lambda a: cmd_undone(manager, a))

    sp = sub.add_parser("delete", help="Delete a task")
    sp.add_argument("id", type=int)
    sp.set_defaults(run=lambda a: cmd_delete(manager, a))

    sp = sub.add_parser("clear", help="Delete all completed tasks")
    sp.set_defaults(run=lambda a: cmd_clear(manager, a))

    sp = sub.add_parser("search", help="Search in task titles")
    sp.add_argument("query", type=str)
    sp.add_argument("--all", action="store_true", help="Search across all tasks (not only pending)")
    sp.set_defaults(run=lambda a: cmd_search(manager, a))

    sp = sub.add_parser("rename", help="Rename a task")
    sp.add_argument("id", type=int)
    sp.add_argument("title", type=str)
    sp.set_defaults(run=lambda a: cmd_rename(manager, a))

    sp = sub.add_parser("stats", help="Show stats")
    sp.set_defaults(run=lambda a: cmd_stats(manager, a))

    sp = sub.add_parser("reorder", help="Reorder by comma-separated ids, e.g. 3,1,2")
    sp.add_argument("ids", type=str)
    sp.set_defaults(run=lambda a: cmd_reorder(manager, a))
