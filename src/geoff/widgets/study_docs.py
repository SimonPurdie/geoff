from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
import asyncio
import re
import subprocess
from textual import events
from textual.message import Message
from textual.widgets import Static, Label, Input, Button, Checkbox, Select
from textual import on

from geoff.config import PromptConfig
from geoff.messages import ConfigUpdated


class DocRow(Horizontal):
    def __init__(self, doc: str, index: int, **kwargs):
        super().__init__(**kwargs)
        self.doc = doc
        self.index = index

    def compose(self) -> ComposeResult:
        yield Input(value=self.doc, classes="doc-input", id=f"doc-input-{self.index}")
        yield Button("X", classes="remove-btn", id=f"remove-doc-{self.index}")


class ModelSelect(Select):
    class RequestModels(Message):
        """Request to load available models."""

        pass

    def _request_models(self) -> None:
        self.post_message(self.RequestModels())

    def on_focus(self, event: events.Focus) -> None:
        self._request_models()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self._request_models()


class StudyDocsWidget(Static):
    DEFAULT_CSS = """
    StudyDocsWidget {
        layout: vertical;
        height: 1fr;
        background: $surface;
        padding: 1 2;
    }

    StudyDocsWidget .section-title {
        color: $primary;
        text-style: bold;
        margin-bottom: 1;
    }

    StudyDocsWidget #docs-list {
        height: 1fr;
        overflow-y: auto;
    }

    StudyDocsWidget .doc-row {
        layout: horizontal;
        height: 1;
        align-vertical: middle;
        margin-bottom: 1;
    }

    StudyDocsWidget .doc-input {
        width: 1fr;
        background: $boost;
        border: none;
        padding: 0 1;
        height: 1;
    }
    
    StudyDocsWidget .doc-input:focus {
        border: none;
        text-style: underline;
    }

    StudyDocsWidget Button.remove-btn {
        width: 3 !important;
        min-width: 0 !important;
        height: 1 !important;
        min-height: 0 !important;
        margin: 0 !important;
        margin-left: 1 !important;
        padding: 0 !important;
        background: transparent !important;
        color: $error !important;
        border: none !important;
        text-style: bold;
    }

    StudyDocsWidget Button.remove-btn:hover {
        background: $error !important;
        color: $text !important;
    }

    StudyDocsWidget Button.remove-btn:focus {
        background: transparent !important;
        color: $error !important;
        text-style: bold underline;
    }

    StudyDocsWidget #add-doc-btn {
        margin-top: 1;
        margin-bottom: 2;
        background: transparent;
        color: $primary;
        border: none;
        height: 1;
        min-height: 0;
        width: auto;
        min-width: 10;
        padding: 0;
    }

    StudyDocsWidget #add-doc-btn:hover {
        text-style: underline;
        background: transparent;
    }

    StudyDocsWidget Label {
        color: $text-muted;
    }

    StudyDocsWidget .section-subtitle {
        color: $text-muted;
        text-style: bold;
        margin-right: 1;
        width: auto;
    }

    StudyDocsWidget #breadcrumbs-input-row {
        height: auto;
        align-vertical: middle;
        margin-top: 1;
    }

    StudyDocsWidget #model-input-row {
        height: auto;
        align-vertical: middle;
        margin-top: 1;
    }

    StudyDocsWidget #model-select {
        width: 1fr;
        height: 1;
        margin-left: 1;
        background: $boost;
        border: none;
    }

    StudyDocsWidget #model-select:focus {
        border: none;
        text-style: underline;
    }

    StudyDocsWidget #breadcrumbs-input-row Checkbox {
        width: auto;
        height: 1;
        border: none;
        background: transparent;
        color: $text-muted;
        margin: 0;
        padding: 0;
    }

    StudyDocsWidget #breadcrumbs-input-row Checkbox:hover {
        color: $primary;
    }

    StudyDocsWidget #breadcrumbs-input {
        width: 1fr;
        background: $boost;
        border: none;
        padding: 0 1;
        height: 1;
        margin-left: 1;
    }

    StudyDocsWidget #breadcrumbs-input:focus {
        border: none;
        text-style: underline;
    }
    """

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._models_loaded = False
        self._models_loading = False

    def compose(self) -> ComposeResult:
        yield Label("Orientation / Study Docs", classes="section-title")
        with Vertical(id="docs-list"):
            for i, doc in enumerate(self.config.study_docs):
                yield DocRow(doc, i, classes="doc-row", id=f"doc-row-{i}")

            yield Button("+ Add Doc", id="add-doc-btn", variant="primary")

        with Horizontal(id="model-input-row"):
            yield Label("Model:", classes="section-subtitle")
            yield ModelSelect(
                self._initial_model_options(),
                id="model-select",
                value=self.config.model,
                allow_blank=False,
                compact=True,
            )

        with Horizontal(id="breadcrumbs-input-row"):
            yield Label("Breadcrumbs:", classes="section-subtitle")
            yield Checkbox(
                value=self.config.breadcrumb_enabled,
                id="breadcrumbs-checkbox",
            )
            yield Input(
                value=self.config.breadcrumbs_file,
                id="breadcrumbs-input",
                placeholder="Path to breadcrumbs file",
            )

    def _initial_model_options(self) -> list[tuple[str, str]]:
        options = ["default"]
        if self.config.model and self.config.model not in options:
            options.append(self.config.model)
        return [(model, model) for model in options]

    def _parse_models_output(self, output: str) -> list[str]:
        pattern = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
        models = []
        seen = set()
        for match in pattern.finditer(output):
            model = match.group(0)
            if model not in seen:
                seen.add(model)
                models.append(model)
        return models

    def _fetch_opencode_models(self) -> tuple[list[str], str | None]:
        try:
            result = subprocess.run(
                ["opencode", "models"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            return [], "Opencode command not found"

        output = "\n".join([result.stdout or "", result.stderr or ""])
        models = self._parse_models_output(output)

        if not models and result.returncode != 0:
            return [], "Unable to load Opencode models"

        return models, None

    def _apply_model_options(self, models: list[str]) -> None:
        options = ["default"]
        for model in models:
            if model not in options:
                options.append(model)

        if self.config.model and self.config.model not in options:
            options.append(self.config.model)

        select = self.query_one("#model-select", Select)
        select.set_options([(model, model) for model in options])
        if self.config.model in options:
            select.value = self.config.model

    async def _load_models_if_needed(self) -> None:
        if self._models_loaded or self._models_loading:
            return

        self._models_loading = True
        models, error = await asyncio.to_thread(self._fetch_opencode_models)
        self._models_loading = False

        if error:
            if self.app:
                self.app.notify(error, severity="warning")
            return

        if models:
            self._models_loaded = True
            self._apply_model_options(models)

    @on(Button.Pressed, "#add-doc-btn")
    async def add_doc(self):
        self.config.study_docs.append("docs/SPEC.md")
        self.post_message(ConfigUpdated())
        await self.recompose_docs_list()

    @on(Button.Pressed, ".remove-btn")
    async def remove_doc(self, event: Button.Pressed):
        doc_row = event.button.parent
        if isinstance(doc_row, DocRow):
            index = doc_row.index
            if 0 <= index < len(self.config.study_docs):
                self.config.study_docs.pop(index)
                self.post_message(ConfigUpdated())
                await self.recompose_docs_list()

    @on(Checkbox.Changed, "#breadcrumbs-checkbox")
    def on_breadcrumb_toggled(self, event: Checkbox.Changed):
        self.config.breadcrumb_enabled = event.value
        self.post_message(ConfigUpdated())

    @on(Select.Changed, "#model-select")
    def on_model_changed(self, event: Select.Changed):
        if event.value:
            self.config.model = str(event.value)
            self.post_message(ConfigUpdated())

    @on(ModelSelect.RequestModels)
    async def on_model_requested(self) -> None:
        await self._load_models_if_needed()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "breadcrumbs-input":
            self.config.breadcrumbs_file = event.value
            self.post_message(ConfigUpdated())
        elif event.input.id and event.input.id.startswith("doc-input-"):
            doc_row = event.input.parent
            if isinstance(doc_row, DocRow):
                index = doc_row.index
                if 0 <= index < len(self.config.study_docs):
                    self.config.study_docs[index] = event.value
                    self.post_message(ConfigUpdated())

    async def recompose_docs_list(self):
        docs_list = self.query_one("#docs-list", Vertical)
        # Remove all children except the button (which is last)
        # But wait, Button is INSIDE docs-list in my new compose method?
        # Yes:
        # with Vertical(id="docs-list"):
        #     ... rows ...
        #     yield Button

        # So I should clear all and rebuild all.
        await docs_list.remove_children()

        for i, doc in enumerate(self.config.study_docs):
            await docs_list.mount(DocRow(doc, i, classes="doc-row", id=f"doc-row-{i}"))

        await docs_list.mount(Button("+ Add Doc", id="add-doc-btn", variant="primary"))

    async def update_from_config(self, config: PromptConfig) -> None:
        self.config = config
        model_select = self.query_one("#model-select", Select)
        existing_values = [
            value for _, value in getattr(model_select, "_options", [])
        ]
        if not existing_values:
            self._apply_model_options([])
        elif config.model not in existing_values:
            models = [value for value in existing_values if value != "default"]
            self._apply_model_options(models)
        model_select.value = config.model
        breadcrumbs_input = self.query_one("#breadcrumbs-input", Input)
        breadcrumbs_input.value = config.breadcrumbs_file

        breadcrumbs_checkbox = self.query_one("#breadcrumbs-checkbox", Checkbox)
        breadcrumbs_checkbox.value = config.breadcrumb_enabled

        await self.recompose_docs_list()
