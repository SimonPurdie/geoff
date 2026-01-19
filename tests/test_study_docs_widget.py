import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input
from geoff.config import PromptConfig
from geoff.widgets.study_docs import StudyDocsWidget, DocRow


class StudyDocsApp(App):
    CSS = """
    $geoff-primary: blue;
    $geoff-secondary: green;
    """

    def __init__(self, config):
        super().__init__()
        self.config_obj = config

    def compose(self) -> ComposeResult:
        yield StudyDocsWidget(self.config_obj)


@pytest.mark.asyncio
async def test_study_docs_add_remove():
    config = PromptConfig(study_docs=["doc1.md"])
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)

        # Check initial state
        assert len(widget.query(DocRow)) == 1
        assert widget.query_one("Input.doc-input").value == "doc1.md"

        # Add a doc
        await pilot.click("#add-doc-btn")
        # Wait for messages to process
        await pilot.pause()

        assert len(widget.query(DocRow)) == 2
        assert len(config.study_docs) == 2

        # Remove the first doc (doc1.md)
        # Indices are re-assigned in recompose_docs_list: 0 and 1
        await pilot.click("#remove-doc-0")
        await pilot.pause()

        assert len(widget.query(DocRow)) == 1
        assert len(config.study_docs) == 1
        # The remaining doc should be the one added (default is docs/SPEC.md usually,
        # but let's check what I implemented in add_doc: "docs/SPEC.md" or "docs/NEW_DOC.md"?)
        # My implementation: self.config.study_docs.append("docs/SPEC.md")
        assert config.study_docs[0] == "docs/SPEC.md"


@pytest.mark.asyncio
async def test_study_docs_edit():
    config = PromptConfig(study_docs=["doc1.md"])
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        # Edit doc
        input_widget = app.query_one("#doc-input-0", Input)

        # Programmatic value change doesn't always trigger events in Textual depending on version,
        # so we manually post the message to be sure we are testing the handler logic.
        input_widget.post_message(Input.Changed(input_widget, "new_doc.md"))
        await pilot.pause()

        assert config.study_docs[0] == "new_doc.md"

        # Edit breadcrumbs
        bc_input = app.query_one("#breadcrumbs-input", Input)
        bc_input.post_message(Input.Changed(bc_input, "new_bread.md"))
        await pilot.pause()

        assert config.breadcrumbs_file == "new_bread.md"
