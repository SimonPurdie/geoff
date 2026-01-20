import sys
from geoff.app import GeoffApp
from geoff.executor import execute_opencode_once, execute_opencode_loop


def main():
    app = GeoffApp()
    result = app.run()

    if result:
        action, *args = result
        if action == "run_once":
            execute_opencode_once(*args)
        elif action == "run_loop":
            execute_opencode_loop(*args)


if __name__ == "__main__":
    main()
