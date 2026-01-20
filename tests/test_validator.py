import pytest
from pathlib import Path

from geoff.config import PromptConfig
from geoff.validator import PromptValidator


@pytest.fixture
def validator(tmp_path):
    return PromptValidator(execution_dir=tmp_path)


class TestValidateEmptyStudyDocs:
    def test_empty_study_doc_path(self, validator):
        config = PromptConfig(study_docs=[""])
        errors = validator.validate(config)
        assert "Study doc path cannot be empty" in errors

    def test_whitespace_only_study_doc_path(self, validator):
        config = PromptConfig(study_docs=["   "])
        errors = validator.validate(config)
        assert "Study doc path cannot be empty" in errors


class TestValidateStudyDocFileExistence:
    def test_missing_study_doc_file(self, validator):
        config = PromptConfig(
            study_docs=["nonexistent.md"],
            breadcrumb_enabled=False,
            task_mode="oneoff",
            oneoff_prompt="test prompt",
        )
        errors = validator.validate(config)
        assert "Study doc file not found: nonexistent.md" in errors

    def test_existing_study_doc_file(self, validator):
        existing_file = validator.execution_dir / "existing.md"
        existing_file.write_text("# Test file")
        config = PromptConfig(
            study_docs=[existing_file.name],
            breadcrumb_enabled=False,
            task_mode="oneoff",
            oneoff_prompt="test prompt",
        )
        errors = validator.validate(config)
        assert not any("not found" in e for e in errors)


class TestValidateBreadcrumbs:
    def test_empty_breadcrumbs_path_when_enabled(self, validator):
        config = PromptConfig(breadcrumb_enabled=True, breadcrumbs_file="")
        errors = validator.validate(config)
        assert (
            "Breadcrumbs file path cannot be empty when breadcrumb is enabled" in errors
        )

    def test_missing_breadcrumbs_file(self, validator):
        config = PromptConfig(
            breadcrumb_enabled=True,
            breadcrumbs_file="missing.md",
            task_mode="oneoff",
            oneoff_prompt="test",
            study_docs=[],
        )
        errors = validator.validate(config)
        assert "Breadcrumbs file not found: missing.md" in errors

    def test_existing_breadcrumbs_file(self, validator):
        existing_file = validator.execution_dir / "existing.md"
        existing_file.write_text("# Test file")
        config = PromptConfig(
            breadcrumb_enabled=True,
            breadcrumbs_file=existing_file.name,
            task_mode="oneoff",
            oneoff_prompt="test",
            study_docs=[],
        )
        errors = validator.validate(config)
        assert not any("not found" in e for e in errors)

    def test_breadcrumbs_disabled_empty_path_ok(self, validator):
        config = PromptConfig(breadcrumb_enabled=False, breadcrumbs_file="")
        errors = validator.validate(config)
        assert not any("empty" in e.lower() for e in errors)


class TestValidateTaskSourceTasklist:
    def test_empty_tasklist_path(self, validator):
        config = PromptConfig(task_mode="tasklist", tasklist_file="")
        errors = validator.validate(config)
        assert "Tasklist file path cannot be empty in tasklist mode" in errors

    def test_missing_tasklist_file(self, validator):
        config = PromptConfig(
            task_mode="tasklist",
            tasklist_file="missing.md",
            breadcrumb_enabled=False,
            study_docs=[],
        )
        errors = validator.validate(config)
        assert "Tasklist file not found: missing.md" in errors

    def test_existing_tasklist_file(self, validator):
        existing_file = validator.execution_dir / "existing.md"
        existing_file.write_text("# Test file")
        config = PromptConfig(
            task_mode="tasklist",
            tasklist_file=existing_file.name,
            breadcrumb_enabled=False,
            study_docs=[],
        )
        errors = validator.validate(config)
        assert not any("not found" in e for e in errors)


class TestValidateTaskSourceOneoff:
    def test_empty_oneoff_prompt(self, validator):
        config = PromptConfig(task_mode="oneoff", oneoff_prompt="")
        errors = validator.validate(config)
        assert "One-off prompt cannot be empty in one-off mode" in errors

    def test_whitespace_only_oneoff_prompt(self, validator):
        config = PromptConfig(task_mode="oneoff", oneoff_prompt="   ")
        errors = validator.validate(config)
        assert "One-off prompt cannot be empty in one-off mode" in errors

    def test_valid_oneoff_prompt(self, validator):
        config = PromptConfig(task_mode="oneoff", oneoff_prompt="Do something cool")
        errors = validator.validate(config)
        assert not any("empty" in e.lower() for e in errors)


class TestValidateIterationValues:
    def test_negative_max_iterations(self, validator):
        config = PromptConfig(max_iterations=-1)
        errors = validator.validate(config)
        assert "Max iterations must be >= 0" in errors

    def test_zero_max_iterations_allowed(self, validator):
        config = PromptConfig(max_iterations=0)
        errors = validator.validate(config)
        assert not any("max iterations" in e.lower() for e in errors)

    def test_positive_max_iterations_allowed(self, validator):
        config = PromptConfig(max_iterations=10)
        errors = validator.validate(config)
        assert not any("max iterations" in e.lower() for e in errors)


class TestValidateMaxStuck:
    def test_negative_max_stuck(self, validator):
        config = PromptConfig(max_stuck=-1)
        errors = validator.validate(config)
        assert "Max stuck must be >= 0" in errors

    def test_zero_max_stuck_allowed(self, validator):
        config = PromptConfig(max_stuck=0)
        errors = validator.validate(config)
        assert not any("max stuck" in e.lower() for e in errors)

    def test_positive_max_stuck_allowed(self, validator):
        config = PromptConfig(max_stuck=5)
        errors = validator.validate(config)
        assert not any("max stuck" in e.lower() for e in errors)


class TestIsValid:
    def test_valid_config(self, validator):
        config = PromptConfig(
            study_docs=[],
            breadcrumbs_file="",
            task_mode="oneoff",
            oneoff_prompt="test prompt",
            breadcrumb_enabled=False,
            max_iterations=0,
            max_stuck=2,
        )
        assert validator.is_valid(config) is True

    def test_invalid_config(self, validator):
        config = PromptConfig(
            study_docs=[""],
            breadcrumbs_file="",
            task_mode="oneoff",
            oneoff_prompt="",
        )
        assert validator.is_valid(config) is False


class TestMultipleErrors:
    def test_multiple_validation_errors(self, validator):
        config = PromptConfig(
            study_docs=[""],
            breadcrumbs_file="",
            task_mode="tasklist",
            tasklist_file="",
            max_iterations=-1,
        )
        errors = validator.validate(config)
        assert len(errors) >= 4
        assert any("Study doc path cannot be empty" in e for e in errors)
        assert any(
            "Breadcrumbs file path cannot be empty when breadcrumb is enabled" in e
            for e in errors
        )
        assert any(
            "Tasklist file path cannot be empty in tasklist mode" in e for e in errors
        )
        assert any("Max iterations must be >= 0" in e for e in errors)


class TestDefaultExecutionDirectory:
    def test_uses_current_working_directory(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        validator = PromptValidator()
        assert validator.execution_dir == Path.cwd()

    def test_custom_execution_directory(self, tmp_path):
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        validator = PromptValidator(execution_dir=custom_dir)
        assert validator.execution_dir == custom_dir
