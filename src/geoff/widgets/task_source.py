from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Label, Input, TextArea, RadioSet, RadioButton
from textual import on

from geoff.config import PromptConfig
from geoff.messages import ConfigUpdated


class TaskSourceWidget(Static):
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

    TaskSourceWidget {
        layout: vertical;
        height: 1fr;
        border: solid $geoff-border;
        padding: 1;
        background: $geoff-panel-bg;
    }

    TaskSourceWidget .section-title {
        color: $geoff-primary;
        text-style: bold;
        margin-bottom: 1;
    }

    TaskSourceWidget RadioSet {
        layout: vertical;
        height: auto;
        margin-bottom: 1;
    }

    TaskSourceWidget RadioButton {
        color: $geoff-text;
    }

    TaskSourceWidget RadioButton:hover {
        color: $geoff-primary;
    }

    TaskSourceWidget RadioButton:focus {
        background: $geoff-border;
    }

    TaskSourceWidget TextArea {
        height: 1fr;
        border: solid $geoff-border;
        background: #0f172a;
    }

    TaskSourceWidget TextArea:focus {
        border: solid $geoff-primary;
    }

    TaskSourceWidget #tasklist-input-row {
        height: auto;
        align-vertical: middle;
    }

    TaskSourceWidget #tasklist-input-row Label {
        min-width: 15;
    }

    TaskSourceWidget Input {
        width: 1fr;
        background: #0f172a;
        border: solid $geoff-border;
        padding: 0 1;
    }

    TaskSourceWidget Input:focus {
        border: solid $geoff-primary;
    }

    TaskSourceWidget Label {
        color: $geoff-text-muted;
    }
    """

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Label(
            "Task Source (mutually exclusive, required)", classes="section-title"
        )

        with RadioSet(id="mode-radios"):
            yield RadioButton(
                "Tasklist Mode",
                id="mode-tasklist",
                value=(self.config.task_mode == "tasklist"),
            )
            yield RadioButton(
                "One-off Prompt",
                id="mode-oneoff",
                value=(self.config.task_mode == "oneoff"),
            )

        # Tasklist input
        with Horizontal(id="tasklist-input-row"):
            yield Label("Tasklist File:", id="tasklist-label")
            yield Input(
                value=self.config.tasklist_file,
                id="tasklist-input",
                placeholder="Path to tasklist file",
            )

        # One-off prompt input
        yield Label("One-off Prompt:", id="oneoff-label")
        yield TextArea(
            self.config.oneoff_prompt, id="oneoff-input", show_line_numbers=False
        )

    def on_mount(self) -> None:
        # Set initial visibility based on mode
        self.update_visibility()

    def update_visibility(self) -> None:
        is_tasklist = self.config.task_mode == "tasklist"

        self.query_one("#tasklist-input-row").display = is_tasklist
        self.query_one("#tasklist-input").display = is_tasklist

        self.query_one("#oneoff-label").display = not is_tasklist
        self.query_one("#oneoff-input").display = not is_tasklist

    @on(RadioSet.Changed, "#mode-radios")
    def on_mode_changed(self, event: RadioSet.Changed) -> None:
        if event.pressed.id == "mode-tasklist":
            self.config.task_mode = "tasklist"
        elif event.pressed.id == "mode-oneoff":
            self.config.task_mode = "oneoff"

        self.update_visibility()
        self.post_message(ConfigUpdated())

    @on(Input.Changed, "#tasklist-input")
    def on_tasklist_changed(self, event: Input.Changed) -> None:
        self.config.tasklist_file = event.value
        self.post_message(ConfigUpdated())

    @on(TextArea.Changed, "#oneoff-input")
    def on_oneoff_changed(self, event: TextArea.Changed) -> None:
        # event.text_area contains the content of the TextArea
        self.config.oneoff_prompt = event.text_area.text
        self.post_message(ConfigUpdated())

    def update_from_config(self, config: PromptConfig) -> None:
        self.config = config
        self.query_one("#mode-tasklist", RadioButton).value = (
            config.task_mode == "tasklist"
        )
        self.query_one("#mode-oneoff", RadioButton).value = config.task_mode == "oneoff"
        self.query_one("#tasklist-input", Input).value = config.tasklist_file
        self.query_one("#oneoff-input", TextArea).text = config.oneoff_prompt
        self.update_visibility()
