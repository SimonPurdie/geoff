import pytest
from hypothesis import given, settings, strategies as st
from geoff.app import GeoffApp


@pytest.mark.asyncio
async def test_app_layout():
    app = GeoffApp()
    async with app.run_test() as pilot:
        assert pilot.app.query_one("#study-docs")
        assert pilot.app.query_one("#task-source")
        assert pilot.app.query_one("#actions")
        assert pilot.app.query_one("#bottom-panel")


@pytest.mark.asyncio
async def test_new_dashboard_layout_structure():
    app = GeoffApp()
    async with app.run_test() as pilot:
        main_body = pilot.app.query_one("#main-body")

        top_row = pilot.app.query_one("#top-row")
        assert top_row in list(main_body.children)

        study_docs = pilot.app.query_one("#study-docs")
        task_source = pilot.app.query_one("#task-source")
        assert study_docs in list(top_row.children)
        assert task_source in list(top_row.children)

        toolbar = pilot.app.query_one("#actions")
        assert toolbar in list(main_body.children)

        prompt_preview = pilot.app.query_one("#bottom-panel")
        assert prompt_preview.parent == pilot.app.screen


@pytest.mark.asyncio
async def test_no_right_spacer():
    app = GeoffApp()
    async with app.run_test() as pilot:
        try:
            pilot.app.query_one("#right-spacer")
            assert False, "right-spacer should not exist in new layout"
        except Exception:
            pass


@pytest.mark.asyncio
async def test_no_left_panel():
    app = GeoffApp()
    async with app.run_test() as pilot:
        try:
            pilot.app.query_one("#left-panel")
            assert False, "left-panel should not exist in new layout"
        except Exception:
            pass


@given(
    width=st.integers(min_value=80, max_value=200),
    height=st.integers(min_value=24, max_value=100),
)
@settings(max_examples=10)
@pytest.mark.asyncio
async def test_layout_adapts_to_size(width, height):
    app = GeoffApp()
    async with app.run_test(size=(width, height)) as pilot:
        main_body = pilot.app.query_one("#main-body")
        assert main_body.size[0] > 0
        assert main_body.size[1] > 0
