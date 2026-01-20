import pytest
from hypothesis import given, settings, strategies as st
from textual.app import App, ComposeResult
from textual.widgets import Input, RadioSet, TextArea, RadioButton, Checkbox
from geoff.config import PromptConfig
from geoff.widgets.task_source import TaskSourceWidget


def filepath_strategy(min_size=1, max_size=50):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


def text_strategy(min_size=1, max_size=100):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,!?\n"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


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


@given(
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
    tasklist_file=filepath_strategy(),
    oneoff_prompt=text_strategy(),
    backpressure_enabled=st.booleans(),
    max_iterations=st.integers(min_value=0, max_value=100),
    max_stuck=st.integers(min_value=0, max_value=10),
)
@settings(max_examples=30)
@pytest.mark.asyncio
async def test_task_source_initial_state(
    task_mode,
    tasklist_file,
    oneoff_prompt,
    backpressure_enabled,
    max_iterations,
    max_stuck,
):
    config = PromptConfig(
        task_mode=task_mode,
        tasklist_file=tasklist_file,
        oneoff_prompt=oneoff_prompt,
        backpressure_enabled=backpressure_enabled,
        max_iterations=max_iterations,
        max_stuck=max_stuck,
    )
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        radios = widget.query_one(RadioSet)
        if task_mode == "tasklist":
            assert radios.pressed_button is not None
            assert radios.pressed_button.id == "mode-tasklist"
            assert widget.query_one("#tasklist-input", Input).display is True
            assert widget.query_one("#oneoff-input", TextArea).display is False
        else:
            assert radios.pressed_button is not None
            assert radios.pressed_button.id == "mode-oneoff"
            assert widget.query_one("#tasklist-input", Input).display is False
            assert widget.query_one("#oneoff-input", TextArea).display is True

        assert (
            widget.query_one("#backpressure-checkbox", Checkbox).value
            == backpressure_enabled
        )
        assert widget.query_one("#max-iterations", Input).value == str(max_iterations)
        assert widget.query_one("#max-stuck", Input).value == str(max_stuck)


@given(
    initial_mode=st.sampled_from(["tasklist", "oneoff"]),
    switch_times=st.integers(min_value=0, max_value=3),
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_task_source_mode_switch_property(initial_mode, switch_times):
    config = PromptConfig(task_mode=initial_mode)
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        expected_mode = initial_mode
        for _ in range(switch_times):
            if expected_mode == "tasklist":
                await pilot.click("#mode-oneoff")
            else:
                await pilot.click("#mode-tasklist")
            await pilot.pause()
            expected_mode = "oneoff" if expected_mode == "tasklist" else "tasklist"

            assert config.task_mode == expected_mode


@given(
    initial_tasklist=filepath_strategy(),
    new_tasklist=filepath_strategy(),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_task_source_tasklist_update(initial_tasklist, new_tasklist):
    config = PromptConfig(task_mode="tasklist", tasklist_file=initial_tasklist)
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        new_config = PromptConfig(task_mode="tasklist", tasklist_file=new_tasklist)
        widget.update_from_config(new_config)

        tasklist_input = widget.query_one("#tasklist-input", Input)
        assert tasklist_input.value == new_tasklist


@given(
    initial_prompt=text_strategy(),
    new_prompt=text_strategy(),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_task_source_oneoff_update(initial_prompt, new_prompt):
    config = PromptConfig(task_mode="oneoff", oneoff_prompt=initial_prompt)
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        new_config = PromptConfig(task_mode="oneoff", oneoff_prompt=new_prompt)
        widget.update_from_config(new_config)

        oneoff_input = widget.query_one("#oneoff-input", TextArea)
        assert oneoff_input.text == new_prompt


@given(
    initial_mode=st.sampled_from(["tasklist", "oneoff"]),
    new_mode=st.sampled_from(["tasklist", "oneoff"]),
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_task_source_update_mode(initial_mode, new_mode):
    config = PromptConfig(task_mode=initial_mode)
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        new_config = PromptConfig(task_mode=new_mode)
        widget.update_from_config(new_config)

        assert widget.config.task_mode == new_mode


@pytest.mark.asyncio
async def test_task_source_mode_switch():
    config = PromptConfig(task_mode="tasklist")
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        # Check initial state
        radios = widget.query_one(RadioSet)
        assert radios.pressed_button is not None
        assert radios.pressed_button.id == "mode-tasklist"
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


@given(
    initial_enabled=st.booleans(), toggle_times=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_backpressure_toggle_property(initial_enabled, toggle_times):
    config = PromptConfig(backpressure_enabled=initial_enabled)
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)
        checkbox = widget.query_one("#backpressure-checkbox", Checkbox)

        expected = initial_enabled
        for _ in range(toggle_times):
            await pilot.click("#backpressure-checkbox")
            await pilot.pause()
            expected = not expected
            assert checkbox.value == expected
            assert config.backpressure_enabled == expected


@pytest.mark.asyncio
async def test_loop_config_edit():
    config = PromptConfig(max_iterations=0, max_stuck=2)
    app = TaskSourceApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(TaskSourceWidget)

        # Max Iterations
        iter_input = widget.query_one("#max-iterations", Input)
        iter_input.value = "5"
        iter_input.post_message(Input.Changed(iter_input, "5"))
        await pilot.pause()
        assert config.max_iterations == 5

        # Validation test
        iter_input.value = "-1"
        iter_input.post_message(Input.Changed(iter_input, "-1"))
        await pilot.pause()
        assert config.max_iterations == 5  # Should not change

        # Max Stuck
        stuck_input = widget.query_one("#max-stuck", Input)
        stuck_input.value = "10"
        stuck_input.post_message(Input.Changed(stuck_input, "10"))
        await pilot.pause()
        assert config.max_stuck == 10
