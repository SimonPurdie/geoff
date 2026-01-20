from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Label, Input, Button
from textual.message import Message
from textual import on

from geoff.config import PromptConfig


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
        height: auto;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }

    StudyDocsWidget .section-title {
        text-style: bold;
        margin-bottom: 1;
    }

    StudyDocsWidget .doc-row {
        layout: horizontal;
        height: auto;
        margin-bottom: 1;
        align-vertical: middle;
    }

    StudyDocsWidget .doc-input {
        width: 1fr;
    }

    StudyDocsWidget .remove-btn {
        width: 4;
        min-width: 4;
        margin-left: 1;
        background: $error;
        color: $text;
    }
    
    StudyDocsWidget #add-doc-btn {
        margin-bottom: 1;
        background: $secondary;
    }
    """

    class ConfigUpdated(Message):
        """Message sent when config is updated."""

        pass

    def __init__(self, config: PromptConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def compose(self) -> ComposeResult:
        yield Label("Orientation / Study Docs", classes="section-title")

        yield Label("Docs:")
        with Vertical(id="docs-list"):
            for i, doc in enumerate(self.config.study_docs):
                yield DocRow(doc, i, classes="doc-row", id=f"doc-row-{i}")

        yield Button("+ Add Doc", id="add-doc-btn", variant="primary")

        yield Label("Breadcrumbs:")
        yield Input(
            value=self.config.breadcrumbs_file,
            id="breadcrumbs-input",
            placeholder="Path to breadcrumbs file",
        )

    @on(Button.Pressed, "#add-doc-btn")
    async def add_doc(self):
        self.config.study_docs.append("docs/SPEC.md")
        self.post_message(self.ConfigUpdated())
        await self.recompose_docs_list()

    @on(Button.Pressed, ".remove-btn")
    async def remove_doc(self, event: Button.Pressed):
        doc_row = event.button.parent
        if isinstance(doc_row, DocRow):
            index = doc_row.index
            if 0 <= index < len(self.config.study_docs):
                self.config.study_docs.pop(index)
                self.post_message(self.ConfigUpdated())
                await self.recompose_docs_list()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "breadcrumbs-input":
            self.config.breadcrumbs_file = event.value
            self.post_message(self.ConfigUpdated())
        elif event.input.id and event.input.id.startswith("doc-input-"):
            doc_row = event.input.parent
            if isinstance(doc_row, DocRow):
                index = doc_row.index
                if 0 <= index < len(self.config.study_docs):
                    self.config.study_docs[index] = event.value
                    self.post_message(self.ConfigUpdated())

    async def recompose_docs_list(self):
        docs_list = self.query_one("#docs-list", Vertical)
        await docs_list.remove_children()

        for i, doc in enumerate(self.config.study_docs):
            await docs_list.mount(DocRow(doc, i, classes="doc-row", id=f"doc-row-{i}"))

    def update_from_config(self, config: PromptConfig) -> None:
        self.config = config
        breadcrumbs_input = self.query_one("#breadcrumbs-input", Input)
        breadcrumbs_input.value = config.breadcrumbs_file
