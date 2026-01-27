from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Static

from geoff.config_manager import ConfigManager
from geoff.prompt_builder import build_prompt
from geoff.validator import PromptValidator
from geoff.clipboard import copy_to_clipboard
from geoff.messages import ConfigUpdated
from geoff.widgets.study_docs import StudyDocsWidget
from geoff.widgets.task_source import TaskSourceWidget
from geoff.widgets.toolbar import ToolbarWidget
from geoff.widgets.prompt_preview import PromptPreviewWidget
from geoff.widgets.error_modal import ErrorModal


class GeoffApp(App):
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }

    #main-body {
        layout: vertical;
        height: 1fr;
        background: $surface;
        padding: 1;
    }

    #top-row {
        layout: horizontal;
        height: 1fr;
    }

    #bottom-panel {
        height: 10;
        background: $background;
        border-top: solid $primary-background;
    }

    #actions {
        height: auto;
    }

    .section-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }

    #study-docs {
        width: 1fr;
        height: 1fr;
        margin-right: 1;
    }

    #task-source {
        width: 1fr;
        height: 1fr;
        margin-left: 1;
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
            with Horizontal(id="top-row"):
                yield StudyDocsWidget(self.prompt_config, id="study-docs")
                yield TaskSourceWidget(self.prompt_config, id="task-source")

            yield ToolbarWidget(id="actions")

        yield PromptPreviewWidget(self.prompt_config, id="bottom-panel")

    def on_mount(self) -> None:
        self.title = "geoff"
        self.theme = self.prompt_config.theme
        self.watch(self, "theme", self._update_theme_config, init=False)

    def _update_theme_config(self, theme: str) -> None:
        """Update the config when the theme changes."""
        self.prompt_config.theme = theme
        self._save_config()

    @on(ConfigUpdated)
    def handle_config_updated(self) -> None:
        """Handle config updates from child widgets."""
        self.prompt_config.theme = self.theme
        self.query_one(PromptPreviewWidget).update_prompt()
        self._save_config()

    def _save_config(self) -> None:
        """Auto-save config to repo-local .geoff/geoff.yaml."""
        self.prompt_config.theme = self.theme
        try:
            self.config_manager.save_repo_config(self.prompt_config)
        except Exception as e:
            self.notify(f"Failed to save config: {e}", severity="error")

    def on_toolbar_widget_copy_prompt(self, message: ToolbarWidget.CopyPrompt) -> None:
        errors = self.validator.validate(self.prompt_config)
        if errors:
            self.push_screen(ErrorModal(errors))
            return

        prompt = build_prompt(self.prompt_config)
        if copy_to_clipboard(prompt):
            self.notify("Prompt copied to clipboard", severity="information")
        else:
            self.notify("Failed to copy to clipboard", severity="error")

    def on_toolbar_widget_run_once(self, message: ToolbarWidget.RunOnce) -> None:
        errors = self.validator.validate(self.prompt_config)
        if errors:
            self.push_screen(ErrorModal(errors))
            return

        prompt = build_prompt(self.prompt_config)
        self.exit(("run_once", prompt))

    def on_toolbar_widget_run_loop(self, message: ToolbarWidget.RunLoop) -> None:
        errors = self.validator.validate(self.prompt_config)
        if errors:
            self.push_screen(ErrorModal(errors))
            return

        prompt = build_prompt(self.prompt_config)
        self.exit(
            (
                "run_loop",
                prompt,
                self.prompt_config.max_iterations,
                self.prompt_config.max_stuck,
                self.prompt_config.max_frozen,
            )
        )

    async def on_toolbar_widget_reset(self, message: ToolbarWidget.Reset) -> None:
        await self._reset_to_defaults()

    async def _reset_to_defaults(self) -> None:
        """Reset all fields to global config defaults."""
        repo_config_path = self.config_manager.repo_config_path
        if repo_config_path.exists():
            repo_config_path.unlink()

        self.prompt_config = self.config_manager.resolve_config()
        self.theme = self.prompt_config.theme

        # Update all widgets
        await self.query_one(StudyDocsWidget).update_from_config(self.prompt_config)
        self.query_one(TaskSourceWidget).update_from_config(self.prompt_config)

        self.query_one(PromptPreviewWidget).update_prompt(self.prompt_config)
        self.notify("Reset to defaults", severity="information")

    def on_toolbar_widget_quit(self, message: ToolbarWidget.Quit) -> None:
        self.exit()
