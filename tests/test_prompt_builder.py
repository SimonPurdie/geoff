from geoff.config import PromptConfig
from geoff.prompt_builder import build_prompt


def test_build_prompt_defaults():
    config = PromptConfig()
    prompt = build_prompt(config)

    expected_lines = [
        "study docs/SPEC.md",
        "check docs/BREADCRUMBS.md",
        "study docs/PLAN.md and pick the most important thing to do.",
        "IMPORTANT:",
        "- author property based tests or unit tests (whichever is best)",
        "- after performing your task run the tests",
        "- when tests pass, commit to deploy changes",
        "if you ran into difficulties due to a lack of information about the project or environment, which you then resolved, leave a note about it in docs/BREADCRUMBS.md to help future agents.",
        "update docs/PLAN.md when the task is done",
    ]

    assert prompt == "\n".join(expected_lines)


def test_build_prompt_oneoff():
    config = PromptConfig(
        task_mode="oneoff",
        oneoff_prompt="Do something cool.\n  And fast.",
    )
    prompt = build_prompt(config)

    assert "study docs/PLAN.md" not in prompt
    assert "update docs/PLAN.md" not in prompt
    assert "Do something cool.\n  And fast." in prompt
    assert "IMPORTANT:" in prompt  # Backpressure enabled by default


def test_build_prompt_disabled_features():
    config = PromptConfig(backpressure_enabled=False, breadcrumb_enabled=False)
    prompt = build_prompt(config)

    assert "IMPORTANT:" not in prompt
    assert "check docs/BREADCRUMBS.md" not in prompt
    assert "if you ran into difficulties" not in prompt


def test_build_prompt_multiple_docs():
    config = PromptConfig(study_docs=["doc1.md", "doc2.md"])
    prompt = build_prompt(config)

    assert "study doc1.md" in prompt
    assert "study doc2.md" in prompt
    # Check order
    lines = prompt.splitlines()
    assert lines[0] == "study doc1.md"
    assert lines[1] == "study doc2.md"


def test_build_prompt_empty_paths():
    config = PromptConfig(study_docs=[], breadcrumbs_file="", tasklist_file="")
    prompt = build_prompt(config)

    assert "study" not in prompt  # No docs, no tasklist
    assert "check" not in prompt  # No breadcrumbs
    assert "update" not in prompt  # No tasklist


def test_custom_backpressure_strings():
    config = PromptConfig(
        backpressure_enabled=True,
        prompt_backpressure_header="CRITICAL:",
        prompt_backpressure_lines=[
            "- write more tests",
            "- verify your changes",
        ],
    )
    prompt = build_prompt(config)

    assert "CRITICAL:" in prompt
    assert "- write more tests" in prompt
    assert "- verify your changes" in prompt
    assert "IMPORTANT:" not in prompt
    assert "author property based tests" not in prompt


def test_custom_tasklist_study_string():
    config = PromptConfig(
        task_mode="tasklist",
        tasklist_file="tasks.txt",
        prompt_tasklist_study="examine {tasklist} and select priority.",
    )
    prompt = build_prompt(config)

    assert "examine tasks.txt and select priority." in prompt
    assert "pick the most important thing to do" not in prompt


def test_custom_tasklist_update_string():
    config = PromptConfig(
        task_mode="tasklist",
        tasklist_file="tasks.txt",
        prompt_tasklist_update="mark completion in {tasklist}",
    )
    prompt = build_prompt(config)

    assert "mark completion in tasks.txt" in prompt
    assert "update tasks.txt when the task is done" not in prompt


def test_custom_breadcrumb_instruction_string():
    config = PromptConfig(
        breadcrumb_enabled=True,
        breadcrumbs_file="notes.log",
        prompt_breadcrumb_instruction="if you had to figure something out, log it in {breadcrumbs}.",
    )
    prompt = build_prompt(config)

    assert "check notes.log" in prompt
    assert "if you had to figure something out, log it in notes.log." in prompt
    assert "if you ran into difficulties" not in prompt


def test_all_custom_prompt_strings():
    config = PromptConfig(
        task_mode="tasklist",
        tasklist_file="work.md",
        breadcrumbs_file="journal.md",
        prompt_tasklist_study="look at {tasklist} and decide what matters.",
        prompt_tasklist_update="record progress in {tasklist}",
        prompt_backpressure_header="NOTE:",
        prompt_backpressure_lines=[
            "- test thoroughly",
            "- commit early and often",
        ],
        prompt_breadcrumb_instruction="document discoveries in {breadcrumbs}.",
    )
    prompt = build_prompt(config)

    assert "look at work.md and decide what matters." in prompt
    assert "record progress in work.md" in prompt
    assert "NOTE:" in prompt
    assert "- test thoroughly" in prompt
    assert "- commit early and often" in prompt
    assert "document discoveries in journal.md." in prompt


def test_custom_empty_backpressure_lines():
    config = PromptConfig(
        backpressure_enabled=True,
        prompt_backpressure_lines=[],
    )
    prompt = build_prompt(config)

    assert "IMPORTANT:" in prompt
    lines = prompt.splitlines()
    assert "IMPORTANT:" in lines
    backpressure_idx = lines.index("IMPORTANT:")
    assert backpressure_idx < len(lines) - 1
