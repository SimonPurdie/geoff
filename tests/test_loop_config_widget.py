import pytest
from hypothesis import given, settings, strategies as st
from textual.app import App, ComposeResult
from textual.widgets import Input, Label
from geoff.config import PromptConfig
from geoff.widgets.loop_config import LoopConfigWidget


class LoopConfigApp(App):
    def __init__(self, config):
        super().__init__()
        self.config_obj = config

    def compose(self) -> ComposeResult:
        yield LoopConfigWidget(self.config_obj)


@pytest.mark.asyncio
async def test_loop_config_initialization():
    config = PromptConfig(max_iterations=0, max_stuck=2)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(LoopConfigWidget)
        max_iter_input = widget.query_one("#max-iterations", Input)
        max_stuck_input = widget.query_one("#max-stuck", Input)

        # Check initial values
        assert max_iter_input.value == "0"
        assert max_stuck_input.value == "2"

        # Check infinity indicator for 0
        indicator = widget.query_one("#infinity-indicator", Label)
        # Check visibility via classes or style
        assert "hidden" not in indicator.classes
        assert indicator.display is True


@pytest.mark.asyncio
async def test_loop_config_updates():
    config = PromptConfig(max_iterations=0, max_stuck=2)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        # Update max iterations
        await pilot.click("#max-iterations")
        # clear input first? Input usually appends?
        # Let's set value directly to be safe, or select all delete.
        # pilot.click focuses.
        # But for robust testing of binding:
        input_widget = app.query_one("#max-iterations", Input)
        input_widget.value = "5"
        # We need to trigger the event manually if setting value programmatically doesn't?
        # Textual Input.value setter DOES trigger Changed message usually.
        # But wait, checking BREADCRUMBS.md:
        # "Task 9 ... programmatic updates in tests (`widget.text = "value"`) require manually posting the `TextArea.Changed(widget)` event"
        # That was TextArea. Input might be different.
        # Let's assume Input.value setter works or we wait.

        await pilot.pause()

        assert config.max_iterations == 5

        # Check infinity indicator hidden
        indicator = app.query_one("#infinity-indicator", Label)
        assert "hidden" in indicator.classes

        # Update max stuck
        max_stuck_input = app.query_one("#max-stuck", Input)
        max_stuck_input.value = "10"
        await pilot.pause()

        assert config.max_stuck == 10


@pytest.mark.asyncio
async def test_loop_config_validation():
    config = PromptConfig(max_iterations=5, max_stuck=2)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        max_iter_input = app.query_one("#max-iterations", Input)

        # Invalid input (text)
        max_iter_input.value = "abc"
        await pilot.pause()

        # Should not update config if invalid
        assert config.max_iterations == 5

        # Invalid input (negative) - assuming we validate this
        max_iter_input.value = "-1"
        await pilot.pause()

        assert config.max_iterations == 5

        # Back to valid
        max_iter_input.value = "0"
        await pilot.pause()

        assert config.max_iterations == 0


@given(
    max_iterations=st.integers(min_value=0, max_value=1000),
    max_stuck=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_loop_config_property_initial_values(max_iterations, max_stuck):
    config = PromptConfig(max_iterations=max_iterations, max_stuck=max_stuck)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(LoopConfigWidget)
        max_iter_input = widget.query_one("#max-iterations", Input)
        max_stuck_input = widget.query_one("#max-stuck", Input)

        assert max_iter_input.value == str(max_iterations)
        assert max_stuck_input.value == str(max_stuck)


@given(
    max_iterations=st.integers(min_value=0, max_value=1000),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_infinity_indicator_property(max_iterations):
    config = PromptConfig(max_iterations=max_iterations, max_stuck=2)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(LoopConfigWidget)
        indicator = widget.query_one("#infinity-indicator", Label)

        if max_iterations == 0:
            assert "hidden" not in indicator.classes
            assert indicator.display is True
        else:
            assert "hidden" in indicator.classes


@given(
    max_iterations=st.integers(min_value=0, max_value=500),
    new_max_iterations=st.integers(min_value=0, max_value=500),
)
@settings(max_examples=15)
@pytest.mark.asyncio
async def test_loop_config_updates_property(max_iterations, new_max_iterations):
    config = PromptConfig(max_iterations=max_iterations, max_stuck=2)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(LoopConfigWidget)
        max_iter_input = widget.query_one("#max-iterations", Input)

        max_iter_input.value = str(new_max_iterations)
        await pilot.pause()

        assert config.max_iterations == new_max_iterations


@given(
    initial_max_iterations=st.integers(min_value=0, max_value=100),
    new_max_stuck=st.integers(min_value=0, max_value=50),
)
@settings(max_examples=15)
@pytest.mark.asyncio
async def test_max_stuck_updates_property(initial_max_iterations, new_max_stuck):
    config = PromptConfig(max_iterations=initial_max_iterations, max_stuck=2)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        max_stuck_input = app.query_one("#max-stuck", Input)

        max_stuck_input.value = str(new_max_stuck)
        await pilot.pause()

        assert config.max_stuck == new_max_stuck


@given(
    max_iterations=st.integers(min_value=0, max_value=100),
    max_stuck=st.integers(min_value=0, max_value=100),
)
@settings(max_examples=15)
@pytest.mark.asyncio
async def test_update_from_config_property(max_iterations, max_stuck):
    config = PromptConfig(max_iterations=0, max_stuck=0)
    app = LoopConfigApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(LoopConfigWidget)

        new_config = PromptConfig(max_iterations=max_iterations, max_stuck=max_stuck)
        widget.update_from_config(new_config)

        max_iter_input = widget.query_one("#max-iterations", Input)
        max_stuck_input = widget.query_one("#max-stuck", Input)

        assert max_iter_input.value == str(max_iterations)
        assert max_stuck_input.value == str(max_stuck)
