from geoff.config import PromptConfig


def build_prompt(config: PromptConfig) -> str:
    lines = []

    # 1. Orientation / Study Docs
    for doc in config.study_docs:
        if doc and doc.strip():
            lines.append(f"study {doc.strip()}")

    # Breadcrumbs check line
    if config.breadcrumb_enabled and config.breadcrumbs_file.strip():
        lines.append(f"check {config.breadcrumbs_file.strip()}")

    # 2. Task Source
    if config.task_mode == "tasklist":
        if config.tasklist_file.strip():
            lines.append(
                f"study {config.tasklist_file.strip()} and pick the most important thing to do."
            )
    elif config.task_mode == "oneoff":
        if config.oneoff_prompt.strip():
            lines.append(config.oneoff_prompt.strip())

    # 3. Backpressure
    if config.backpressure_enabled:
        lines.append("IMPORTANT:")
        lines.append("- author property based tests or unit tests (whichever is best)")
        lines.append("- after performing your task run the tests")
        lines.append("- when tests pass, commit to deploy changes")

    # 4. Breadcrumb Instruction
    if config.breadcrumb_enabled and config.breadcrumbs_file.strip():
        lines.append(
            f"if you ran into difficulties due to a lack of information about the project or environment, which you then resolved, leave a note about it in {config.breadcrumbs_file.strip()} to help future agents."
        )

    # 5. Task Update
    if config.task_mode == "tasklist" and config.tasklist_file.strip():
        lines.append(f"update {config.tasklist_file.strip()} when the task is done")

    return "\n".join(lines)
