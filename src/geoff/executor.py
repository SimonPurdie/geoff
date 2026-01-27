import subprocess
import sys
import time
import hashlib
import os
from pathlib import Path
from typing import Optional


def compute_repo_hash(exec_dir: Optional[Path] = None) -> str:
    """Compute a hash of the repository state for change detection.

    Uses git rev-parse HEAD if in a git repo, otherwise falls back to
    hashing the directory contents.
    """
    cwd = exec_dir or Path.cwd()

    try:
        # Check if we are in a git repository
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )

        # Get HEAD commit hash
        head_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        head_hash = head_result.stdout.strip()

        # Get working tree status (staged, unstaged, untracked)
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        status = status_result.stdout

        combined = f"{head_hash}\n{status}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    hash_input = []
    for root, dirs, files in os.walk(cwd):
        dirs.sort()
        for f in sorted(files):
            fpath = Path(root) / f
            relpath = fpath.relative_to(cwd)
            try:
                mtime = fpath.stat().st_mtime
                size = fpath.stat().st_size
                hash_input.append(f"{relpath}:{mtime}:{size}")
            except OSError:
                pass

    combined = "\n".join(hash_input)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def execute_opencode_once(prompt: str, exec_dir: Optional[Path] = None) -> None:
    """Execute Opencode once with the given prompt.

    Exits the TUI cleanly and runs the prompt through Opencode.

    Args:
        prompt: The assembled prompt to execute
        exec_dir: Directory to execute in (defaults to current working directory)
    """
    cwd = exec_dir or Path.cwd()

    cmd = ["opencode", "run", prompt, "--log-level", "INFO"]

    try:
        subprocess.run(cmd, cwd=cwd, check=False)
    except KeyboardInterrupt:
        pass
    except FileNotFoundError:
        print(
            "Error: 'opencode' command not found. Ensure Opencode is installed.",
            file=sys.stderr,
        )
        sys.exit(1)


def execute_opencode_loop(
    prompt: str,
    max_iterations: int = 0,
    max_stuck: int = 2,
    exec_dir: Optional[Path] = None,
) -> None:
    """Execute Opencode in a loop with change detection.

    Runs Opencode repeatedly until user cancels, max iterations reached,
    or repo becomes stuck (no changes detected for max_stuck iterations).

    Args:
        prompt: The assembled prompt to execute
        max_iterations: 0 for no limit, otherwise max iterations to run
        max_stuck: Consecutive iterations with no changes before breaking
        exec_dir: Directory to execute in (defaults to current working directory)
    """
    cwd = exec_dir or Path.cwd()

    stuck_count = 0
    iteration = 0
    has_changes = True

    print(
        f"Starting loop execution (max_iterations={max_iterations}, max_stuck={max_stuck})"
    )

    try:
        while True:
            iteration += 1

            prev_hash = compute_repo_hash(cwd)

            print(f"\n--- Iteration {iteration} ---")

            cmd = ["opencode", "run", prompt, "--log-level", "INFO"]

            result = subprocess.run(cmd, cwd=cwd, check=False)

            curr_hash = compute_repo_hash(cwd)

            if curr_hash == prev_hash:
                stuck_count += 1
                print(f"No changes detected (stuck: {stuck_count}/{max_stuck})")
            else:
                stuck_count = 0
                print("Changes detected")

            if max_iterations > 0 and iteration >= max_iterations:
                print(f"Reached max iterations ({max_iterations})")
                break

            if stuck_count >= max_stuck:
                print(f"Repo stuck for {stuck_count} consecutive iterations")
                break

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nLoop cancelled by user")
    except FileNotFoundError:
        print(
            "Error: 'opencode' command not found. Ensure Opencode is installed.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"\nLoop terminated after {iteration} iteration(s)")
