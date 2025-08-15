import argparse
from todo import ToDoManager
from commands import register_subcommands
from utils import print_error

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="todo", description="Simple in-memory ToDo CLI")
    return p

def main():
    manager = ToDoManager()
    parser = build_parser()
    register_subcommands(parser, manager)
    args = parser.parse_args()
    try:
        args.run(args)  # each subcommand sets a `run` lambda
    except (KeyError, ValueError) as e:
        print_error(e)

if __name__ == "__main__":
    main()
