from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.message import Message
from textual import on


class ToolbarWidget(Static):
    DEFAULT_CSS = """
    $geoff-primary: #3b82f6;
    $geoff-secondary: #64748b;
    $geoff-accent: #8b5cf6;
    $geoff-success: #22c55e;
    $geoff-warning: #f59e0b;
    $geoff-error: #ef4444;
    $geoff-panel-bg: #1e293b;
    $geoff-border: #475569;
    $geoff-text: #f1f5f9;
    $geoff-text-muted: #94a3b8;

    ToolbarWidget {
        layout: horizontal;
        height: auto;
        padding: 1;
        align: center middle;
        background: $geoff-panel-bg;
        border-top: solid $geoff-border;
    }

    ToolbarWidget Button {
        margin-right: 1;
        min-width: 16;
    }

    ToolbarWidget #btn-copy {
        background: $geoff-secondary;
        color: $geoff-text;
    }

    ToolbarWidget #btn-copy:hover {
        background: #475569;
    }

    ToolbarWidget #btn-run-once {
        background: $geoff-success;
        color: $geoff-text;
    }

    ToolbarWidget #btn-run-once:hover {
        background: #16a34a;
    }

    ToolbarWidget #btn-run-loop {
        background: $geoff-accent;
        color: $geoff-text;
    }

    ToolbarWidget #btn-run-loop:hover {
        background: #7c3aed;
    }

    ToolbarWidget #btn-reset {
        background: $geoff-warning;
        color: $geoff-text;
    }

    ToolbarWidget #btn-reset:hover {
        background: #d97706;
    }

    ToolbarWidget #btn-quit {
        background: $geoff-error;
        color: $geoff-text;
    }

    ToolbarWidget #btn-quit:hover {
        background: #dc2626;
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
