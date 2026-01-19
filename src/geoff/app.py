from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Static, Placeholder

from geoff.config_manager import ConfigManager
from geoff.widgets.study_docs import StudyDocsWidget


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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="main-body"):
            with VerticalScroll(id="left-panel"):
                yield StudyDocsWidget(self.prompt_config, id="study-docs")
                yield Placeholder("Task Source", id="task-source", classes="panel-item")
                yield Placeholder(
                    "Backpressure", id="backpressure", classes="panel-item"
                )
                yield Placeholder("Breadcrumb", id="breadcrumb", classes="panel-item")
                yield Placeholder(
                    "Loop Configuration", id="loop-config", classes="panel-item"
                )
                yield Placeholder("Actions", id="actions", classes="panel-item")

            yield Static(" ", id="right-spacer")

        yield Placeholder("Effective Prompt", id="bottom-panel")

    def on_mount(self) -> None:
        self.title = "GEOFF - Prompt Constructor"
