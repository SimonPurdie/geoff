import pytest
from hypothesis import given, settings, strategies as st
from textual.app import App, ComposeResult
from textual.widgets import Checkbox
from geoff.config import PromptConfig
from geoff.widgets.backpressure import BackpressureWidget


class BackpressureApp(App):
    CSS = """
    $geoff-primary: blue;
    $geoff-secondary: green;
    """

    def __init__(self, config):
        super().__init__()
        self.config_obj = config

    def compose(self) -> ComposeResult:
        yield BackpressureWidget(self.config_obj)


@given(backpressure_enabled=st.booleans())
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_backpressure_initial_state(backpressure_enabled):
    config = PromptConfig(backpressure_enabled=backpressure_enabled)
    app = BackpressureApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BackpressureWidget)
        checkbox = widget.query_one("#backpressure-checkbox", Checkbox)

        assert checkbox.value == backpressure_enabled
        assert config.backpressure_enabled == backpressure_enabled


@given(
    initial_enabled=st.booleans(), toggle_times=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_backpressure_toggle_property(initial_enabled, toggle_times):
    config = PromptConfig(backpressure_enabled=initial_enabled)
    app = BackpressureApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BackpressureWidget)
        checkbox = widget.query_one("#backpressure-checkbox", Checkbox)

        expected = initial_enabled
        for _ in range(toggle_times):
            await pilot.click("#backpressure-checkbox")
            await pilot.pause()
            expected = not expected
            assert checkbox.value == expected
            assert config.backpressure_enabled == expected


@given(initial_enabled=st.booleans(), new_enabled=st.booleans())
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_backpressure_update_from_config(initial_enabled, new_enabled):
    config = PromptConfig(backpressure_enabled=initial_enabled)
    app = BackpressureApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BackpressureWidget)

        new_config = PromptConfig(backpressure_enabled=new_enabled)
        widget.update_from_config(new_config)

        checkbox = widget.query_one("#backpressure-checkbox", Checkbox)
        assert checkbox.value == new_enabled


@pytest.mark.asyncio
async def test_backpressure_toggle():
    config = PromptConfig(backpressure_enabled=True)
    app = BackpressureApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BackpressureWidget)
        checkbox = widget.query_one(Checkbox)

        # Check initial state
        assert checkbox.value is True
        assert config.backpressure_enabled is True

        # Toggle off
        await pilot.click("#backpressure-checkbox")
        await pilot.pause()

        assert checkbox.value is False
        assert config.backpressure_enabled is False

        # Toggle on
        await pilot.click("#backpressure-checkbox")
        await pilot.pause()

        assert checkbox.value is True
        assert config.backpressure_enabled is True
