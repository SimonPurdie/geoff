from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.message import Message
from textual import on


class ToolbarWidget(Static):
    DEFAULT_CSS = """
    ToolbarWidget {
        layout: horizontal;
        height: auto;
        padding: 1;
        align: center middle;
        background: $surface;
        border-top: solid $primary;
    }

    ToolbarWidget Button {
        margin-right: 1;
    }
    
    #btn-quit {
        background: $error;
        color: $text;
    }
    """

    class CopyPrompt(Message):
        """Request to copy the effective prompt to clipboard."""

        pass

    class RunOnce(Message):
        """Request to run the prompt once."""

        pass

    class RunLoop(Message):
        """Request to run the prompt in a loop."""

        pass

    class Reset(Message):
        """Request to reset configuration to defaults."""

        pass

    class Quit(Message):
        """Request to quit the application."""

        pass

    def compose(self) -> ComposeResult:
        yield Button("Copy Prompt", id="btn-copy", variant="primary")
        yield Button("Run Once", id="btn-run-once", variant="success")
        yield Button("Run Loop", id="btn-run-loop", variant="success")
        yield Button("Reset", id="btn-reset", variant="warning")
        yield Button("Quit", id="btn-quit", variant="error")

    @on(Button.Pressed, "#btn-copy")
    def action_copy_prompt(self):
        self.post_message(self.CopyPrompt())

    @on(Button.Pressed, "#btn-run-once")
    def action_run_once(self):
        self.post_message(self.RunOnce())

    @on(Button.Pressed, "#btn-run-loop")
    def action_run_loop(self):
        self.post_message(self.RunLoop())

    @on(Button.Pressed, "#btn-reset")
    def action_reset(self):
        self.post_message(self.Reset())

    @on(Button.Pressed, "#btn-quit")
    def action_quit(self):
        self.post_message(self.Quit())
