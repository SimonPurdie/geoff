import pytest
from textual.app import App, ComposeResult
from geoff.config import PromptConfig
from geoff.widgets.prompt_preview import PromptPreviewWidget


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
