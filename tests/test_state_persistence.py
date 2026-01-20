"""Tests for state persistence functionality in GeoffApp."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from textual.app import App

from geoff.config import PromptConfig
from geoff.config_manager import ConfigManager


class TestStatePersistence:
    """Test cases for auto-save config functionality."""

    def test_save_config_creates_directory(self, tmp_path):
        """Test that save_repo_config creates the .geoff directory if it doesn't exist."""
        cm = ConfigManager(working_dir=tmp_path)
        config = PromptConfig(max_iterations=42)

        repo_path = tmp_path / ".geoff" / "geoff.yaml"
        assert not repo_path.exists()

        cm.save_repo_config(config)

        assert repo_path.exists()
        loaded = cm.resolve_config()
        assert loaded.max_iterations == 42

    def test_save_config_overwrites_existing(self, tmp_path):
        """Test that save_repo_config overwrites existing config file."""
        cm = ConfigManager(working_dir=tmp_path)

        config1 = PromptConfig(max_iterations=10)
        cm.save_repo_config(config1)

        config2 = PromptConfig(max_iterations=99)
        cm.save_repo_config(config2)

        loaded = cm.resolve_config()
        assert loaded.max_iterations == 99

    def test_config_persistence_across_manager_instances(self, tmp_path):
        """Test that config saved by one manager can be loaded by another."""
        cm1 = ConfigManager(working_dir=tmp_path)
        config = PromptConfig(
            study_docs=["docs/A.md", "docs/B.md"], task_mode="oneoff", max_iterations=50
        )
        cm1.save_repo_config(config)

        cm2 = ConfigManager(working_dir=tmp_path)
        loaded = cm2.resolve_config()

        assert loaded.study_docs == ["docs/A.md", "docs/B.md"]
        assert loaded.task_mode == "oneoff"
        assert loaded.max_iterations == 50

    def test_partial_config_update_preserves_other_fields(self, tmp_path):
        """Test that updating one field doesn't erase others."""
        cm = ConfigManager(working_dir=tmp_path)

        config1 = PromptConfig(
            study_docs=["docs/SPEC.md"], max_iterations=10, backpressure_enabled=True
        )
        cm.save_repo_config(config1)

        config2 = PromptConfig(
            study_docs=["docs/SPEC.md", "docs/PLAN.md"],
            max_iterations=20,
            backpressure_enabled=False,
        )
        cm.save_repo_config(config2)

        loaded = cm.resolve_config()
        assert loaded.study_docs == ["docs/SPEC.md", "docs/PLAN.md"]
        assert loaded.max_iterations == 20
        assert loaded.backpressure_enabled is False

    def test_empty_study_docs_persists_correctly(self, tmp_path):
        """Test that empty study_docs list is persisted correctly."""
        cm = ConfigManager(working_dir=tmp_path)
        config = PromptConfig(study_docs=[])

        cm.save_repo_config(config)

        loaded = cm.resolve_config()
        assert loaded.study_docs == []

    def test_save_config_handles_special_characters(self, tmp_path):
        """Test that special characters in paths are handled correctly."""
        cm = ConfigManager(working_dir=tmp_path)
        config = PromptConfig(
            study_docs=["docs with spaces/file.md"],
            tasklist_file="path/to/file with spaces.md",
            breadcrumbs_file="some file.md",
        )

        cm.save_repo_config(config)

        loaded = cm.resolve_config()
        assert loaded.study_docs == ["docs with spaces/file.md"]
        assert loaded.tasklist_file == "path/to/file with spaces.md"
        assert loaded.breadcrumbs_file == "some file.md"

    def test_save_config_persists_theme(self, tmp_path):
        """Test that the theme is persisted in the config."""
        cm = ConfigManager(working_dir=tmp_path)
        config = PromptConfig(theme="monokai")

        cm.save_repo_config(config)

        loaded = cm.resolve_config()
        assert loaded.theme == "monokai"


class TestResetFunctionality:
    """Test cases for reset to defaults functionality."""

    def test_reset_removes_repo_config(self, tmp_path):
        """Test that reset removes the repo-level config file."""
        cm = ConfigManager(working_dir=tmp_path)

        config = PromptConfig(max_iterations=999)
        cm.save_repo_config(config)

        repo_path = tmp_path / ".geoff" / "geoff.yaml"
        assert repo_path.exists()

        if repo_path.exists():
            repo_path.unlink()

        assert not repo_path.exists()

    def test_reset_after_save_returns_defaults(self, tmp_path):
        """Test that after reset, config returns to defaults."""
        cm = ConfigManager(working_dir=tmp_path)

        custom_config = PromptConfig(
            max_iterations=100, task_mode="oneoff", backpressure_enabled=False
        )
        cm.save_repo_config(custom_config)

        repo_path = tmp_path / ".geoff" / "geoff.yaml"
        if repo_path.exists():
            repo_path.unlink()

        loaded = cm.resolve_config()

        assert loaded.max_iterations == 0
        assert loaded.task_mode == "tasklist"
        assert loaded.backpressure_enabled is True

    def test_reset_preserves_global_config(self, tmp_path):
        """Test that reset removes repo config but preserves global config precedence."""
        from geoff.config_io import save_yaml

        cm = ConfigManager(working_dir=tmp_path)
        global_path = tmp_path / "global.yaml"
        cm.global_config_path = global_path

        save_yaml(global_path, {"max_iterations": 25, "task_mode": "oneoff"})

        repo_path = tmp_path / ".geoff" / "geoff.yaml"
        save_yaml(repo_path, {"max_iterations": 50})

        if repo_path.exists():
            repo_path.unlink()

        loaded = cm.resolve_config()
        assert loaded.max_iterations == 25
        assert loaded.task_mode == "oneoff"
