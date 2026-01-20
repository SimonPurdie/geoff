# TUI Refactor Plan

## Goal
Improve the TUI aesthetics ("cleaner and slicker", "minimalistic"), ensure it respects themes, and verify it handles multiple study docs correctly.

## Status
**Completed**

## Steps

### 1. Update Validation Tool (`utils/preview_tui.py`)
- [x] Update `get_required_widgets()` to reflect the current nesting.
- [x] Verification Passed.

### 2. Global CSS Refactor (`src/geoff/app.py`)
- [x] Remove custom `$geoff-*` definitions.
- [x] Define layout rules using standard Textual variables.

### 3. Widget CSS & Layout Refactor
- [x] `src/geoff/widgets/study_docs.py` refactored.
- [x] `src/geoff/widgets/task_source.py` refactored.
- [x] `src/geoff/widgets/toolbar.py` refactored.
- [x] `src/geoff/widgets/prompt_preview.py` refactored.

### 4. Verification
- [x] `utils/preview_tui.py` passed.

## Notes
- **Theme Support**: By switching to variables like `$surface`, `$primary`, `$text`, the app will automatically respect Textual's built-in themes (Dark, Light, Dracula, etc.).
- **Multiple Docs**: The `StudyDocsWidget` uses a `Vertical` scrollable container. With compact styling, 5 docs will fit easily without scrolling, but scrolling is preserved if needed.
