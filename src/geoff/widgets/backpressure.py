from textual.app import ComposeResult
from textual.widgets import Static, Checkbox, Label
from textual.message import Message
from textual import on

from geoff.config import PromptConfig


class BackpressureWidget(Static):
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

    BackpressureWidget {
        layout: vertical;
        height: auto;
        border: solid $geoff-border;
        padding: 1;
        margin-bottom: 1;
        background: $geoff-panel-bg;
    }

    BackpressureWidget .section-title {
        color: $geoff-primary;
        text-style: bold;
        margin-bottom: 1;
    }

    BackpressureWidget Checkbox {
        color: $geoff-text;
    }

    BackpressureWidget Checkbox:hover {
        color: $geoff-primary;
    }

    BackpressureWidget Checkbox Box {
        border: solid $geoff-border;
    }

    BackpressureWidget Checkbox:focus {
        background: $geoff-border;
    }
    """

    class ConfigUpdated(Message):
        """Message sent when config is updated."""

        pass

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Label("Backpressure", classes="section-title")
        yield Checkbox(
            "Enforce tests & commit",
            value=self.config.backpressure_enabled,
            id="backpressure-checkbox",
        )

    @on(Checkbox.Changed, "#backpressure-checkbox")
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.config.backpressure_enabled = event.value
        self.post_message(self.ConfigUpdated())
