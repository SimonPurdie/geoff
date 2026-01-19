from textual.app import ComposeResult
from textual.widgets import Static, Checkbox, Label
from textual.message import Message
from textual import on

from geoff.config import PromptConfig


class BreadcrumbWidget(Static):
    DEFAULT_CSS = """
    BreadcrumbWidget {
        layout: vertical;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    BreadcrumbWidget .section-title {
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
        yield Label("Breadcrumb", classes="section-title")
        yield Checkbox(
            "Leave breadcrumbs",
            value=self.config.breadcrumb_enabled,
            id="breadcrumb-checkbox",
        )

    @on(Checkbox.Changed, "#breadcrumb-checkbox")
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.config.breadcrumb_enabled = event.value
        self.post_message(self.ConfigUpdated())
