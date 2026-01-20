import pytest
from hypothesis import given, settings, strategies as st
from textual.app import App, ComposeResult
from textual.widgets import Input, Checkbox
from textual.containers import Vertical
from geoff.config import PromptConfig
from geoff.widgets.study_docs import StudyDocsWidget, DocRow


def filepath_strategy(min_size=1, max_size=50):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


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


@given(
    study_docs=st.lists(filepath_strategy(), max_size=5),
    breadcrumbs_file=filepath_strategy(),
    breadcrumb_enabled=st.booleans(),
)
@settings(max_examples=30)
@pytest.mark.asyncio
async def test_study_docs_initial_state(
    study_docs, breadcrumbs_file, breadcrumb_enabled
):
    config = PromptConfig(
        study_docs=study_docs,
        breadcrumbs_file=breadcrumbs_file,
        breadcrumb_enabled=breadcrumb_enabled,
    )
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)

        assert len(widget.query(DocRow)) == len(study_docs)

        for i, expected_doc in enumerate(study_docs):
            input_widget = widget.query_one(f"#doc-input-{i}", Input)
            assert input_widget.value == expected_doc

        bc_input = widget.query_one("#breadcrumbs-input", Input)
        assert bc_input.value == breadcrumbs_file

        bc_checkbox = widget.query_one("#breadcrumbs-checkbox", Checkbox)
        assert bc_checkbox.value == breadcrumb_enabled


@given(
    initial_docs=st.lists(filepath_strategy(), max_size=3),
    new_docs=st.lists(filepath_strategy(), max_size=3),
    initial_bc_enabled=st.booleans(),
    new_bc_enabled=st.booleans(),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_study_docs_update_from_config(
    initial_docs, new_docs, initial_bc_enabled, new_bc_enabled
):
    config = PromptConfig(
        study_docs=initial_docs, breadcrumb_enabled=initial_bc_enabled
    )
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)

        new_config = PromptConfig(
            study_docs=new_docs, breadcrumb_enabled=new_bc_enabled
        )
        await widget.update_from_config(new_config)

        assert len(widget.query(DocRow)) == len(new_docs)

        for i, expected_doc in enumerate(new_docs):
            input_widget = widget.query_one(f"#doc-input-{i}", Input)
            assert input_widget.value == expected_doc

        bc_checkbox = widget.query_one("#breadcrumbs-checkbox", Checkbox)
        assert bc_checkbox.value == new_bc_enabled


@given(
    initial_breadcrumbs=filepath_strategy(),
    new_breadcrumbs=filepath_strategy(),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_study_docs_breadcrumbs_update(initial_breadcrumbs, new_breadcrumbs):
    config = PromptConfig(breadcrumbs_file=initial_breadcrumbs)
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)

        new_config = PromptConfig(breadcrumbs_file=new_breadcrumbs)
        await widget.update_from_config(new_config)

        bc_input = widget.query_one("#breadcrumbs-input", Input)
        assert bc_input.value == new_breadcrumbs


@given(
    study_docs=st.lists(filepath_strategy(), max_size=3),
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_study_docs_add_remove_property(study_docs):
    config = PromptConfig(study_docs=list(study_docs))
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)
        initial_count = len(widget.query(DocRow))

        await pilot.click("#add-doc-btn")
        await pilot.pause()

        new_count = len(widget.query(DocRow))
        assert new_count == initial_count + 1
        expected_docs = len(study_docs) + 1
        assert len(config.study_docs) == expected_docs, (
            f"Expected {expected_docs} docs, got {config.study_docs}"
        )

        if new_count > 0:
            await pilot.click("#remove-doc-0")
            await pilot.pause()

            final_count = len(widget.query(DocRow))
            assert final_count == initial_count


@pytest.mark.asyncio
async def test_study_docs_add_remove():
    config = PromptConfig(study_docs=["doc1.md"])
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)

        # Check initial state
        assert len(widget.query(DocRow)) == 1
        assert widget.query_one("#doc-input-0", Input).value == "doc1.md"

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
        # The remaining doc should be the one added
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


@given(
    initial_enabled=st.booleans(), toggle_times=st.integers(min_value=0, max_value=3)
)
@settings(max_examples=15, deadline=None)
@pytest.mark.asyncio
async def test_breadcrumb_toggle_property(initial_enabled, toggle_times):
    config = PromptConfig(breadcrumb_enabled=initial_enabled)
    app = StudyDocsApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(StudyDocsWidget)
        checkbox = widget.query_one("#breadcrumbs-checkbox", Checkbox)

        expected = initial_enabled
        for _ in range(toggle_times):
            await pilot.click("#breadcrumbs-checkbox")
            await pilot.pause()
            expected = not expected
            assert checkbox.value == expected
            assert config.breadcrumb_enabled == expected
