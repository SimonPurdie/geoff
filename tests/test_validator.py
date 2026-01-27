import pytest
from hypothesis import given, settings, strategies as st, HealthCheck
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
        # Should not error - should create blank file instead
        assert len(errors) == 0
        # Verify the file was created
        breadcrumbs_path = validator.execution_dir / "missing.md"
        assert breadcrumbs_path.exists()
        assert breadcrumbs_path.read_text() == ""

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

    def test_invalid_breadcrumbs_filename(self, validator):
        # Test with a path that would cause permission issues
        # Using a path that tries to write to root directory which should fail
        config = PromptConfig(
            breadcrumb_enabled=True,
            breadcrumbs_file="/root/forbidden.md",  # Should fail due to permissions
            task_mode="oneoff",
            oneoff_prompt="test",
            study_docs=[],
        )
        errors = validator.validate(config)
        # Should error because can't create file in root directory
        assert len(errors) > 0
        assert any("invalid" in e.lower() or "failed" in e.lower() for e in errors)


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


class TestValidateFrozen:
    def test_negative_frozen(self, validator):
        config = PromptConfig(max_frozen=-1)
        errors = validator.validate(config)
        assert "Frozen must be >= 0" in errors

    def test_zero_frozen_allowed(self, validator):
        config = PromptConfig(max_frozen=0)
        errors = validator.validate(config)
        assert not any("frozen" in e.lower() for e in errors)

    def test_positive_frozen_allowed(self, validator):
        config = PromptConfig(max_frozen=5)
        errors = validator.validate(config)
        assert not any("frozen" in e.lower() for e in errors)


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
            max_frozen=0,
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


def filepath_strategy(min_size=1, max_size=50):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    ).filter(
        lambda x: x
        and x.strip()
        and not x.strip().startswith("/")
        and "/" not in x.strip()[:-1]
    )


def text_strategy(min_size=1, max_size=100):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,!?\n"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


