from pathlib import Path
from geoff.config_manager import ConfigManager
from geoff.config import PromptConfig
from geoff.config_io import save_yaml


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
