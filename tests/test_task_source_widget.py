import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input, RadioSet, TextArea
from geoff.config import PromptConfig
from geoff.widgets.task_source import TaskSourceWidget


class TaskSourceApp(App):
    CSS = """
    $geoff-primary: blue;
    $geoff-secondary: green;
    """

    def __init__(self, config):
        super().__init__()
        self.config_obj = config

    def compose(self) -> ComposeResult:
        yield TaskSourceWidget(self.config_obj)


@pytest.mark.asyncio
async def test_task_source_mode_switch():
    config = PromptConfig(task_mode="tasklist")
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        # Check initial state
        assert widget.query_one(RadioSet).pressed_button.id == "mode-tasklist"
        assert widget.query_one("#tasklist-input", Input).display is True
        assert widget.query_one("#oneoff-input", TextArea).display is False

        # Switch to one-off mode
        await pilot.click("#mode-oneoff")
        await pilot.pause()

        assert config.task_mode == "oneoff"
        assert widget.query_one("#tasklist-input", Input).display is False
        assert widget.query_one("#oneoff-input", TextArea).display is True

        # Switch back to tasklist mode
        await pilot.click("#mode-tasklist")
        await pilot.pause()

        assert config.task_mode == "tasklist"
        assert widget.query_one("#tasklist-input", Input).display is True
        assert widget.query_one("#oneoff-input", TextArea).display is False


@pytest.mark.asyncio
async def test_task_source_edit_values():
    config = PromptConfig(
        task_mode="tasklist", tasklist_file="old_plan.md", oneoff_prompt="old prompt"
    )
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        # Edit tasklist file
        input_widget = app.query_one("#tasklist-input", Input)
        input_widget.value = "new_plan.md"
        # Manually triggering changed event if needed, but value assignment might trigger it?
        # Textual's Input.Changed is usually triggered by user interaction.
        # We can simulate typing or just post the message.
        input_widget.post_message(Input.Changed(input_widget, "new_plan.md"))
        await pilot.pause()

        assert config.tasklist_file == "new_plan.md"

        # Switch to one-off mode to edit prompt
        await pilot.click("#mode-oneoff")
        await pilot.pause()

        # Edit one-off prompt
        textarea_widget = app.query_one("#oneoff-input", TextArea)
        textarea_widget.text = "new prompt"
        textarea_widget.post_message(TextArea.Changed(textarea_widget))
        await pilot.pause()

        assert config.oneoff_prompt == "new prompt"
