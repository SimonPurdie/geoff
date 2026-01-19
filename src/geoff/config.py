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
    max_iterations: int = 0
    max_stuck: int = 2
