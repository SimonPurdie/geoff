import pytest
from textual.app import App, ComposeResult
from textual.widgets import Checkbox
from geoff.config import PromptConfig
from geoff.widgets.breadcrumb import BreadcrumbWidget


class BreadcrumbApp(App):
    CSS = """
    $geoff-primary: blue;
    $geoff-secondary: green;
    """

    def __init__(self, config):
        super().__init__()
        self.config_obj = config

    def compose(self) -> ComposeResult:
        yield BreadcrumbWidget(self.config_obj)


@pytest.mark.asyncio
async def test_breadcrumb_toggle():
    config = PromptConfig(breadcrumb_enabled=True)
    app = BreadcrumbApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BreadcrumbWidget)
        checkbox = widget.query_one(Checkbox)

        # Check initial state
        assert checkbox.value is True
        assert config.breadcrumb_enabled is True

        # Toggle off
        await pilot.click("#breadcrumb-checkbox")
        await pilot.pause()

        assert checkbox.value is False
        assert config.breadcrumb_enabled is False

        # Toggle on
        await pilot.click("#breadcrumb-checkbox")
        await pilot.pause()

        assert checkbox.value is True
        assert config.breadcrumb_enabled is True
