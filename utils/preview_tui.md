# preview_tui.py

A command-line utility for previewing and validating the Geoff TUI layout, optimized for agentic workflows.

## Purpose

This utility launches the Geoff TUI in test mode and extracts rich spatial and state information. It is designed to help spatially-adept models (like LLMs) understand the TUI's current state, layout, and interactive elements.

- **Spatial Mapping**: Generates a high-resolution ASCII map of the terminal layout.
- **State Extraction**: Captures current values of inputs, labels of buttons, and states of checkboxes.
- **Focus Tracking**: Identifies which widget currently holds input focus.
- **Hierarchy Analysis**: Provides a complete tree view of all UI components.

## Usage

```bash
uv run python3 utils/preview_tui.py [options]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--width WIDTH` | Terminal width in columns | 120 |
| `--height HEIGHT` | Terminal height in rows | 40 |
| `--timeout SECONDS` | Render timeout in seconds | 2.0 |
| `-h, --help` | Show help message | - |

## Output Sections

### 1. High-Resolution Spatial Map
A 1:1 character grid representing the terminal.
- `+`, `-`, `|`: Widget boundaries.
- `Text`: Widget IDs placed within their respective regions.
- This section allows agents to calculate exact mouse click coordinates or relative positions.

### 2. Interactable Widgets
A table of widgets that can be interacted with (Inputs, Buttons, etc.)
- **ID**: The widget's unique identifier.
- **TYPE**: The Textual widget class.
- **POS/SIZE**: Exact coordinates `(x, y)` and dimensions `(w, h)`.
- **VALUE/TEXT**: Current state or label.
- **Focus (`*`)**: An asterisk indicates the widget currently has focus.

### 3. Full Hierarchy
A tree view of all widgets, including internal/anonymous ones.
- `[V-]`: Visible
- `[H-]`: Hidden
- `[VF]`: Visible and Focused

## Integration for Agents

Agents can use this utility to "see" the UI before performing actions:

```bash
# 1. Check current state
uv run python3 utils/preview_tui.py --width 100 --height 30

# 2. Based on output, click a button
# (Example: btn-run-once is at (19, 72) with size 16x3)
```


### Options

| Flag | Description | Default |
|------|-------------|---------|
| `--width WIDTH` | Terminal width in columns | 120 |
| `--height HEIGHT` | Terminal height in rows | 40 |
| `--timeout SECONDS` | Render timeout in seconds | 2.0 |
| `-h, --help` | Show help message | - |

### Examples

```bash
# Run with default settings (120x40, 2s timeout)
python utils/preview_tui.py

# Test with a smaller terminal size
python utils/preview_tui.py --width 80 --height 24

# Allow more time for rendering
python utils/preview_tui.py --timeout 5.0
```

## Expected Output

On success, the utility prints a report showing:

```
============================================================
GEOFF TUI PREVIEW RESULTS
============================================================
Success: YES
Total widgets: 42
Visible widgets: 42

------------------------------------------------------------
ALL WIDGETS:
------------------------------------------------------------
[VISIBLE] Header
[VISIBLE] StudyDocsWidget #study-docs
[VISIBLE] TaskSourceWidget #task-source
...
============================================================
```

### Output Sections

- **Success**: Overall validation status (YES/NO)
- **Total widgets**: Count of all widgets found in the TUI
- **Visible widgets**: Count of widgets with non-zero size and visible
- **Zero-size widgets**: Widgets that failed to render with dimensions
- **Hidden widgets**: Widgets with `display=False`
- **All widgets**: Detailed list with visibility status and position

### Exit Codes

- `0`: All required widgets are present and visible
- `1`: One or more issues detected (missing, zero-size, or hidden widgets)

## Integration

This utility can be used in development workflows:

```bash
# Run as part of a test suite
python utils/preview_tui.py || echo "TUI layout validation failed"
```

## Programmatic Usage

The module can also be imported and used directly:

```python
import asyncio
from utils.preview_tui import preview_tui, format_preview_result

async def check_tui():
    result = await preview_tui(size=(120, 40), timeout=2.0)
    print(format_preview_result(result))
    return result.success

asyncio.run(check_tui())
```
