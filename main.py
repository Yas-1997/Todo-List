import argparse
from pathlib import Path
from todo import ToDoManager

DEFAULT_DATA_PATH = Path.home() / ".todo_cli" / "tasks.json"

manager = ToDoManager()

def cmd_add(args):
    t = manager.add_task(args.title)
    print(f"Added: {t}")

def cmd_list(args):
    items = manager.list_tasks(show_done=not args.pending)
    if not items:
        print("No tasks.")
        return
    for t in items:
        print(repr(t))

def cmd_done(args):
    t = manager.complete_task(args.id, done=True)
    print(f"Marked done: {t}")

def cmd_undone(args):
    t = manager.complete_task(args.id, done=False)
    print(f"Marked undone: {t}")

def cmd_delete(args):
    t = manager.delete_task(args.id)
    print(f"Deleted: {t}")

def cmd_clear(args):
    n = manager.clear_completed()
    print(f"Removed {n} completed task(s).")

def cmd_search(args):
    items = manager.search(args.query, show_done=None if args.all else False)
    if not items:
        print("No matches.")
        return
    for t in items:
        print(repr(t))

def cmd_rename(args):
    t = manager.rename_task(args.id, args.title)
    print(f"Renamed: {t}")

def cmd_stats(args):
    s = manager.stats()
    print(f"Total: {s['total']} | Done: {s['done']} | Pending: {s['pending']}")

def cmd_reorder(args):
    try:
        ids = [int(x) for x in args.ids.split(",") if x.strip().isdigit()]
    except Exception:
        raise ValueError("Provide ids as comma-separated integers, e.g. 3,1,2")
    manager.reorder(ids)
    print("Order updated.")
    cmd_list(argparse.Namespace(pending=False))

def build_parser():
    p = argparse.ArgumentParser(prog="todo", description="JSON-persistent ToDo CLI")
    p.add_argument(
        "--data-path",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Path to JSON data file (default: {DEFAULT_DATA_PATH})",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("add", help="Add a new task")
    sp.add_argument("title", type=str)
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("list", help="List tasks")
    sp.add_argument("--pending", action="store_true", help="Show only pending tasks")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("done", help="Mark a task as done")
    sp.add_argument("id", type=int)
    sp.set_defaults(func=cmd_done)

    sp = sub.add_parser("undone", help="Mark a task as not done")
    sp.add_argument("id", type=int)
    sp.set_defaults(func=cmd_undone)

    sp = sub.add_parser("delete", help="Delete a task")
    sp.add_argument("id", type=int)
    sp.set_defaults(func=cmd_delete)

    sp = sub.add_parser("clear", help="Delete all completed tasks")
    sp.set_defaults(func=cmd_clear)

    sp = sub.add_parser("search", help="Search task titles")
    sp.add_argument("query", type=str)
    sp.add_argument("--all", action="store_true", help="Search across all tasks (not only pending)")
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("rename", help="Rename a task")
    sp.add_argument("id", type=int)
    sp.add_argument("title", type=str)
    sp.set_defaults(func=cmd_rename)

    sp = sub.add_parser("stats", help="Show stats")
    sp.set_defaults(func=cmd_stats)

    sp = sub.add_parser("reorder", help="Reorder by comma-separated ids, e.g. 3,1,2")
    sp.add_argument("ids", type=str)
    sp.set_defaults(func=cmd_reorder)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()

    # 1) LOAD
    data_path: Path = args.data_path
    manager.load_from_file(data_path)

    try:
        # 2) RUN COMMAND
        args.func(args)
    except (KeyError, ValueError) as e:
        print(f"Error: {e}")
    finally:
        # 3) SAVE (after every run; safe and simple)
        try:
            manager.save_to_file(data_path)
        except Exception as e:
            print(f"Warning: could not save data: {e}")

if __name__ == "__main__":
    main()
