import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from textual.widgets import Input, Checkbox, TextArea, RadioButton
from geoff.widgets.prompt_preview import PromptPreviewWidget
from geoff.widgets.task_source import TaskSourceWidget


@pytest.fixture
def mock_config_manager(tmp_path):
    """Ensure tests run with a clean, isolated config."""
    # Patch ConfigManager where it's used in geoff.app
    with patch("geoff.app.ConfigManager") as mock:
        instance = mock.return_value
        # Point to a temporary path
        instance.repo_config_path = tmp_path / ".geoff" / "geoff.yaml"
        instance.repo_config_path.parent.mkdir(parents=True, exist_ok=True)

        # Mock resolve_config to return a fresh default config
        from geoff.config import PromptConfig

        instance.resolve_config.side_effect = lambda: PromptConfig()

        yield instance


@pytest.mark.asyncio
async def test_live_preview_updates(mock_config_manager):
    from geoff.app import GeoffApp

    app = GeoffApp()
    async with app.run_test(size=(120, 80)) as pilot:
        # 1. Test Backpressure toggle
        task_source_widget = app.query_one(TaskSourceWidget)
        checkbox = task_source_widget.query_one("#backpressure-checkbox", Checkbox)
        preview_widget = app.query_one(PromptPreviewWidget)

        # Initial state: Backpressure is enabled by default
        assert "IMPORTANT:" in str(preview_widget.prompt_text.render())

        # Toggle off
        checkbox.value = False
        await pilot.pause()

        assert "- After implementing functionality" not in str(
            preview_widget.prompt_text.render()
        )

        # 2. Test Task Source Input
        tasklist_input = task_source_widget.query_one("#tasklist-input", Input)

        tasklist_input.value = "new/plan.md"
        await pilot.pause()

        assert "follow new/plan.md" in str(preview_widget.prompt_text.render())

        # 3. Test One-off prompt
        app.query_one("#mode-oneoff", RadioButton).value = True
        await pilot.pause()

        oneoff_input = task_source_widget.query_one("#oneoff-input", TextArea)
        oneoff_input.text = "Custom prompt text"
        oneoff_input.post_message(TextArea.Changed(oneoff_input))
        await pilot.pause()

        assert "Custom prompt text" in str(preview_widget.prompt_text.render())


@pytest.mark.asyncio
async def test_reset_updates_ui(mock_config_manager):
    from geoff.app import GeoffApp

    app = GeoffApp()
    async with app.run_test(size=(120, 80)) as pilot:
        # Modify some values
        app.query_one("#backpressure-checkbox", Checkbox).value = False
        app.query_one("#tasklist-input", Input).value = "modified_plan.md"
        await pilot.pause()

        # Verify preview updated
        preview_text = str(app.query_one(PromptPreviewWidget).prompt_text.render())
        assert "- After implementing functionality" not in preview_text
        assert "follow modified_plan.md" in preview_text

        # Trigger Reset via action instead of click
        from geoff.widgets.toolbar import ToolbarWidget

        app.query_one(ToolbarWidget).post_message(ToolbarWidget.Reset())
        await pilot.pause()

        # Verify UI widgets reset
        assert app.query_one("#backpressure-checkbox", Checkbox).value is True
        assert app.query_one("#tasklist-input", Input).value == "docs/PLAN.md"

        # Verify preview reset
        preview_text_after = str(
            app.query_one(PromptPreviewWidget).prompt_text.render()
        )
        assert "IMPORTANT:" in preview_text_after
        assert "follow docs/PLAN.md" in preview_text_after


@pytest.mark.asyncio
async def test_theme_persistence_and_reactivity(mock_config_manager, tmp_path):
    from geoff.app import GeoffApp

    app = GeoffApp()
    async with app.run_test(size=(120, 80)) as pilot:
        # Initial theme
        assert app.theme == "catppuccin-mocha"

        # Change theme
        app.theme = "dracula"
        await pilot.pause()

        # Check if config was updated and saved
        assert app.prompt_config.theme == "dracula"
        mock_config_manager.save_repo_config.assert_called()

        # Verify it's saved to the actual config object passed to the mock
        saved_config = mock_config_manager.save_repo_config.call_args[0][0]
        assert saved_config.theme == "dracula"
