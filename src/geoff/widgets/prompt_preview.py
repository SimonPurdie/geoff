from textual.widgets import Static
from textual.containers import VerticalScroll
from geoff.config import PromptConfig
from geoff.prompt_builder import build_prompt


class PromptPreviewWidget(VerticalScroll):
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

    PromptPreviewWidget {
        layout: vertical;
        height: 100%;
        background: #0f172a;
        overflow-y: scroll;
    }

    PromptPreviewWidget Static {
        padding: 1;
        color: $geoff-text-muted;
    }
    """

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config_data = config
        self.prompt_text = Static(build_prompt(config))

    def compose(self):
        yield self.prompt_text

    def update_prompt(self):
        self.prompt_text.update(build_prompt(self.config_data))
