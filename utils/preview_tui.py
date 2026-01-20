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
    has_focus: bool = False
    value: Optional[str] = None
    text: Optional[str] = None
    is_enabled: bool = True
    classes: List[str] = field(default_factory=list)
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
        {"type": "Horizontal", "id": "top-row", "required": True},
        {"type": "Horizontal", "id": "settings-row", "required": True},
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

    app = GeoffApp()

    try:
        async with app.run_test(size=size) as pilot:
            await asyncio.sleep(timeout)

            required = get_required_widgets()
            widgets: List[WidgetInfo] = []
            missing_widgets: List[str] = []
            zero_size_widgets: List[str] = []
            hidden_widgets: List[str] = []

            # Start inspection from the screen to get the full hierarchy once
            screen_info = inspect_widget(pilot.app.screen, "Screen", "screen")
            widgets = [screen_info]

            # Validate required widgets by searching the hierarchy
            all_widgets_flat = []

            def flatten(w):
                all_widgets_flat.append(w)
                for child in w.children:
                    flatten(child)

            flatten(screen_info)

            for req in required:
                widget_type = req["type"]
                widget_id = req["id"]

                found = False
                for w in all_widgets_flat:
                    if widget_id:
                        if w.widget_id == widget_id:
                            found = True
                    elif w.widget_type == widget_type:
                        found = True

                    if found:
                        if not w.visible:
                            if w.height == 0 or w.width == 0:
                                zero_size_widgets.append(
                                    f"{widget_type} (#{widget_id})"
                                )
                            else:
                                hidden_widgets.append(f"{widget_type} (#{widget_id})")
                        break

                if not found and req.get("required", True):
                    missing_widgets.append(f"{widget_type} (#{widget_id})")

            visible_count = sum(1 for w in all_widgets_flat if w.visible)

            return TUIPreviewResult(
                success=len(missing_widgets) == 0 and len(zero_size_widgets) == 0,
                widgets=widgets,
                missing_widgets=missing_widgets,
                zero_size_widgets=zero_size_widgets,
                hidden_widgets=hidden_widgets,
                total_widgets=len(all_widgets_flat),
                visible_widgets=visible_count,
            )

    except Exception as e:
        return TUIPreviewResult(
            success=False,
            widgets=[],
            missing_widgets=[],
            zero_size_widgets=[],
            hidden_widgets=[],
            total_widgets=0,
            visible_widgets=0,
            raw_output=f"Error running app: {e}",
        )


def inspect_widget(widget, widget_type: str, widget_id: Optional[str]) -> WidgetInfo:
    """Inspect a widget and return its information."""
    from textual.widgets import (
        Input,
        Button,
        Checkbox,
        RadioButton,
        TextArea,
        Label,
        Static,
    )

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
    has_focus = getattr(widget, "has_focus", False)
    is_enabled = not getattr(widget, "disabled", False)
    classes = list(getattr(widget, "classes", []))

    value = None
    text = None

    if isinstance(widget, Input):
        value = widget.value
    elif isinstance(widget, (Checkbox, RadioButton)):
        value = str(widget.value)
        text = str(widget.label)
    elif isinstance(widget, Button):
        text = str(widget.label)
    elif isinstance(widget, TextArea):
        value = widget.text
    elif isinstance(widget, (Label, Static)):
        # Try to get text content safely
        try:
            if hasattr(widget, "render"):
                render_result = widget.render()
                if render_result is not None:
                    text = str(render_result)
        except:
            pass

    render_error = None
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
        has_focus=has_focus,
        value=value,
        text=text,
        is_enabled=is_enabled,
        classes=classes,
        render_error=render_error,
        children=children,
    )


