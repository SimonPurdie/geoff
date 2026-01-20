from pathlib import Path
from geoff.config_manager import ConfigManager, BASE_PROMPT_STRING_KEYS
from geoff.config import PromptConfig
from geoff.config_io import load_yaml, save_yaml
from hypothesis import given, settings, HealthCheck
from hypothesis.strategies import lists, text


def test_resolve_defaults(tmp_path):
    # Point paths to non-existent locations
    cm = ConfigManager(working_dir=tmp_path)
    cm.global_config_path = tmp_path / "global.yaml"

    config = cm.resolve_config()
    assert config == PromptConfig()


def test_resolve_global_override(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    # Save global config
    save_yaml(global_path, {"max_iterations": 10})

    config = cm.resolve_config()
    assert config.max_iterations == 10
    assert config.task_mode == "tasklist"  # default remains


def test_resolve_repo_override(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    # global non-existent
    cm.global_config_path = tmp_path / "global.yaml"

    # repo config
    repo_path = tmp_path / ".geoff" / "geoff.yaml"
    save_yaml(repo_path, {"max_iterations": 5})

    config = cm.resolve_config()
    assert config.max_iterations == 5


def test_resolve_precedence(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    repo_path = tmp_path / ".geoff" / "geoff.yaml"

    save_yaml(global_path, {"max_iterations": 10, "task_mode": "oneoff"})
    save_yaml(repo_path, {"max_iterations": 5})  # Should override global

    config = cm.resolve_config()
    assert config.max_iterations == 5
    assert config.task_mode == "oneoff"  # Inherited from global


def test_save_repo_config(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    config = PromptConfig(max_iterations=99)

    cm.save_repo_config(config)

    repo_path = tmp_path / ".geoff" / "geoff.yaml"
    assert repo_path.exists()

    # Verify we can load it back
    loaded_config = cm.resolve_config()
    assert loaded_config.max_iterations == 99


def test_base_prompt_strings_precedence_user_over_repo(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    repo_path = tmp_path / ".geoff" / "geoff.yaml"

    user_custom = "user custom study prompt"
    repo_custom = "repo custom study prompt"

    save_yaml(global_path, {"prompt_tasklist_study": user_custom})
    save_yaml(repo_path, {"prompt_tasklist_study": repo_custom})

    config = cm.resolve_config()

    assert config.prompt_tasklist_study == user_custom


def test_base_prompt_strings_lines_precedence_user_over_repo(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    repo_path = tmp_path / ".geoff" / "geoff.yaml"

    user_custom_lines = ["- user line 1", "- user line 2"]
    repo_custom_lines = ["- repo line 1", "- repo line 2", "- repo line 3"]

    save_yaml(global_path, {"prompt_backpressure_lines": user_custom_lines})
    save_yaml(repo_path, {"prompt_backpressure_lines": repo_custom_lines})

    config = cm.resolve_config()

    assert config.prompt_backpressure_lines == user_custom_lines


def test_base_prompt_strings_precedence_user_over_default(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    user_custom = "user custom header"

    save_yaml(global_path, {"prompt_backpressure_header": user_custom})

    config = cm.resolve_config()

    assert config.prompt_backpressure_header == user_custom


def test_base_prompt_strings_lines_loaded_from_global(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    user_custom_lines = [
        "- first custom line",
        "- second custom line",
        "- third custom line",
    ]

    save_yaml(global_path, {"prompt_backpressure_lines": user_custom_lines})

    config = cm.resolve_config()

    assert config.prompt_backpressure_lines == user_custom_lines


def test_base_prompt_strings_materialize_default_when_no_user_no_repo(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    assert not global_path.exists()

    config = cm.resolve_config()

    assert config.prompt_tasklist_study == PromptConfig().prompt_tasklist_study
    assert global_path.exists()

    loaded = load_yaml(global_path)
    assert loaded is not None
    assert "prompt_tasklist_study" in loaded


def test_base_prompt_strings_materialize_repo_when_no_user(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    repo_path = tmp_path / ".geoff" / "geoff.yaml"
    repo_custom = "repo custom breadcrumb instruction"
    save_yaml(repo_path, {"prompt_breadcrumb_instruction": repo_custom})

    assert not global_path.exists()

    config = cm.resolve_config()

    assert config.prompt_breadcrumb_instruction == repo_custom
    assert global_path.exists()

    loaded = load_yaml(global_path)
    assert loaded is not None
    assert loaded.get("prompt_breadcrumb_instruction") == repo_custom


def test_base_prompt_strings_no_materialize_when_user_exists(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    user_custom = "user custom header"
    user_custom_update = "user custom update"
    save_yaml(
        global_path,
        {
            "prompt_backpressure_header": user_custom,
            "prompt_tasklist_update": user_custom_update,
        },
    )

    repo_path = tmp_path / ".geoff" / "geoff.yaml"
    repo_custom_header = "repo custom header"
    save_yaml(repo_path, {"prompt_backpressure_header": repo_custom_header})

    config = cm.resolve_config()

    assert config.prompt_backpressure_header == user_custom
    assert config.prompt_tasklist_update == user_custom_update

    loaded = load_yaml(global_path)
    assert loaded is not None
    assert loaded.get("prompt_backpressure_header") == user_custom
    assert loaded.get("prompt_tasklist_update") == user_custom_update


def test_base_prompt_strings_all_keys_materialized(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    assert not global_path.exists()

    config = cm.resolve_config()

    loaded = load_yaml(global_path)
    assert loaded is not None

    for key in BASE_PROMPT_STRING_KEYS:
        assert key in loaded, f"{key} should be materialized in user config"
        assert loaded[key] == getattr(config, key)


def test_save_repo_config_excludes_base_prompt_strings(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    config = PromptConfig(
        max_iterations=99,
        prompt_tasklist_study="custom study",
        prompt_backpressure_header="custom header",
    )

    cm.save_repo_config(config)

    repo_path = tmp_path / ".geoff" / "geoff.yaml"
    assert repo_path.exists()

    loaded = load_yaml(repo_path)
    assert loaded is not None
    assert loaded.get("max_iterations") == 99
    assert "prompt_tasklist_study" not in loaded
    assert "prompt_backpressure_header" not in loaded


def test_base_prompt_strings_preserves_existing_non_base_keys(tmp_path):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    save_yaml(global_path, {"max_iterations": 42, "task_mode": "oneoff"})

    config = cm.resolve_config()

    loaded = load_yaml(global_path)
    assert loaded is not None
    assert loaded.get("max_iterations") == 42
    assert loaded.get("task_mode") == "oneoff"


@given(
    prompt_backpressure_lines=lists(
        text(min_size=5, max_size=50), min_size=1, max_size=5
    ),
)
@settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_base_prompt_strings_lines_loaded_from_global_property(
    tmp_path, prompt_backpressure_lines
):
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    save_yaml(global_path, {"prompt_backpressure_lines": prompt_backpressure_lines})

    config = cm.resolve_config()

    assert config.prompt_backpressure_lines == prompt_backpressure_lines


def test_oneoff_prompt_preserved_in_global_config(tmp_path):
    """Test that oneoff_prompt set by user in global config is preserved."""
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    user_oneoff_prompt = "This is my custom one-off prompt"
    save_yaml(
        global_path,
        {
            "task_mode": "oneoff",
            "oneoff_prompt": user_oneoff_prompt,
        },
    )

    config = cm.resolve_config()

    assert config.task_mode == "oneoff"
    assert config.oneoff_prompt == user_oneoff_prompt

    loaded = load_yaml(global_path)
    assert loaded.get("oneoff_prompt") == user_oneoff_prompt
    assert loaded.get("task_mode") == "oneoff"


def test_non_base_keys_preserved_during_materialization(tmp_path):
    """Test that non-base keys in global config are preserved when materializing defaults."""
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    save_yaml(
        global_path,
        {
            "max_iterations": 42,
            "task_mode": "oneoff",
            "oneoff_prompt": "my custom prompt",
        },
    )

    config = cm.resolve_config()

    assert config.max_iterations == 42
    assert config.oneoff_prompt == "my custom prompt"

    loaded = load_yaml(global_path)
    assert loaded.get("max_iterations") == 42
    assert loaded.get("oneoff_prompt") == "my custom prompt"
    assert loaded.get("task_mode") == "oneoff"


def test_resolve_config_with_empty_repo_preserves_global(tmp_path):
    """Test that global config values are preserved when repo config is empty/deleted."""
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    save_yaml(
        global_path,
        {
            "task_mode": "oneoff",
            "oneoff_prompt": "User's custom oneoff prompt",
            "max_iterations": 100,
        },
    )

    config = cm.resolve_config()

    assert config.task_mode == "oneoff"
    assert config.oneoff_prompt == "User's custom oneoff prompt"
    assert config.max_iterations == 100


def test_multiple_resolve_config_calls_preserve_global(tmp_path):
    """Test that multiple calls to resolve_config don't corrupt global config."""
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    save_yaml(
        global_path,
        {
            "task_mode": "oneoff",
            "oneoff_prompt": "My persistent prompt",
        },
    )

    for _ in range(5):
        config = cm.resolve_config()
        assert config.oneoff_prompt == "My persistent prompt"

    loaded = load_yaml(global_path)
    assert loaded.get("oneoff_prompt") == "My persistent prompt"
    assert loaded.get("task_mode") == "oneoff"


def test_reset_scenario_with_global_oneoff_prompt(tmp_path):
    """Test the reset scenario: repo deleted, global has oneoff_prompt."""
    cm = ConfigManager(working_dir=tmp_path)
    global_path = tmp_path / "global.yaml"
    cm.global_config_path = global_path

    repo_path = tmp_path / ".geoff" / "geoff.yaml"

    save_yaml(
        global_path,
        {
            "task_mode": "oneoff",
            "oneoff_prompt": "This should persist after reset",
        },
    )
    save_yaml(repo_path, {"max_iterations": 5})

    assert repo_path.exists()

    repo_path.unlink()

    config = cm.resolve_config()

    assert config.task_mode == "oneoff"
    assert config.oneoff_prompt == "This should persist after reset"

    loaded = load_yaml(global_path)
    assert loaded.get("oneoff_prompt") == "This should persist after reset"
    assert loaded.get("task_mode") == "oneoff"
