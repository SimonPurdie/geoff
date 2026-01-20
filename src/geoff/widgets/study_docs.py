from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Label, Input, Button, Checkbox
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


class StudyDocsWidget(Static):
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

    StudyDocsWidget {
        layout: vertical;
        height: 1fr;
        border: solid $geoff-border;
        background: $geoff-panel-bg;
    }

    StudyDocsWidget .section-title {
        color: $geoff-primary;
        text-style: bold;
        margin-bottom: 1;
    }

    StudyDocsWidget #docs-list {
        height: 1fr;
        overflow-y: auto;
    }

    StudyDocsWidget .doc-row {
        layout: horizontal;
        height: auto;
        align-vertical: middle;
    }

    StudyDocsWidget .doc-input {
        width: 1fr;
        background: #0f172a;
        border: solid $geoff-border;
        padding: 0 1;
    }

    StudyDocsWidget .doc-input:focus {
        border: solid $geoff-primary;
    }

    StudyDocsWidget .remove-btn {
        width: 4;
        min-width: 4;
        margin-left: 1;
        background: $geoff-error;
        color: $geoff-text;
    }

    StudyDocsWidget .remove-btn:hover {
        background: #dc2626;
    }

    StudyDocsWidget #add-doc-btn {
        margin-bottom: 1;
        background: $geoff-secondary;
    }

    StudyDocsWidget #add-doc-btn:hover {
        background: #475569;
    }

    StudyDocsWidget Label {
        color: $geoff-text-muted;
    }

    StudyDocsWidget #breadcrumbs-input-row {
        height: auto;
        align-vertical: middle;
        padding: 0 1 1 1;
    }

    StudyDocsWidget #breadcrumbs-input-row Checkbox {
        min-width: 15;
        height: 1;
        color: $geoff-text-muted;
    }
    
    StudyDocsWidget #breadcrumbs-input-row Checkbox:hover {
        color: $geoff-primary;
    }

    StudyDocsWidget #breadcrumbs-input {
        width: 1fr;
        background: #0f172a;
        border: solid $geoff-border;
        padding: 0 1;
    }

    StudyDocsWidget #breadcrumbs-input:focus {
        border: solid $geoff-primary;
    }
    """

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        with Vertical(id="docs-list"):
            for i, doc in enumerate(self.config.study_docs):
                yield DocRow(doc, i, classes="doc-row", id=f"doc-row-{i}")

            yield Button("+ Add Doc", id="add-doc-btn", variant="primary")

        with Horizontal(id="breadcrumbs-input-row"):
            yield Checkbox(
                "Breadcrumbs",
                value=self.config.breadcrumb_enabled,
                id="breadcrumbs-checkbox",
            )
            yield Input(
                value=self.config.breadcrumbs_file,
                id="breadcrumbs-input",
                placeholder="Path to breadcrumbs file",
            )

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
        breadcrumbs_input = self.query_one("#breadcrumbs-input", Input)
        breadcrumbs_input.value = config.breadcrumbs_file

        breadcrumbs_checkbox = self.query_one("#breadcrumbs-checkbox", Checkbox)
        breadcrumbs_checkbox.value = config.breadcrumb_enabled

        await self.recompose_docs_list()