def generate_high_res_map(result: TUIPreviewResult, width: int, height: int) -> str:
    """Generate a high-resolution ASCII map of the TUI."""
    grid = [[" " for _ in range(width)] for _ in range(height)]

    all_visible = []

    def flatten(ws):
        for w in ws:
            if w.visible:
                all_visible.append(w)
                flatten(w.children)

    flatten(result.widgets)

    # Sort by area descending so smaller widgets are drawn on top
    all_visible.sort(key=lambda w: w.region_width * w.region_height, reverse=True)

    for w in all_visible:
        x1, y1 = w.region_x, w.region_y
        x2, y2 = x1 + w.region_width - 1, y1 + w.region_height - 1

        # Clip to terminal boundaries
        rx1, ry1 = max(0, x1), max(0, y1)
        rx2, ry2 = min(width - 1, x2), min(height - 1, y2)

        # Draw borders
        for y in range(ry1, ry2 + 1):
            for x in range(rx1, rx2 + 1):
                if y == y1 or y == y2:
                    if x == x1 or x == x2:
                        grid[y][x] = "+"
                    else:
                        grid[y][x] = "-"
                elif x == x1 or x == x2:
                    grid[y][x] = "|"

        # Draw ID label in the middle if there's space
        if (
            w.widget_id
            and w.region_width > len(w.widget_id) + 2
            and w.region_height > 2
        ):
            mid_y = y1 + w.region_height // 2
            mid_x = (
                y1 + (w.region_width - len(w.widget_id)) // 2
            )  # Wait, y1+... should be x1+...
            mid_x = x1 + (w.region_width - len(w.widget_id)) // 2

            if 0 <= mid_y < height:
                for i, char in enumerate(w.widget_id):
                    tx = mid_x + i
                    if 0 <= tx < width:
                        grid[mid_y][tx] = char

    lines = ["+" + "-" * width + "+"]
    for row in grid:
        lines.append("|" + "".join(row) + "|")
    lines.append("+" + "-" * width + "+")

    return "\n".join(lines)


def format_preview_result(result: TUIPreviewResult, width: int, height: int) -> str:
    """Format a TUI preview result as a human-readable string."""
    lines = []

    lines.append("=" * 60)
    lines.append("GEOFF TUI PREVIEW RESULTS")
    lines.append("=" * 60)
    lines.append(f"Success: {'YES' if result.success else 'NO'}")
    lines.append(f"Terminal Size: {width}x{height}")
    lines.append(f"Total widgets: {result.total_widgets}")
    lines.append(f"Visible widgets: {result.visible_widgets}")
    lines.append("")

    lines.append("HIGH-RESOLUTION SPATIAL MAP:")
    lines.append(generate_high_res_map(result, width, height))
    lines.append("")

    if result.zero_size_widgets:
        lines.append("ZERO-SIZE WIDGETS (rendering issue):")
        for w in result.zero_size_widgets:
            lines.append(f"  - {w}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("INTERACTABLE WIDGETS:")
    lines.append("-" * 60)
    lines.append(f"{'ID':<25} {'TYPE':<20} {'POS':<12} {'SIZE':<10} {'VALUE/TEXT'}")

    def print_interactable(ws):
        for w in ws:
            # Include widgets with IDs or specific interactable types,
            # or Statics that likely contain the prompt preview
            is_interactable = (
                w.widget_id
                or w.widget_type
                in ["Input", "Button", "Checkbox", "RadioButton", "TextArea"]
                or (w.widget_type == "Static" and w.text and len(w.text) > 10)
            )
            if w.visible and is_interactable:
                pos = f"({w.region_x},{w.region_y})"
                size = f"{w.region_width}x{w.region_height}"
                # Clean up value/text for display (remove newlines)
                display_val = (w.value or w.text or "").replace("\n", " ")
                display_val = display_val[:60]
                focused = "*" if w.has_focus else " "
                lines.append(
                    f"{focused}{w.widget_id or '':<24} {w.widget_type:<20} {pos:<12} {size:<10} {display_val}"
                )
            print_interactable(w.children)

    print_interactable(result.widgets)
    lines.append("")

    lines.append("-" * 60)
    lines.append("FULL HIERARCHY (ABBREVIATED):")
    lines.append("-" * 60)

    def print_hierarchy(ws, indent=0):
        for w in ws:
            status = "V" if w.visible else "H"
            focus = "F" if w.has_focus else "-"
            prefix = "  " * indent
            line = f"[{status}{focus}] {prefix}{w.widget_type}"
            if w.widget_id:
                line += f" #{w.widget_id}"
            line += f" ({w.region_width}x{w.region_height})"
            lines.append(line)
            print_hierarchy(w.children, indent + 1)

    print_hierarchy(result.widgets)

    lines.append("=" * 60)

    return "\n".join(lines)


async def run_preview_and_exit(size: tuple[int, int] = (120, 40)) -> TUIPreviewResult:
    """Run the TUI preview and return the result.

    This is a convenience function for CLI usage.
    """
    result = await preview_tui(size=size)
    print(format_preview_result(result, size[0], size[1]))
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
    print(format_preview_result(result, args.width, args.height))

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    main()
