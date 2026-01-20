import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

from geoff.executor import (
    compute_repo_hash,
    execute_opencode_once,
    execute_opencode_loop,
)


class TestComputeRepoHash:
    """Tests for the compute_repo_hash function."""

    def test_returns_git_hash_when_in_git_repo(self, tmp_path):
        """Should return git HEAD hash when in a git repository."""
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "initial"],
            cwd=tmp_path,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "test",
                "GIT_AUTHOR_EMAIL": "test@test.com",
                "GIT_COMMITTER_NAME": "test",
                "GIT_COMMITTER_EMAIL": "test@test.com",
            },
        )

        result = compute_repo_hash(tmp_path)

        assert len(result) == 40
        assert result.isalnum()

    def test_returns_fallback_hash_when_not_in_git_repo(self, tmp_path):
        """Should compute directory hash when not in a git repository."""
        (tmp_path / "test.txt").write_text("hello world")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "another.txt").write_text("content")

        result = compute_repo_hash(tmp_path)

        assert len(result) == 16
        assert result.isalnum()

    def test_consistent_hash_for_same_content(self, tmp_path):
        """Same directory content should produce same hash."""
        (tmp_path / "file.txt").write_text("content")

        hash1 = compute_repo_hash(tmp_path)
        hash2 = compute_repo_hash(tmp_path)

        assert hash1 == hash2

    def test_different_hash_for_different_content(self, tmp_path):
        """Different directory content should produce different hash."""
        import time

        (tmp_path / "file.txt").write_text("content1")
        hash1 = compute_repo_hash(tmp_path)

        time.sleep(0.01)
        (tmp_path / "file.txt").write_text("content2")
        hash2 = compute_repo_hash(tmp_path)

        assert hash1 != hash2

    def test_hash_changes_on_file_modification(self, tmp_path):
        """Hash should change when a file is modified."""
        import time

        test_file = tmp_path / "test.txt"
        test_file.write_text("original")
        hash1 = compute_repo_hash(tmp_path)

        time.sleep(0.01)
        test_file.write_text("modified")
        hash2 = compute_repo_hash(tmp_path)

        assert hash1 != hash2

    def test_hash_changes_on_file_deletion(self, tmp_path):
        """Hash should change when a file is deleted."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        hash1 = compute_repo_hash(tmp_path)

        test_file.unlink()
        hash2 = compute_repo_hash(tmp_path)

        assert hash1 != hash2

    def test_hash_changes_on_new_file(self, tmp_path):
        """Hash should change when a new file is added."""
        hash1 = compute_repo_hash(tmp_path)

        (tmp_path / "new.txt").write_text("new content")
        hash2 = compute_repo_hash(tmp_path)

        assert hash1 != hash2

    def test_uses_cwd_when_no_exec_dir_specified(self, tmp_path):
        """Should use current working directory when exec_dir is None."""
        with patch("geoff.executor.Path.cwd", return_value=tmp_path):
            subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", "initial"],
                cwd=tmp_path,
                capture_output=True,
                env={
                    **os.environ,
                    "GIT_AUTHOR_NAME": "test",
                    "GIT_AUTHOR_EMAIL": "test@test.com",
                    "GIT_COMMITTER_NAME": "test",
                    "GIT_COMMITTER_EMAIL": "test@test.com",
                },
            )

            result = compute_repo_hash()

            assert len(result) == 40


class TestExecuteOpencodeOnce:
    """Tests for the execute_opencode_once function."""

    @patch("geoff.executor.subprocess.run")
    def test_executes_opencode_command(self, mock_run, tmp_path):
        """Should execute opencode run with the given prompt."""
        mock_run.return_value = MagicMock()

        execute_opencode_once("test prompt", tmp_path)

        mock_run.assert_called_once()
        args = mock_run.call_args
        assert args[1]["cwd"] == tmp_path
        assert "opencode" in args[0][0]
        assert "run" in args[0][0]
        assert "test prompt" in args[0][0]
        assert "--log-level" in args[0][0]
        assert "INFO" in args[0][0]

    @patch("geoff.executor.subprocess.run")
    def test_uses_check_false(self, mock_run, tmp_path):
        """Should use check=False to allow non-zero exit codes."""
        mock_run.return_value = MagicMock()

        execute_opencode_once("prompt", tmp_path)

        assert mock_run.call_args[1]["check"] is False

    @patch("geoff.executor.subprocess.run")
    def test_handles_keyboard_interrupt(self, mock_run, tmp_path):
        """Should handle KeyboardInterrupt gracefully."""
        mock_run.side_effect = KeyboardInterrupt()

        execute_opencode_once("prompt", tmp_path)

        mock_run.assert_called()

    @patch("geoff.executor.subprocess.run")
    def test_handles_missing_opencode(self, mock_run, tmp_path):
        """Should handle FileNotFoundError when opencode is not installed."""
        mock_run.side_effect = FileNotFoundError()

        with pytest.raises(SystemExit) as exc_info:
            execute_opencode_once("prompt", tmp_path)

        assert exc_info.value.code == 1

    @patch("geoff.executor.subprocess.run")
    def test_uses_current_dir_when_not_specified(self, mock_run, tmp_path):
        """Should use current working directory when exec_dir is None."""
        mock_run.return_value = MagicMock()

        with patch("geoff.executor.Path.cwd", return_value=tmp_path):
            execute_opencode_once("prompt")

            assert mock_run.call_args[1]["cwd"] == tmp_path


class TestExecuteOpencodeLoop:
    """Tests for the execute_opencode_loop function."""

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_single_iteration_with_max_iterations_one(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should run exactly once when max_iterations=1."""
        mock_run.return_value = MagicMock()
        mock_hash.return_value = "abc123"

        execute_opencode_loop(
            "prompt", max_iterations=1, max_stuck=2, exec_dir=tmp_path
        )

        assert mock_run.call_count == 1
        mock_sleep.assert_not_called()

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_runs_indefinitely_when_max_iterations_zero(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should run indefinitely when max_iterations=0."""
        call_count = 0

        def fake_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                raise KeyboardInterrupt()
            return MagicMock()

        def changing_hash(*args, **kwargs):
            return f"hash{call_count}"

        mock_run.side_effect = fake_run
        mock_hash.side_effect = changing_hash

        execute_opencode_loop(
            "prompt", max_iterations=0, max_stuck=2, exec_dir=tmp_path
        )

        assert call_count == 3
        mock_sleep.assert_called()

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_stops_after_max_stuck_consecutive_no_changes(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should stop after max_stuck consecutive iterations with no changes."""
        mock_run.return_value = MagicMock()

        def changing_hash(*args):
            calls = mock_hash.call_count
            if calls < 3:
                return f"hash{calls}"
            return "same_hash"

        mock_hash.side_effect = changing_hash

        execute_opencode_loop(
            "prompt", max_iterations=0, max_stuck=2, exec_dir=tmp_path
        )

        assert mock_run.call_count == 3

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_resets_stuck_count_on_changes(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should reset stuck counter when changes are detected."""
        call_count = 0

        def fake_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 5:
                raise KeyboardInterrupt()
            return MagicMock()

        def fake_hash(*args):
            if mock_hash.call_count % 2 == 0:
                return "same_hash"
            return "different_hash"

        mock_run.side_effect = fake_run
        mock_hash.side_effect = fake_hash

        execute_opencode_loop(
            "prompt", max_iterations=0, max_stuck=3, exec_dir=tmp_path
        )

        assert call_count == 5

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_stops_at_max_iterations(self, mock_run, mock_hash, mock_sleep, tmp_path):
        """Should stop when max_iterations is reached."""
        mock_run.return_value = MagicMock()
        mock_hash.return_value = "same"

        execute_opencode_loop(
            "prompt", max_iterations=5, max_stuck=10, exec_dir=tmp_path
        )

        assert mock_run.call_count == 5

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_handles_keyboard_interrupt(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should handle KeyboardInterrupt gracefully."""
        mock_run.side_effect = KeyboardInterrupt()
        mock_hash.return_value = "abc123"

        execute_opencode_loop("prompt", max_iterations=10, exec_dir=tmp_path)

        mock_run.assert_called()

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_handles_missing_opencode(self, mock_run, mock_hash, mock_sleep, tmp_path):
        """Should handle FileNotFoundError when opencode is not installed."""
        mock_run.side_effect = FileNotFoundError()
        mock_hash.return_value = "abc123"

        with pytest.raises(SystemExit) as exc_info:
            execute_opencode_loop("prompt", exec_dir=tmp_path)

        assert exc_info.value.code == 1

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_sleeps_two_seconds_between_iterations(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should sleep 2 seconds between iterations."""
        call_count = 0

        def fake_run(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count >= 3:
                raise KeyboardInterrupt()
            return MagicMock()

        def changing_hash(*args):
            return f"hash{call_count}"

        mock_run.side_effect = fake_run
        mock_hash.side_effect = changing_hash

        execute_opencode_loop("prompt", max_iterations=5, exec_dir=tmp_path)

        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(2)

    @patch("geoff.executor.time.sleep")
    @patch("geoff.executor.compute_repo_hash")
    @patch("geoff.executor.subprocess.run")
    def test_uses_current_dir_when_not_specified(
        self, mock_run, mock_hash, mock_sleep, tmp_path
    ):
        """Should use current working directory when exec_dir is None."""
        mock_run.return_value = MagicMock()
        mock_hash.return_value = "abc123"
        mock_run.side_effect = KeyboardInterrupt()

        with patch("geoff.executor.Path.cwd", return_value=tmp_path):
            execute_opencode_loop("prompt")

            assert mock_run.call_args[1]["cwd"] == tmp_path
