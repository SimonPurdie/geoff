import sys
from geoff.app import GeoffApp
from geoff.executor import execute_opencode_once, execute_opencode_loop


def main():
    app = GeoffApp()
    result = app.run()

    if result:
        action, *args = result
        if action == "run_once":
            prompt = args[0]
            model = args[1] if len(args) > 1 else None
            execute_opencode_once(prompt, model=model)
        elif action == "run_loop":
            prompt = args[0]
            model = args[1] if len(args) > 1 else None
            max_iterations = args[2] if len(args) > 2 else 0
            max_stuck = args[3] if len(args) > 3 else 2
            max_frozen = args[4] if len(args) > 4 else 0
            execute_opencode_loop(
                prompt,
                max_iterations=max_iterations,
                max_stuck=max_stuck,
                max_frozen=max_frozen,
                model=model,
            )


if __name__ == "__main__":
    main()
