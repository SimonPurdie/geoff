import pytest
from geoff.app import GeoffApp


@pytest.mark.asyncio
async def test_app_layout():
    app = GeoffApp()
    async with app.run_test() as pilot:
        # Check if widgets exist
        assert pilot.app.query_one("#study-docs")
        assert pilot.app.query_one("#task-source")
        assert pilot.app.query_one("#backpressure")
        assert pilot.app.query_one("#breadcrumb")
        assert pilot.app.query_one("#loop-config")
        assert pilot.app.query_one("#actions")
        assert pilot.app.query_one("#bottom-panel")

        # Check structure
        left_panel = pilot.app.query_one("#left-panel")
        assert "study-docs" in [c.id for c in left_panel.children]
