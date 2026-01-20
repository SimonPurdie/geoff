import pytest
from hypothesis import given, settings, strategies as st
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


@pytest.mark.asyncio
async def test_toolbar_all_buttons_exist_property():
    class PropertyTestApp(App):
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

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        assert app.query_one("#btn-copy") is not None
        assert app.query_one("#btn-run-once") is not None
        assert app.query_one("#btn-run-loop") is not None
        assert app.query_one("#btn-reset") is not None
        assert app.query_one("#btn-quit") is not None


@pytest.mark.asyncio
async def test_toolbar_copy_button_triggers_message():
    class PropertyTestApp(App):
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

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        await pilot.click("#btn-copy")
        await pilot.pause()
        assert "CopyPrompt" in app.messages


@pytest.mark.asyncio
async def test_toolbar_run_once_button_triggers_message():
    class PropertyTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def __init__(self):
            super().__init__()
            self.messages = []

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

        def on_toolbar_widget_run_once(self, message: ToolbarWidget.RunOnce):
            self.messages.append("RunOnce")

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        await pilot.click("#btn-run-once")
        await pilot.pause()
        assert "RunOnce" in app.messages


@pytest.mark.asyncio
async def test_toolbar_run_loop_button_triggers_message():
    class PropertyTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def __init__(self):
            super().__init__()
            self.messages = []

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

        def on_toolbar_widget_run_loop(self, message: ToolbarWidget.RunLoop):
            self.messages.append("RunLoop")

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        await pilot.click("#btn-run-loop")
        await pilot.pause()
        assert "RunLoop" in app.messages


@pytest.mark.asyncio
async def test_toolbar_reset_button_triggers_message():
    class PropertyTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def __init__(self):
            super().__init__()
            self.messages = []

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

        def on_toolbar_widget_reset(self, message: ToolbarWidget.Reset):
            self.messages.append("Reset")

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        await pilot.click("#btn-reset")
        await pilot.pause()
        assert "Reset" in app.messages


@pytest.mark.asyncio
async def test_toolbar_quit_button_triggers_message():
    class PropertyTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def __init__(self):
            super().__init__()
            self.messages = []

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

        def on_toolbar_widget_quit(self, message: ToolbarWidget.Quit):
            self.messages.append("Quit")

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        await pilot.click("#btn-quit")
        await pilot.pause()
        assert "Quit" in app.messages


@pytest.mark.asyncio
async def test_toolbar_composes_correct_number_of_buttons():
    class PropertyTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        buttons = list(app.query("Button"))
        assert len(buttons) == 5


@pytest.mark.asyncio
async def test_toolbar_all_buttons_have_ids():
    class PropertyTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

    app = PropertyTestApp()
    async with app.run_test() as pilot:
        copy_btn = app.query_one("#btn-copy")
        run_once_btn = app.query_one("#btn-run-once")
        run_loop_btn = app.query_one("#btn-run-loop")
        reset_btn = app.query_one("#btn-reset")
        quit_btn = app.query_one("#btn-quit")

        assert copy_btn is not None
        assert run_once_btn is not None
        assert run_loop_btn is not None
        assert reset_btn is not None
        assert quit_btn is not None


@pytest.mark.asyncio
async def test_toolbar_all_buttons_fire_messages():
    class FullMessageTestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def __init__(self):
            super().__init__()
            self.received_messages = []

        def compose(self) -> ComposeResult:
            yield ToolbarWidget()

        def on_toolbar_widget_copy_prompt(self, message: ToolbarWidget.CopyPrompt):
            self.received_messages.append("CopyPrompt")

        def on_toolbar_widget_run_once(self, message: ToolbarWidget.RunOnce):
            self.received_messages.append("RunOnce")

        def on_toolbar_widget_run_loop(self, message: ToolbarWidget.RunLoop):
            self.received_messages.append("RunLoop")

        def on_toolbar_widget_reset(self, message: ToolbarWidget.Reset):
            self.received_messages.append("Reset")

        def on_toolbar_widget_quit(self, message: ToolbarWidget.Quit):
            self.received_messages.append("Quit")

    app = FullMessageTestApp()
    async with app.run_test() as pilot:
        await pilot.click("#btn-copy")
        await pilot.pause()
        assert "CopyPrompt" in app.received_messages

        app.received_messages.clear()
        await pilot.click("#btn-run-once")
        await pilot.pause()
        assert "RunOnce" in app.received_messages

        app.received_messages.clear()
        await pilot.click("#btn-run-loop")
        await pilot.pause()
        assert "RunLoop" in app.received_messages

        app.received_messages.clear()
        await pilot.click("#btn-reset")
        await pilot.pause()
        assert "Reset" in app.received_messages

        app.received_messages.clear()
        await pilot.click("#btn-quit")
        await pilot.pause()
        assert "Quit" in app.received_messages
