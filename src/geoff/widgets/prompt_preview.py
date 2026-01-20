from textual.widgets import Static
from textual.containers import VerticalScroll
from geoff.config import PromptConfig
from geoff.prompt_builder import build_prompt


class PromptPreviewWidget(VerticalScroll):
    DEFAULT_CSS = """
    PromptPreviewWidget {
        layout: vertical;
        height: 100%;
        background: $background;
        overflow-y: scroll;
    }

    PromptPreviewWidget Static {
        padding: 1;
        color: $text-muted;
    }
    """

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config_data = config
        self.prompt_text = Static(build_prompt(config))

    def compose(self):
        yield self.prompt_text

    def update_prompt(self, config: PromptConfig | None = None):
        if config:
            self.config_data = config
        self.prompt_text.update(build_prompt(self.config_data))
