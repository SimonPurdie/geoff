from textual.app import ComposeResult
from textual.widgets import Static, Label, Input
from textual.containers import Horizontal
from textual.message import Message
from textual import on
from textual.validation import Number, Function

from geoff.config import PromptConfig


class LoopConfigWidget(Static):
    DEFAULT_CSS = """
    LoopConfigWidget {
        layout: vertical;
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    LoopConfigWidget .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    LoopConfigWidget .input-row {
        height: auto;
        align-vertical: middle;
        margin-bottom: 1;
    }

    LoopConfigWidget Label {
        margin-right: 1;
        min-width: 15;
    }

    LoopConfigWidget Input {
        width: 10;
    }

    #infinity-indicator {
        margin-left: 1;
        color: $accent;
        text-style: bold;
        width: 3;
    }
    
    .hidden {
        display: none;
    }
    """

    class ConfigUpdated(Message):
        """Message sent when config is updated."""

        pass

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Label("Loop Configuration", classes="section-title")

        with Horizontal(classes="input-row"):
            yield Label("Max iterations:")
            yield Input(
                str(self.config.max_iterations),
                id="max-iterations",
                validators=[
                    Number(minimum=0),
                    Function(lambda v: v.isdigit(), "Must be an integer"),
                ],
            )
            # Infinity symbol: ∞
            yield Label("∞", id="infinity-indicator")

        with Horizontal(classes="input-row"):
            yield Label("Max stuck:")
            yield Input(
                str(self.config.max_stuck),
                id="max-stuck",
                validators=[
                    Number(minimum=0),
                    Function(lambda v: v.isdigit(), "Must be an integer"),
                ],
            )

    def on_mount(self) -> None:
        self._update_infinity_indicator()

    @on(Input.Changed, "#max-iterations")
    def on_max_iterations_changed(self, event: Input.Changed) -> None:
        if event.validation_result and event.validation_result.is_valid:
            try:
                val = int(event.value)
                self.config.max_iterations = val
                self._update_infinity_indicator()
                self.post_message(self.ConfigUpdated())
            except ValueError:
                pass  # Should be caught by validator but just in case

    @on(Input.Changed, "#max-stuck")
    def on_max_stuck_changed(self, event: Input.Changed) -> None:
        if event.validation_result and event.validation_result.is_valid:
            try:
                val = int(event.value)
                self.config.max_stuck = val
                self.post_message(self.ConfigUpdated())
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
