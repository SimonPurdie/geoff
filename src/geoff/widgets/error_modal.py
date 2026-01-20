from typing import List

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static


class ErrorModal(ModalScreen[None]):
    DEFAULT_CSS = """
    ErrorModal {
        align: center middle;
    }

    ErrorModal > Container {
        width: 60;
        max-height: 20;
        border: thick $error;
        background: $surface;
        padding: 1;
    }

    #error-title {
        color: $error;
        text-align: center;
        margin-bottom: 1;
    }

    #error-content {
        height: auto;
        max-height: 14;
        margin-bottom: 1;
    }

    #error-ok-button {
        width: 100%;
        margin-top: 1;
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
                    yield Static(f"- {error}")
            yield Button("OK", id="error-ok-button", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "error-ok-button":
            self.dismiss()
