import pytest
from hypothesis import given, settings, strategies as st
from textual.app import App, ComposeResult
from textual.widgets import Static
from geoff.config import PromptConfig
from geoff.widgets.prompt_preview import PromptPreviewWidget


def filepath_strategy(min_size=1, max_size=50):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


def text_strategy(min_size=1, max_size=100):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.,!?\n"
    return st.text(
        min_size=min_size, max_size=max_size, alphabet=st.sampled_from(list(alphabet))
    )


class PreviewApp(App):
    def __init__(self, config):
        super().__init__()
        self.config_obj = config

    def compose(self) -> ComposeResult:
        yield PromptPreviewWidget(self.config_obj)


@pytest.mark.asyncio
async def test_prompt_preview_update():
    config = PromptConfig(
        study_docs=["doc1.md"],
        task_mode="oneoff",
        oneoff_prompt="Do something.",
        backpressure_enabled=False,
        breadcrumb_enabled=False,
    )
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)

        # Check initial content
        # Static.render() returns the content to be displayed
        initial_text = str(widget.prompt_text.render())

        assert "study doc1.md" in initial_text

        assert "Do something." in initial_text

        # Update config
        config.oneoff_prompt = "Do something else."
        widget.update_prompt()
        await pilot.pause()

        updated_text = str(widget.prompt_text.render())
        assert "Do something else." in updated_text


@given(
    study_docs=st.lists(filepath_strategy(), max_size=5),
    breadcrumbs_file=filepath_strategy(),
    tasklist_file=filepath_strategy(),
    backpressure_enabled=st.booleans(),
    breadcrumb_enabled=st.booleans(),
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
)
@settings(max_examples=30)
@pytest.mark.asyncio
async def test_prompt_preview_initial_state(
    study_docs,
    breadcrumbs_file,
    tasklist_file,
    backpressure_enabled,
    breadcrumb_enabled,
    task_mode,
):
    config = PromptConfig(
        study_docs=study_docs,
        breadcrumbs_file=breadcrumbs_file,
        tasklist_file=tasklist_file,
        backpressure_enabled=backpressure_enabled,
        breadcrumb_enabled=breadcrumb_enabled,
        task_mode=task_mode,
    )
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)
        prompt_content = str(widget.prompt_text.render())

        for doc in study_docs:
            if doc:
                assert f"study {doc}" in prompt_content

        if breadcrumb_enabled and breadcrumbs_file:
            assert f"check {breadcrumbs_file}" in prompt_content
        else:
            assert "check " not in prompt_content

        if backpressure_enabled:
            assert "IMPORTANT:" in prompt_content
        else:
            assert "IMPORTANT:" not in prompt_content


@given(
    initial_study_docs=st.lists(filepath_strategy(), max_size=3),
    new_study_docs=st.lists(filepath_strategy(), max_size=3),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_prompt_preview_study_docs_update(initial_study_docs, new_study_docs):
    config = PromptConfig(study_docs=list(initial_study_docs))
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)

        initial_content = str(widget.prompt_text.render())
        for doc in initial_study_docs:
            if doc:
                assert f"study {doc}" in initial_content

        config.study_docs = list(new_study_docs)
        widget.update_prompt()
        await pilot.pause()

        updated_content = str(widget.prompt_text.render())
        for doc in new_study_docs:
            if doc:
                assert f"study {doc}" in updated_content


@given(
    initial_backpressure=st.booleans(),
    new_backpressure=st.booleans(),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_prompt_preview_backpressure_update(
    initial_backpressure, new_backpressure
):
    config = PromptConfig(
        backpressure_enabled=initial_backpressure,
        task_mode="oneoff",
        oneoff_prompt="test prompt",
    )
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)

        initial_content = str(widget.prompt_text.render())
        if initial_backpressure:
            assert "IMPORTANT:" in initial_content
        else:
            assert "IMPORTANT:" not in initial_content

        config.backpressure_enabled = new_backpressure
        widget.update_prompt()
        await pilot.pause()

        updated_content = str(widget.prompt_text.render())
        if new_backpressure:
            assert "IMPORTANT:" in updated_content
        else:
            assert "IMPORTANT:" not in updated_content


@given(
    initial_breadcrumb=st.booleans(),
    new_breadcrumb=st.booleans(),
    breadcrumbs_file=filepath_strategy(),
)
@settings(max_examples=20)
@pytest.mark.asyncio
async def test_prompt_preview_breadcrumb_update(
    initial_breadcrumb, new_breadcrumb, breadcrumbs_file
):
    config = PromptConfig(
        breadcrumb_enabled=initial_breadcrumb,
        breadcrumbs_file=breadcrumbs_file,
        task_mode="oneoff",
        oneoff_prompt="test prompt",
    )
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)

        initial_content = str(widget.prompt_text.render())
        if initial_breadcrumb and breadcrumbs_file:
            assert f"check {breadcrumbs_file}" in initial_content
        else:
            assert "check " not in initial_content

        config.breadcrumb_enabled = new_breadcrumb
        widget.update_prompt()
        await pilot.pause()

        updated_content = str(widget.prompt_text.render())
        if new_breadcrumb and breadcrumbs_file:
            assert f"check {breadcrumbs_file}" in updated_content
        else:
            assert "check " not in updated_content


@given(
    task_mode=st.sampled_from(["tasklist", "oneoff"]),
    tasklist_file=filepath_strategy(),
    oneoff_prompt=text_strategy(),
)
@settings(max_examples=30)
@pytest.mark.asyncio
async def test_prompt_preview_task_mode_switch(task_mode, tasklist_file, oneoff_prompt):
    config = PromptConfig(
        task_mode=task_mode,
        tasklist_file=tasklist_file,
        oneoff_prompt=oneoff_prompt,
    )
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)
        prompt_content = str(widget.prompt_text.render())

        if task_mode == "tasklist":
            assert (
                f"study {tasklist_file} and pick the most important thing to do"
                in prompt_content
            )
            assert f"update {tasklist_file} when the task is done" in prompt_content
            else:
            assert oneoff_prompt.strip() in prompt_content
            assert "pick the most important thing to do" not in prompt_content


@given(
    initial_mode=st.sampled_from(["tasklist", "oneoff"]),
    new_mode=st.sampled_from(["tasklist", "oneoff"]),
    tasklist_file=filepath_strategy(),
    oneoff_prompt=text_strategy(),
)
@settings(max_examples=20, deadline=None)
@pytest.mark.asyncio
async def test_prompt_preview_mode_toggle(
    initial_mode, new_mode, tasklist_file, oneoff_prompt
):
    config = PromptConfig(
        task_mode=initial_mode,
        tasklist_file=tasklist_file,
        oneoff_prompt=oneoff_prompt,
    )
    app = PreviewApp(config)

    async with app.run_test() as pilot:
        widget = app.query_one(PromptPreviewWidget)

        config.task_mode = new_mode
        widget.update_prompt()
        await pilot.pause()

        prompt_content = str(widget.prompt_text.render())
        if new_mode == "tasklist":
            assert (
                f"study {tasklist_file} and pick the most important thing to do"
                in prompt_content
            )
            assert f"update {tasklist_file} when the task is done" in prompt_content
        else:
            assert "pick the most important thing to do" not in prompt_content
            assert "update " not in prompt_content
