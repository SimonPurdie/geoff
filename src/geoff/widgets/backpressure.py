from textual.app import ComposeResult
from textual.widgets import Static, Checkbox, Label
from textual.message import Message
from textual import on

from geoff.config import PromptConfig


class BackpressureWidget(Static):
    DEFAULT_CSS = """
    BackpressureWidget {
        layout: vertical;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    BackpressureWidget .section-title {
        text-style: bold;
        margin-bottom: 1;
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
