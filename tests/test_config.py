from geoff.config import PromptConfig


def test_config_defaults():
    config = PromptConfig()
    assert config.study_docs == ["docs/SPEC.md"]
    assert config.model == "default"
    assert config.breadcrumbs_file == "docs/BREADCRUMBS.md"
    assert config.task_mode == "tasklist"
    assert config.tasklist_file == "docs/PLAN.md"
    assert config.oneoff_prompt == ""
    assert config.backpressure_enabled is True
    assert config.breadcrumb_enabled is True
    assert config.max_iterations == 0
    assert config.max_stuck == 2
    assert config.max_frozen == 0


def test_config_custom_values():
    config = PromptConfig(
        study_docs=["docs/OTHER.md"],
        model="openai/gpt-4o",
        task_mode="oneoff",
        max_iterations=5,
    )
    assert config.study_docs == ["docs/OTHER.md"]
    assert config.model == "openai/gpt-4o"
    assert config.task_mode == "oneoff"
    assert config.max_iterations == 5
    # Check default persisted
    assert config.backpressure_enabled is True
