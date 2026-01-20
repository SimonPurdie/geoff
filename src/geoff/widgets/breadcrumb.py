from textual.app import ComposeResult
from textual.widgets import Static, Checkbox, Label
from textual import on

from geoff.config import PromptConfig
from geoff.messages import ConfigUpdated


class BreadcrumbWidget(Static):
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

    BreadcrumbWidget {
        layout: vertical;
        height: auto;
        border: solid $geoff-border;
        padding: 1;
        margin-bottom: 1;
        background: $geoff-panel-bg;
    }

    BreadcrumbWidget .section-title {
        color: $geoff-primary;
        text-style: bold;
        margin-bottom: 1;
    }

    BreadcrumbWidget Checkbox {
        color: $geoff-text;
    }

    BreadcrumbWidget Checkbox:hover {
        color: $geoff-primary;
    }

    BreadcrumbWidget Checkbox Box {
        border: solid $geoff-border;
    }

    BreadcrumbWidget Checkbox:focus {
        background: $geoff-border;
    }
    """

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
        self.post_message(ConfigUpdated())

    def update_from_config(self, config: PromptConfig) -> None:
        self.config = config
        self.query_one(
            "#breadcrumb-checkbox", Checkbox
        ).value = config.breadcrumb_enabled
