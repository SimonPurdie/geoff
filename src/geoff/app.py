from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Static, Placeholder

from geoff.config_manager import ConfigManager
from geoff.prompt_builder import build_prompt
from geoff.validator import PromptValidator
from geoff.clipboard import copy_to_clipboard
from geoff.widgets.study_docs import StudyDocsWidget
from geoff.widgets.task_source import TaskSourceWidget
from geoff.widgets.backpressure import BackpressureWidget
from geoff.widgets.breadcrumb import BreadcrumbWidget
from geoff.widgets.loop_config import LoopConfigWidget
from geoff.widgets.toolbar import ToolbarWidget
from geoff.widgets.prompt_preview import PromptPreviewWidget


class GeoffApp(App):
    CSS = """
    $geoff-primary: $primary;
    $geoff-secondary: $secondary;

    Screen {
        layout: grid;
        grid-size: 1 3;
        grid-rows: 1 1fr 15; 
    }
    
    #main-body {
        layout: horizontal;
        height: 100%;
        background: $surface;
    }
    
    #left-panel {
        width: 60;
        height: 100%;
        border-right: solid $primary;
        background: $surface;
        padding: 1;
    }
    
    #right-spacer {
        width: 1fr;
        height: 100%;
    }
    
    #bottom-panel {
        border-top: solid $primary;
        height: 100%;
        background: $surface-darken-1;
    }
    """

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.prompt_config = self.config_manager.resolve_config()
        self.validator = PromptValidator()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="main-body"):
            with VerticalScroll(id="left-panel"):
                yield StudyDocsWidget(self.prompt_config, id="study-docs")
                yield TaskSourceWidget(self.prompt_config, id="task-source")
                yield BackpressureWidget(self.prompt_config, id="backpressure")
                yield BreadcrumbWidget(self.prompt_config, id="breadcrumb")
                yield LoopConfigWidget(self.prompt_config, id="loop-config")
                yield ToolbarWidget(id="actions")

            yield Static(" ", id="right-spacer")

        yield PromptPreviewWidget(self.prompt_config, id="bottom-panel")

    def on_mount(self) -> None:
        self.title = "GEOFF - Prompt Constructor"

    def on_config_updated(self) -> None:
        """Handle config updates from child widgets."""
        self.query_one(PromptPreviewWidget).update_prompt()
        # TODO: Auto-save config (Task 21)

    def on_toolbar_widget_copy_prompt(self, message: ToolbarWidget.CopyPrompt) -> None:
        errors = self.validator.validate(self.prompt_config)
        if errors:
            self.notify(f"Validation failed: {'; '.join(errors)}", severity="error")
            return

        prompt = build_prompt(self.prompt_config)
        if copy_to_clipboard(prompt):
            self.notify("Prompt copied to clipboard", severity="information")
        else:
            self.notify("Failed to copy to clipboard", severity="error")

    def on_toolbar_widget_run_once(self, message: ToolbarWidget.RunOnce) -> None:
        self.notify("Run Once not implemented yet")

    def on_toolbar_widget_run_loop(self, message: ToolbarWidget.RunLoop) -> None:
        self.notify("Run Loop not implemented yet")

    def on_toolbar_widget_reset(self, message: ToolbarWidget.Reset) -> None:
        self.notify("Reset not implemented yet")

    def on_toolbar_widget_quit(self, message: ToolbarWidget.Quit) -> None:
        self.exit()
