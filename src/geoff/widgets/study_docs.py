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
        height: auto;
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

    StudyDocsWidget .remove-btn {
        width: 4;
        min-width: 4;
        margin-left: 1;
        background: $error;
        color: $text;
        border: none;
        height: 1;
    }

    StudyDocsWidget .remove-btn:hover {
        background: $error-darken-1;
        color: $text;
    }

    StudyDocsWidget #add-doc-btn {
        margin-top: 1;
        margin-bottom: 2;
        background: transparent;
        color: $primary;
        border: none;
        height: 1;
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
        padding-top: 1;
        border-top: solid $primary-background;
        margin-top: 1;
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

    def compose(self) -> ComposeResult:
        yield Label("Orientation / Study Docs", classes="section-title")
        with Vertical(id="docs-list"):
            for i, doc in enumerate(self.config.study_docs):
                yield DocRow(doc, i, classes="doc-row", id=f"doc-row-{i}")

            yield Button("+ Add Doc", id="add-doc-btn", variant="primary")

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
