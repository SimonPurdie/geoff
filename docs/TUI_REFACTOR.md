# TUI Refactoring Plan

## 1. Problem Statement
The current TUI layout is inefficient:
- **Wasted Space:** A large empty area exists on the right side of the screen.
- **Vertical Constraint:** The fixed-width left panel forces vertical scrolling to access lower widgets.
- **Visual Noise:** Excessive padding and margins reduce information density.

## 2. Design Goal
Maximize horizontal space utilization to display all configuration widgets simultaneously without scrolling. Adopt a dashboard-style grid layout.

## 3. Proposed Layout Architecture

### High-Level Structure
The application will transition from a `Horizontal` split (Left Panel + Right Spacer) to a `Vertical` stack of rows, where rows contain columns.

```text
+---------------------------------------------------------------+
| Header                                                        |
+---------------------------------------------------------------+
| [Row 1: Primary Config] (Height: Flexible/Main)               |
| +---------------------------+ +-----------------------------+ |
| | StudyDocsWidget           | | TaskSourceWidget            | |
| | (Width: 1fr)              | | (Width: 1fr)                | |
| |                           | |                             | |
| | [List of docs...]         | | [Task Mode / One-off...]    | |
| |                           | |                             | |
| +---------------------------+ +-----------------------------+ |
+---------------------------------------------------------------+
| [Row 2: Settings Strip] (Height: Auto)                        |
| +----------------+ +------------------+ +-------------------+ |
| | Backpressure   | | Breadcrumb       | | Loop Config       | |
| | [x] Enabled    | | [x] Enabled      | | Iterations: [0]   | |
| +----------------+ +------------------+ +-------------------+ |
+---------------------------------------------------------------+
| [Row 3: Actions] (Height: Auto)                               |
| [Copy] [Run Once] [Run Loop] [Reset] [Quit]                   |
+---------------------------------------------------------------+
| [Row 4: Preview] (Height: Fixed ~12 lines or 20%)             |
| Effective Prompt Preview...                                   |
+---------------------------------------------------------------+
```

## 4. Implementation Details

### A. `GeoffApp` Layout (`src/geoff/app.py`)
- **Remove:** `#left-panel` (VerticalScroll) and `#right-spacer`.
- **Introduce:** A main container with vertical layout.
- **Compose Method:**
  ```python
  with Container(id="main-body"):
      with Horizontal(id="top-row"):
          yield StudyDocsWidget(...)
          yield TaskSourceWidget(...)
      with Horizontal(id="settings-row"):
          yield BackpressureWidget(...)
          yield BreadcrumbWidget(...)
          yield LoopConfigWidget(...)
      yield ToolbarWidget(...)
      yield PromptPreviewWidget(...)
  ```

### B. CSS Refinements
- **Global:** Define standard spacing variables (e.g., `$spacing: 1`).
- **Containers:**
  - `#top-row`: `height: 1fr;` (Takes available vertical space).
  - `#settings-row`: `height: auto;`
  - Widget Panels: Remove `margin-bottom` in favor of container gaps if possible, or reduce to `1`.
- **Colors:** Maintain existing theme but maybe lighten borders for inner widgets to reduce visual clutter.

### C. Widget-Specific Updates

#### 1. `StudyDocsWidget`
- **Layout:** Ensure the docs list can expand.
- **Styling:** Remove fixed height if any.

#### 2. `TaskSourceWidget`
- **Layout:** This widget needs to be flexible to match the height of `StudyDocsWidget`.
- **TextArea:** The "One-off Prompt" `TextArea` should have `height: 1fr` to consume available space in the column.

#### 3. `BackpressureWidget`, `BreadcrumbWidget`, `LoopConfigWidget`
- **Compact Mode:**
  - These are currently full-width in the sidebar. In the new strip, they act as columns.
  - **CSS:** `width: 1fr; height: auto;`
  - Ensure labels and inputs align horizontally where possible to save vertical space.

#### 4. `PromptPreviewWidget`
- **Dock:** Fix at the bottom or just be the last element in the flex container.
- **Height:** constrain to `height: 12` or `15` to ensure top widgets have priority.

## 5. Verification Steps
1. **Visual Check:** Use `utils/preview_tui.py` to ensure no "zero-size" widgets and correct hierarchy.
2. **Functional Check:** Ensure tab navigation flows logically (Left col -> Right col -> Settings -> Actions).
3. **Resizing:** Verify layout behaves gracefully on smaller terminals (though optimized for standard 120x40).

## 6. Completion Status

### Task 1: GeoffApp Layout Refactoring - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Refactored `GeoffApp` layout from horizontal split to dashboard-style grid
  - Added `#top-row` and `#settings-row` containers for better space utilization
  - Reorganized widgets: StudyDocsWidget and TaskSourceWidget in top row, BackpressureWidget, BreadcrumbWidget, LoopConfigWidget in settings row
  - Removed deprecated `#left-panel` and `#right-spacer`
  - Added property-based tests for new layout structure (`tests/test_app_layout.py`)
  - Updated CSS for new container hierarchy and widget sizing
- **Tests:** All 121 tests pass
