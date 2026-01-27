from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import (
    Static,
    Label,
    Input,
    TextArea,
    RadioSet,
    RadioButton,
    Checkbox,
)
from textual import on
from textual.validation import Number, Function

from geoff.config import PromptConfig
from geoff.messages import ConfigUpdated


class TaskSourceWidget(Static):
    DEFAULT_CSS = """
    TaskSourceWidget {
        layout: vertical;
        height: 1fr;
        background: $surface;
        padding: 1 2;
    }

    TaskSourceWidget .section-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }

    TaskSourceWidget RadioSet {
        layout: vertical;
        height: auto;
        margin-bottom: 1;
        background: transparent;
        border: none;
    }
    
    TaskSourceWidget RadioSet:focus {
        border: none;
    }
    
    TaskSourceWidget #input-container {
        height: 1fr;
    }

    TaskSourceWidget RadioButton {
        color: $text;
        background: transparent;
        border: none;
        padding: 0;
    }

    TaskSourceWidget RadioButton:hover {
        color: $primary;
        background: transparent;
    }

    TaskSourceWidget RadioButton.-on {
        color: $primary;
    }

    TaskSourceWidget TextArea {
        height: 1fr;
        border: none;
        background: $boost;
        margin-left: 2;
    }

    TaskSourceWidget TextArea:focus {
        border: none;
    }

    TaskSourceWidget #tasklist-input-row {
        height: auto;
        align-vertical: middle;
        margin-left: 2;
    }

    TaskSourceWidget #tasklist-input-row Label {
        min-width: 15;
    }

    TaskSourceWidget Input {
        width: 1fr;
        background: $boost;
        border: none;
        padding: 0 1;
        height: 1;
    }

    TaskSourceWidget Input:focus {
        border: none;
        text-style: underline;
    }

    TaskSourceWidget Label {
        color: $text-muted;
    }

    TaskSourceWidget .loop-config-row Label {
        margin-right: 1;
    }

    TaskSourceWidget .small-input {
        width: 6;
        background: $boost;
        border: none;
        text-align: center;
    }
    
    TaskSourceWidget #infinity-indicator {
        margin-left: 1;
        color: $secondary;
        text-style: bold;
        width: 3;
    }

    TaskSourceWidget .hidden {
        display: none;
    }

    TaskSourceWidget Checkbox {
        width: auto;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
        margin: 0;
        padding: 0;
    }

    TaskSourceWidget Checkbox:hover {
        color: $primary;
        background: transparent;
        border: none;
    }
    
    TaskSourceWidget Checkbox:focus {
        border: none;
        background: transparent;
    }

    TaskSourceWidget .backpressure-row {
        height: auto;
        align-vertical: middle;
        margin-top: 1;
    }

    TaskSourceWidget .loop-config-row {
        height: auto;
        align-vertical: middle;
        margin-top: 1;
    }

    TaskSourceWidget .section-subtitle {
        color: $text-muted;
        text-style: bold;
        margin: 0;
        margin-right: 1;
        width: auto;
    }
    """

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Label("Task Configuration", classes="section-title")

        # Container for variable inputs to ensure consistent spacing
        with Vertical(id="input-container"):
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

        with Horizontal(classes="backpressure-row"):
            yield Label("Backpressure:", classes="section-subtitle")
            yield Checkbox(
                value=self.config.backpressure_enabled,
                id="backpressure-checkbox",
            )

        # Loop Config
        with Horizontal(classes="loop-config-row"):
            yield Label("Max Runs:")
            yield Input(
                str(self.config.max_iterations),
                id="max-iterations",
                classes="small-input",
                validators=[
                    Number(minimum=0),
                    Function(lambda v: v.isdigit(), "Must be an integer"),
                ],
            )
            # Infinity symbol: ∞
            yield Label("∞", id="infinity-indicator")

            yield Label("  Stuck:")
            yield Input(
                str(self.config.max_stuck),
                id="max-stuck",
                classes="small-input",
                validators=[
                    Number(minimum=0),
                    Function(lambda v: v.isdigit(), "Must be an integer"),
                ],
            )

            yield Label("  Frozen:")
            yield Input(
                str(self.config.max_frozen),
                id="max-frozen",
                classes="small-input",
                validators=[
                    Number(minimum=0),
                    Function(lambda v: v.isdigit(), "Must be an integer"),
                ],
            )

    def on_mount(self) -> None:
        # Set initial visibility based on mode
        self.update_visibility()
        self._update_infinity_indicator()

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

    @on(Checkbox.Changed, "#backpressure-checkbox")
    def on_backpressure_changed(self, event: Checkbox.Changed) -> None:
        self.config.backpressure_enabled = event.value
        self.post_message(ConfigUpdated())

    @on(Input.Changed, "#max-iterations")
    def on_max_iterations_changed(self, event: Input.Changed) -> None:
        if event.validation_result and event.validation_result.is_valid:
            try:
                val = int(event.value)
                self.config.max_iterations = val
                self._update_infinity_indicator()
                self.post_message(ConfigUpdated())
            except ValueError:
                pass

    @on(Input.Changed, "#max-stuck")
    def on_max_stuck_changed(self, event: Input.Changed) -> None:
        if event.validation_result and event.validation_result.is_valid:
            try:
                val = int(event.value)
                self.config.max_stuck = val
                self.post_message(ConfigUpdated())
            except ValueError:
                pass

    @on(Input.Changed, "#max-frozen")
    def on_max_frozen_changed(self, event: Input.Changed) -> None:
        if event.validation_result and event.validation_result.is_valid:
            try:
                val = int(event.value)
                self.config.max_frozen = val
                self.post_message(ConfigUpdated())
            except ValueError:
                pass

    def _update_infinity_indicator(self) -> None:
        indicator = self.query_one("#infinity-indicator", Label)
        try:
            val = int(self.query_one("#max-iterations", Input).value)
            if val == 0:
                indicator.remove_class("hidden")
            else:
                indicator.add_class("hidden")
        except ValueError:
            indicator.add_class("hidden")

    def update_from_config(self, config: PromptConfig) -> None:
        self.config = config
        self.query_one("#mode-tasklist", RadioButton).value = (
            config.task_mode == "tasklist"
        )
        self.query_one("#mode-oneoff", RadioButton).value = config.task_mode == "oneoff"
        self.query_one("#tasklist-input", Input).value = config.tasklist_file
        self.query_one("#oneoff-input", TextArea).text = config.oneoff_prompt

        self.query_one(
            "#backpressure-checkbox", Checkbox
        ).value = config.backpressure_enabled
        self.query_one("#max-iterations", Input).value = str(config.max_iterations)
        self.query_one("#max-stuck", Input).value = str(config.max_stuck)
        self.query_one("#max-frozen", Input).value = str(config.max_frozen)

        self.update_visibility()
        self._update_infinity_indicator()
