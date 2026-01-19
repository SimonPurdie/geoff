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
        # Defaults for others
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
