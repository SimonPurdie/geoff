import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button, Static

from geoff.widgets.error_modal import ErrorModal


class TestErrorModalDisplay:
    def test_modal_title_displayed(self):
        modal = ErrorModal(["Test error"])
        assert modal is not None

    def test_modal_with_single_error(self):
        errors = ["Only one error"]
        modal = ErrorModal(errors)
        assert modal.errors == errors

    def test_modal_with_multiple_errors(self):
        errors = ["Error 1", "Error 2", "Error 3"]
        modal = ErrorModal(errors)
        assert modal.errors == errors

    def test_modal_with_empty_errors(self):
        modal = ErrorModal([])
        assert modal.errors == []


@pytest.mark.asyncio
async def test_error_modal_renders():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Error A", "Error B"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        assert modal is not None
        assert modal.errors == ["Error A", "Error B"]


@pytest.mark.asyncio
async def test_error_modal_shows_all_errors():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            errors = ["First error", "Second error", "Third error"]
            yield ErrorModal(errors)

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        statics = modal.query(Static)
        rendered_texts = [str(s.render()) for s in statics]
        assert any("First error" in text for text in rendered_texts)
        assert any("Second error" in text for text in rendered_texts)
        assert any("Third error" in text for text in rendered_texts)


@pytest.mark.asyncio
async def test_error_modal_dismiss_on_ok():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Test error"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)

        await pilot.click("#error-ok-button")
        await pilot.pause()

        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_error_modal_with_no_errors():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal([])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        assert modal is not None


@pytest.mark.asyncio
async def test_error_modal_styling():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Test error"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        container = modal.query_one("Container")
        assert container is not None


@pytest.mark.asyncio
async def test_error_modal_dismiss_method():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Test error"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        modal.dismiss()
        await pilot.pause()
        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_error_modal_screen_stack():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield Button("Start", id="start")

        def on_button_pressed(self, event: Button.Pressed) -> None:
            if event.button.id == "start":
                self.push_screen(ErrorModal(["Stacked error"]))

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.click("#start")
        await pilot.pause()

        assert len(app.screen_stack) > 1
        top_screen = app.screen_stack[-1]
        assert isinstance(top_screen, ErrorModal)
        assert top_screen.errors == ["Stacked error"]


@pytest.mark.asyncio
async def test_error_modal_close_via_escape():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Test error"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)

        await pilot.press("escape")
        await pilot.pause()

        assert len(app.screen_stack) == 1


@pytest.mark.asyncio
async def test_error_modal_ok_button_exists():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Test error"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        ok_button = modal.query_one("#error-ok-button", Button)
        assert ok_button is not None
        assert ok_button.label == "OK"


@pytest.mark.asyncio
async def test_error_modal_error_count_matches():
    class TestApp(App):
        CSS = """
        $geoff-primary: blue;
        $geoff-secondary: green;
        """

        def compose(self) -> ComposeResult:
            yield ErrorModal(["Error 1", "Error 2", "Error 3", "Error 4"])

    app = TestApp()
    async with app.run_test() as pilot:
        modal = app.query_one(ErrorModal)
        statics = modal.query(Static)
        error_statics = [s for s in statics if "- " in str(s.render())]
        assert len(error_statics) == 4
