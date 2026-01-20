# preview_tui.py

A command-line utility for previewing and validating the Geoff TUI layout.

## Purpose

This utility launches the Geoff TUI in test mode and validates that all required UI widgets are present, visible, and rendering correctly. It is primarily used for:

- Verifying TUI layout during development
- Detecting missing or zero-size widgets
- Validating widget visibility and positioning
- Testing TUI rendering at different terminal sizes

## Usage

```bash
python utils/preview_tui.py [options]
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
