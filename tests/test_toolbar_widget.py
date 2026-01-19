import pytest
from textual.app import App, ComposeResult
from geoff.widgets.toolbar import ToolbarWidget


class ToolbarTestApp(App):
    CSS = """
    $geoff-primary: blue;
    $geoff-secondary: green;
    """

    def __init__(self):
        super().__init__()
        self.messages = []

    def compose(self) -> ComposeResult:
        yield ToolbarWidget()

    def on_toolbar_widget_copy_prompt(self, message: ToolbarWidget.CopyPrompt):
        self.messages.append("CopyPrompt")

    def on_toolbar_widget_run_once(self, message: ToolbarWidget.RunOnce):
        self.messages.append("RunOnce")

    def on_toolbar_widget_run_loop(self, message: ToolbarWidget.RunLoop):
        self.messages.append("RunLoop")

    def on_toolbar_widget_reset(self, message: ToolbarWidget.Reset):
        self.messages.append("Reset")

    def on_toolbar_widget_quit(self, message: ToolbarWidget.Quit):
        self.messages.append("Quit")


@pytest.mark.asyncio
async def test_toolbar_buttons():
    app = ToolbarTestApp()
    async with app.run_test() as pilot:
        # Check all buttons exist
        assert app.query_one("#btn-copy")
        assert app.query_one("#btn-run-once")
        assert app.query_one("#btn-run-loop")
        assert app.query_one("#btn-reset")
        assert app.query_one("#btn-quit")

        # Test Copy Prompt
        await pilot.click("#btn-copy")
        await pilot.pause()
        assert "CopyPrompt" in app.messages

        # Test Run Once
        app.messages.clear()
        await pilot.click("#btn-run-once")
        await pilot.pause()
        assert "RunOnce" in app.messages

        # Test Run Loop
        app.messages.clear()
        await pilot.click("#btn-run-loop")
        await pilot.pause()
        assert "RunLoop" in app.messages

        # Test Reset
        app.messages.clear()
        await pilot.click("#btn-reset")
        await pilot.pause()
        assert "Reset" in app.messages

        # Test Quit
        app.messages.clear()
        await pilot.click("#btn-quit")
        await pilot.pause()
        assert "Quit" in app.messages
