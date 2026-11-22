"""Entry point of the learning tool.

    python3 tools/course.py            where am I, what is next
    python3 tools/course.py check 1.6a
    python3 tools/course.py -h

The workspace root is the parent of the folder this file lives in, so the tool
works from any current directory and keeps working when the workspace is moved.
Standard library only; Python 3.9 or newer.

All logic lives in the ``courselib`` package next to this file.
"""

import os
import sys

MINIMUM = (3, 9)


def _too_old():
    wanted = f"{MINIMUM[0]}.{MINIMUM[1]}"
    found = f"{sys.version_info[0]}.{sys.version_info[1]}"
    sys.stderr.write(
        f"这个工具需要 Python {wanted} 或更新的版本，现在运行它的是 Python {found}。\n"
        "请用 python3 运行：python3 tools/course.py\n"
    )
    return 2


def _run():
    # Keep the workspace clean: no __pycache__ folders next to the tool or the lessons.
    sys.dont_write_bytecode = True
    tools = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    if tools not in sys.path:
        sys.path.insert(0, tools)
    from courselib.cli import main
    code = main(sys.argv[1:], root=os.path.dirname(tools))
    try:
        sys.stdout.flush()
    except BrokenPipeError:
        # The reader went away (for example "| head"); do not complain about it.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return code


def _main():
    if sys.version_info < MINIMUM:
        return _too_old()
    try:
        return _run()
    except KeyboardInterrupt:
        # Ctrl+C before the tool was ready to handle it (for example while loading).
        try:
            sys.stdout.write("\n已停止。需要时重新运行同一条命令就行。\n")
            sys.stdout.flush()
        except (OSError, ValueError):
            pass
        return 1


if __name__ == "__main__":
    sys.exit(_main())
