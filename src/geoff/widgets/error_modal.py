from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ErrorModal(ModalScreen[None]):
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

    ErrorModal {
        align: center middle;
    }

    ErrorModal > Container {
        width: 60;
        max-height: 20;
        border: thick $geoff-error;
        background: $geoff-panel-bg;
        padding: 1;
    }

    #error-title {
        color: $geoff-error;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    #error-content {
        height: auto;
        max-height: 14;
        margin-bottom: 1;
    }

    #error-content Static {
        color: $geoff-text;
        padding: 0;
        margin-bottom: 0;
    }

    #error-ok-button {
        width: 100%;
        margin-top: 1;
        background: $geoff-error;
        color: $geoff-text;
    }

    #error-ok-button:hover {
        background: #dc2626;
    }
    """

    def __init__(self, errors: List[str]):
        super().__init__()
        self.errors = errors

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Error", id="error-title")
            with Vertical(id="error-content"):
                for error in self.errors:
                    yield Static(f"- {error}", markup=False)
            yield Button("OK", id="error-ok-button", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "error-ok-button":
            self.dismiss()
