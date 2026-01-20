from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class PromptConfig:
    study_docs: List[str] = field(default_factory=lambda: ["docs/SPEC.md"])
    breadcrumbs_file: str = "docs/BREADCRUMBS.md"
    task_mode: Literal["tasklist", "oneoff"] = "tasklist"
    tasklist_file: str = "docs/PLAN.md"
    oneoff_prompt: str = ""
    backpressure_enabled: bool = True
    breadcrumb_enabled: bool = True
    theme: str = "textual-dark"
    max_iterations: int = 0
    max_stuck: int = 2
    prompt_tasklist_study: str = (
        "study {tasklist} and pick the most important thing to do."
    )
    prompt_tasklist_update: str = "update {tasklist} when the task is done"
    prompt_backpressure_header: str = "IMPORTANT:"
    prompt_backpressure_lines: List[str] = field(
        default_factory=lambda: [
            "- author property based tests or unit tests (whichever is best)",
            "- after performing your task run the tests",
            "- when tests pass, commit to deploy changes",
        ]
    )
    prompt_breadcrumb_instruction: str = "if you ran into difficulties due to a lack of information about the project or environment, which you then resolved, leave a note about it in {breadcrumbs} to help future agents."
