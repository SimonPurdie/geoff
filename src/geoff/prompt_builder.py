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
                config.prompt_tasklist_study.format(
                    tasklist=config.tasklist_file.strip()
                )
            )
    elif config.task_mode == "oneoff":
        if config.oneoff_prompt.strip():
            lines.append(config.oneoff_prompt.strip())

    # 3. Backpressure
    if config.backpressure_enabled:
        lines.append(config.prompt_backpressure_header)
        for line in config.prompt_backpressure_lines:
            lines.append(line)

    # 4. Breadcrumb Instruction
    if config.breadcrumb_enabled and config.breadcrumbs_file.strip():
        lines.append(
            config.prompt_breadcrumb_instruction.format(
                breadcrumbs=config.breadcrumbs_file.strip()
            )
        )

    # 5. Task Update
    if config.task_mode == "tasklist" and config.tasklist_file.strip():
        lines.append(
            config.prompt_tasklist_update.format(tasklist=config.tasklist_file.strip())
        )

    return "\n".join(lines)