class TestValidatorPropertyBased:
    @given(
        max_iterations=st.integers(min_value=0, max_value=1000),
        max_stuck=st.integers(min_value=0, max_value=100),
        max_frozen=st.integers(min_value=0, max_value=120),
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_valid_config_with_positive_iterations(
        self, max_iterations, max_stuck, max_frozen, tmp_path
    ):
        validator = PromptValidator(execution_dir=tmp_path)
        existing_file = tmp_path / "doc.md"
        existing_file.write_text("# Test")
        config = PromptConfig(
            study_docs=["doc.md"],
            tasklist_file="doc.md",
            breadcrumbs_file="",
            task_mode="tasklist",
            backpressure_enabled=True,
            breadcrumb_enabled=False,
            max_iterations=max_iterations,
            max_stuck=max_stuck,
            max_frozen=max_frozen,
        )
        errors = validator.validate(config)
        assert not any("not found" in e for e in errors)
        assert not any("cannot be empty" in e for e in errors)
        assert not any("must be >= 0" in e for e in errors)

    @given(
        study_docs=st.lists(filepath_strategy(), max_size=5),
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_empty_study_doc_errors(self, study_docs, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        filtered_docs = [doc for doc in study_docs if doc and doc.strip()]
        empty_docs = ["" for _ in range(max(0, 5 - len(filtered_docs)))]
        all_docs = filtered_docs + empty_docs
        config = PromptConfig(
            study_docs=all_docs,
            task_mode="oneoff",
            oneoff_prompt="test",
            breadcrumb_enabled=False,
        )
        errors = validator.validate(config)
        error_count = sum(1 for e in errors if "Study doc path cannot be empty" in e)
        assert error_count == len([d for d in all_docs if not d or not d.strip()])

    @given(
        study_docs=st.lists(filepath_strategy(), max_size=5),
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_nonexistent_study_doc_files(self, study_docs, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        valid_docs = [doc for doc in study_docs if doc and doc.strip()]
        if not valid_docs:
            return
        config = PromptConfig(
            study_docs=valid_docs,
            task_mode="oneoff",
            oneoff_prompt="test",
            breadcrumb_enabled=False,
        )
        errors = validator.validate(config)
        for doc in valid_docs:
            if not (tmp_path / doc).exists():
                assert any(f"Study doc file not found: {doc}" in e for e in errors)

    @given(
        breadcrumbs_file=filepath_strategy(),
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_breadcrumb_file_existence(self, breadcrumbs_file, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        if not breadcrumbs_file or not breadcrumbs_file.strip():
            config = PromptConfig(
                breadcrumb_enabled=True,
                breadcrumbs_file="",
                task_mode="oneoff",
                oneoff_prompt="test",
                study_docs=[],
            )
            errors = validator.validate(config)
            assert any("Breadcrumbs file path cannot be empty" in e for e in errors)
        else:
            config = PromptConfig(
                breadcrumb_enabled=True,
                breadcrumbs_file=breadcrumbs_file,
                task_mode="oneoff",
                oneoff_prompt="test",
                study_docs=[],
            )
            errors = validator.validate(config)
            if not (tmp_path / breadcrumbs_file).exists():
                assert any(
                    f"Breadcrumbs file not found: {breadcrumbs_file}" in e
                    for e in errors
                )

    @given(
        tasklist_file=filepath_strategy(),
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_tasklist_file_existence(self, tasklist_file, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        if not tasklist_file or not tasklist_file.strip():
            config = PromptConfig(
                task_mode="tasklist",
                tasklist_file="",
                breadcrumb_enabled=False,
                study_docs=[],
            )
            errors = validator.validate(config)
            assert any("Tasklist file path cannot be empty" in e for e in errors)
        else:
            config = PromptConfig(
                task_mode="tasklist",
                tasklist_file=tasklist_file,
                breadcrumb_enabled=False,
                study_docs=[],
            )
            errors = validator.validate(config)
            if not (tmp_path / tasklist_file).exists():
                assert any(
                    f"Tasklist file not found: {tasklist_file}" in e for e in errors
                )

    @given(
        oneoff_prompt=text_strategy(),
    )
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_oneoff_prompt_validation(self, oneoff_prompt, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        stripped = oneoff_prompt.strip()
        if not stripped:
            config = PromptConfig(
                task_mode="oneoff",
                oneoff_prompt=oneoff_prompt,
                breadcrumb_enabled=False,
                study_docs=[],
            )
            errors = validator.validate(config)
            assert any("One-off prompt cannot be empty" in e for e in errors)
        else:
            config = PromptConfig(
                task_mode="oneoff",
                oneoff_prompt=oneoff_prompt,
                breadcrumb_enabled=False,
                study_docs=[],
            )
            errors = validator.validate(config)
            assert not any("One-off prompt cannot be empty" in e for e in errors)

    @given(
        max_iterations=st.integers(min_value=-100, max_value=100),
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_max_iterations_validation(self, max_iterations, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        config = PromptConfig(
            task_mode="oneoff",
            oneoff_prompt="test",
            breadcrumb_enabled=False,
            study_docs=[],
            max_iterations=max_iterations,
        )
        errors = validator.validate(config)
        if max_iterations < 0:
            assert any("Max iterations must be >= 0" in e for e in errors)
        else:
            assert not any("Max iterations must be >= 0" in e for e in errors)

    @given(
        max_stuck=st.integers(min_value=-100, max_value=100),
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_max_stuck_validation(self, max_stuck, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        config = PromptConfig(
            task_mode="oneoff",
            oneoff_prompt="test",
            breadcrumb_enabled=False,
            study_docs=[],
            max_stuck=max_stuck,
        )
        errors = validator.validate(config)
        if max_stuck < 0:
            assert any("Max stuck must be >= 0" in e for e in errors)
        else:
            assert not any("Max stuck must be >= 0" in e for e in errors)

    @given(
        max_frozen=st.integers(min_value=-100, max_value=100),
    )
    @settings(
        max_examples=50,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_max_frozen_validation(self, max_frozen, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        config = PromptConfig(
            task_mode="oneoff",
            oneoff_prompt="test",
            breadcrumb_enabled=False,
            study_docs=[],
            max_frozen=max_frozen,
        )
        errors = validator.validate(config)
        if max_frozen < 0:
            assert any("Frozen must be >= 0" in e for e in errors)
        else:
            assert not any("Frozen must be >= 0" in e for e in errors)

    @given(
        study_docs=st.lists(filepath_strategy(), max_size=3),
        breadcrumbs_file=filepath_strategy(),
        tasklist_file=filepath_strategy(),
        oneoff_prompt=text_strategy(),
        backpressure_enabled=st.booleans(),
        breadcrumb_enabled=st.booleans(),
        task_mode=st.sampled_from(["tasklist", "oneoff"]),
        max_iterations=st.integers(min_value=0, max_value=100),
        max_stuck=st.integers(min_value=0, max_value=10),
        max_frozen=st.integers(min_value=0, max_value=120),
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_is_valid_matches_validate(
        self,
        study_docs,
        breadcrumbs_file,
        tasklist_file,
        oneoff_prompt,
        backpressure_enabled,
        breadcrumb_enabled,
        task_mode,
        max_iterations,
        max_stuck,
        max_frozen,
        tmp_path,
    ):
        validator = PromptValidator(execution_dir=tmp_path)
        for doc in study_docs:
            if doc and doc.strip():
                (tmp_path / doc).touch()
        if tasklist_file and tasklist_file.strip():
            (tmp_path / tasklist_file).touch()
        if breadcrumbs_file and breadcrumbs_file.strip():
            (tmp_path / breadcrumbs_file).touch()

        config = PromptConfig(
            study_docs=study_docs,
            breadcrumbs_file=breadcrumbs_file,
            tasklist_file=tasklist_file,
            oneoff_prompt=oneoff_prompt,
            backpressure_enabled=backpressure_enabled,
            breadcrumb_enabled=breadcrumb_enabled,
            task_mode=task_mode,
            max_iterations=max_iterations,
            max_stuck=max_stuck,
            max_frozen=max_frozen,
        )
        errors = validator.validate(config)
        has_errors = len(errors) > 0
        is_valid = validator.is_valid(config)
        assert is_valid != has_errors

    @given(
        study_docs=st.lists(filepath_strategy(), max_size=3),
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_empty_study_doc_list_valid(self, study_docs, tmp_path):
        validator = PromptValidator(execution_dir=tmp_path)
        empty_docs = [d for d in study_docs if d and d.strip()]
        if not empty_docs:
            config = PromptConfig(
                study_docs=[],
                task_mode="oneoff",
                oneoff_prompt="test",
                breadcrumb_enabled=False,
            )
            errors = validator.validate(config)
            assert not any("Study doc" in e for e in errors)
