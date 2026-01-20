"""TUI Preview Utilities for Geoff.

This module provides utilities to preview and validate the Geoff TUI layout,
checking that all UI elements are present and rendering correctly.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import sys


@dataclass
class WidgetInfo:
    """Information about a widget in the TUI."""

    widget_type: str
    widget_id: Optional[str] = None
    present: bool = False
    display: bool = True
    width: int = 0
    height: int = 0
    region_x: int = 0
    region_y: int = 0
    region_width: int = 0
    region_height: int = 0
    visible: bool = False
    has_content: bool = False
    render_error: Optional[str] = None
    children: List["WidgetInfo"] = field(default_factory=list)


@dataclass
class TUIPreviewResult:
    """Result of a TUI preview validation."""

    success: bool
    widgets: List[WidgetInfo]
    missing_widgets: List[str]
    zero_size_widgets: List[str]
    hidden_widgets: List[str]
    total_widgets: int
    visible_widgets: int
    raw_output: str = ""


def get_required_widgets() -> List[Dict[str, Any]]:
    """Return the list of required widgets with their expected properties."""
    return [
        {"type": "Header", "id": None, "required": True},
        {"type": "StudyDocsWidget", "id": "study-docs", "required": True},
        {"type": "TaskSourceWidget", "id": "task-source", "required": True},
        {"type": "BackpressureWidget", "id": "backpressure", "required": True},
        {"type": "BreadcrumbWidget", "id": "breadcrumb", "required": True},
        {"type": "LoopConfigWidget", "id": "loop-config", "required": True},
        {"type": "ToolbarWidget", "id": "actions", "required": True},
        {"type": "PromptPreviewWidget", "id": "bottom-panel", "required": True},
        {"type": "Container", "id": "main-body", "required": True},
        {"type": "VerticalScroll", "id": "left-panel", "required": True},
        {"type": "Static", "id": "right-spacer", "required": False},
    ]


async def preview_tui(
    size: tuple[int, int] = (120, 40),
    timeout: float = 5.0,
) -> TUIPreviewResult:
    """Preview the Geoff TUI and validate all UI elements.

    Args:
        size: Tuple of (width, height) for the terminal size.
        timeout: Maximum time to wait for rendering in seconds.

    Returns:
        TUIPreviewResult containing all widget information and validation status.
    """
    from geoff.app import GeoffApp

    widgets: List[WidgetInfo] = []
    missing_widgets: List[str] = []
    zero_size_widgets: List[str] = []
    hidden_widgets: List[str] = []

    app = GeoffApp()

    try:
        async with app.run_test(size=size) as pilot:
            await asyncio.sleep(timeout)

            required = get_required_widgets()

            for req in required:
                widget_type = req["type"]
                widget_id = req["id"]

                try:
                    if widget_id:
                        widget = pilot.app.query_one(f"#{widget_id}")
                    else:
                        widget = pilot.app.query(widget_type).first()
                    widget_info = inspect_widget(widget, widget_type, widget_id)
                    widgets.append(widget_info)

                    if not widget_info.present:
                        missing_widgets.append(
                            f"{widget_type} ({widget_id or 'no id'})"
                        )
                    elif widget_info.height == 0 or widget_info.width == 0:
                        zero_size_widgets.append(
                            f"{widget_type} ({widget_id or 'no id'})"
                        )
                    elif not widget_info.display:
                        hidden_widgets.append(f"{widget_type} ({widget_id or 'no id'})")

                except Exception as e:
                    info = WidgetInfo(
                        widget_type=widget_type,
                        widget_id=widget_id,
                        present=False,
                    )
                    widgets.append(info)
                    missing_widgets.append(f"{widget_type} ({widget_id or 'no id'})")

            for w in pilot.app.query("*"):
                info = inspect_widget(w, type(w).__name__, getattr(w, "id", None))
                if info.widget_id and not any(
                    w.widget_id == info.widget_id for w in widgets
                ):
                    widgets.append(info)

    except Exception as e:
        return TUIPreviewResult(
            success=False,
            widgets=widgets,
            missing_widgets=missing_widgets,
            zero_size_widgets=zero_size_widgets,
            hidden_widgets=hidden_widgets,
            total_widgets=len(widgets),
            visible_widgets=0,
            raw_output=f"Error running app: {e}",
        )

    visible_count = sum(1 for w in widgets if w.visible)

    return TUIPreviewResult(
        success=len(missing_widgets) == 0 and len(zero_size_widgets) == 0,
        widgets=widgets,
        missing_widgets=missing_widgets,
        zero_size_widgets=zero_size_widgets,
        hidden_widgets=hidden_widgets,
        total_widgets=len(widgets),
        visible_widgets=visible_count,
    )


def inspect_widget(widget, widget_type: str, widget_id: Optional[str]) -> WidgetInfo:
    """Inspect a widget and return its information."""
    region = getattr(widget, "region", None)
    size = getattr(widget, "size", None)

    region_x = region.x if region else 0
    region_y = region.y if region else 0
    region_width = region.width if region else 0
    region_height = region.height if region else 0

    width = size.width if size else 0
    height = size.height if size else 0

    display = getattr(widget, "display", True)

    visible = display and region_width > 0 and region_height > 0

    has_content = False
    render_error = None

    if hasattr(widget, "render"):
        try:
            render_result = widget.render()
            has_content = render_result is not None
        except Exception as e:
            render_error = str(e)
            has_content = False

    children = []
    for child in getattr(widget, "children", []):
        children.append(
            inspect_widget(child, type(child).__name__, getattr(child, "id", None))
        )

    return WidgetInfo(
        widget_type=widget_type,
        widget_id=widget_id,
        present=True,
        display=display,
        width=width,
        height=height,
        region_x=region_x,
        region_y=region_y,
        region_width=region_width,
        region_height=region_height,
        visible=visible,
        has_content=has_content,
        render_error=render_error,
        children=children,
    )


def format_preview_result(result: TUIPreviewResult) -> str:
    """Format a TUI preview result as a human-readable string."""
    lines = []

    lines.append("=" * 60)
    lines.append("GEOFF TUI PREVIEW RESULTS")
    lines.append("=" * 60)
    lines.append(f"Success: {'YES' if result.success else 'NO'}")
    lines.append(f"Total widgets: {result.total_widgets}")
    lines.append(f"Visible widgets: {result.visible_widgets}")
    lines.append("")

    if result.zero_size_widgets:
        lines.append("ZERO-SIZE WIDGETS (rendering issue):")
        for w in result.zero_size_widgets:
            lines.append(f"  - {w}")
        lines.append("")

    if result.hidden_widgets:
        lines.append("HIDDEN WIDGETS:")
        for w in result.hidden_widgets:
            lines.append(f"  - {w}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("ALL WIDGETS:")
    lines.append("-" * 60)

    for widget in result.widgets:
        if widget.widget_id or widget.widget_type in ["Header", "PromptPreviewWidget"]:
            status = "VISIBLE" if widget.visible else "HIDDEN/ZERO-SIZE"
            if not widget.present:
                status = "MISSING"

            lines.append(f"[{status}] {widget.widget_type}")
            if widget.widget_id:
                lines.append(f" #{widget.widget_id}")

            if widget.visible and widget.region_width > 0:
                lines.append(
                    f" @ ({widget.region_x},{widget.region_y}) {widget.region_width}x{widget.region_height}"
                )
            else:
                lines.append("")

            if widget.render_error:
                lines.append(f"    Render error: {widget.render_error}")

    lines.append("=" * 60)

    return "\n".join(lines)


async def run_preview_and_exit(size: tuple[int, int] = (120, 40)) -> TUIPreviewResult:
    """Run the TUI preview and return the result.

    This is a convenience function for CLI usage.
    """
    result = await preview_tui(size=size)
    print(format_preview_result(result))
    return result


def main():
    """CLI entry point for TUI preview utility."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Preview and validate Geoff TUI layout"
    )
    parser.add_argument(
        "--width", type=int, default=120, help="Terminal width (default: 120)"
    )
    parser.add_argument(
        "--height", type=int, default=40, help="Terminal height (default: 40)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="Render timeout in seconds (default: 2.0)",
    )

    args = parser.parse_args()

    result = asyncio.run(
        preview_tui(size=(args.width, args.height), timeout=args.timeout)
    )
    print(format_preview_result(result))

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    main()
