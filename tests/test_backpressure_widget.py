import pytest
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
