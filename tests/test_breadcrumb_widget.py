import pytest
from hypothesis import given, settings, strategies as st
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


@given(breadcrumb_enabled=st.booleans())
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_breadcrumb_initial_state(breadcrumb_enabled):
    config = PromptConfig(breadcrumb_enabled=breadcrumb_enabled)
    app = BreadcrumbApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BreadcrumbWidget)
        checkbox = widget.query_one("#breadcrumb-checkbox", Checkbox)

        assert checkbox.value == breadcrumb_enabled
        assert config.breadcrumb_enabled == breadcrumb_enabled


@given(
    initial_enabled=st.booleans(), toggle_times=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_breadcrumb_toggle_property(initial_enabled, toggle_times):
    config = PromptConfig(breadcrumb_enabled=initial_enabled)
    app = BreadcrumbApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BreadcrumbWidget)
        checkbox = widget.query_one("#breadcrumb-checkbox", Checkbox)

        expected = initial_enabled
        for _ in range(toggle_times):
            await pilot.click("#breadcrumb-checkbox")
            await pilot.pause()
            expected = not expected
            assert checkbox.value == expected
            assert config.breadcrumb_enabled == expected


@given(initial_enabled=st.booleans(), new_enabled=st.booleans())
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_breadcrumb_update_from_config(initial_enabled, new_enabled):
    config = PromptConfig(breadcrumb_enabled=initial_enabled)
    app = BreadcrumbApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(BreadcrumbWidget)

        new_config = PromptConfig(breadcrumb_enabled=new_enabled)
        widget.update_from_config(new_config)

        checkbox = widget.query_one("#breadcrumb-checkbox", Checkbox)
        assert checkbox.value == new_enabled


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
