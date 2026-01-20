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

### Task 2: Property-Based Tests for LoopConfigWidget - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Added 5 new Hypothesis property-based tests for LoopConfigWidget
  - Tests cover: initial value rendering, infinity indicator behavior, config updates for max_iterations and max_stuck, and update_from_config method
  - All 126 tests pass (5 new tests added to existing 121)
- **Tests:**
  - `test_loop_config_property_initial_values`: Tests widget initialization with various max_iterations (0-1000) and max_stuck (0-100) values
  - `test_infinity_indicator_property`: Tests infinity indicator visibility (shown when max_iterations=0, hidden otherwise)
  - `test_loop_config_updates_property`: Tests config updates propagate correctly for max_iterations
  - `test_max_stuck_updates_property`: Tests config updates propagate correctly for max_stuck
  - `test_update_from_config_property`: Tests update_from_config method with various config values

### Task 3: Property-Based Tests for Widgets - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Added property-based tests for BackpressureWidget, BreadcrumbWidget, StudyDocsWidget, and TaskSourceWidget
  - Tests cover initial state rendering, toggle behavior, config updates, and update_from_config method
  - All 141 tests pass (15 new tests added to existing 126)
- **Tests:**
  - BackpressureWidget: `test_backpressure_initial_state`, `test_backpressure_toggle_property`, `test_backpressure_update_from_config`
  - BreadcrumbWidget: `test_breadcrumb_initial_state`, `test_breadcrumb_toggle_property`, `test_breadcrumb_update_from_config`
  - StudyDocsWidget: `test_study_docs_initial_state`, `test_study_docs_update_from_config`, `test_study_docs_breadcrumbs_update`, `test_study_docs_add_remove_property`
  - TaskSourceWidget: `test_task_source_initial_state`, `test_task_source_mode_switch_property`, `test_task_source_tasklist_update`, `test_task_source_oneoff_update`, `test_task_source_update_mode`

### Task 4: Property-Based Tests for PromptPreviewWidget - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Added 6 new Hypothesis property-based tests for PromptPreviewWidget
  - Tests cover initial state rendering with various configs, study_docs updates, backpressure updates, breadcrumb updates, task mode switch, and mode toggle
  - All 147 tests pass (6 new tests added to existing 141)
- **Tests:**
  - `test_prompt_preview_initial_state`: Tests widget initialization with various combinations of study_docs, breadcrumbs, tasklist, backpressure, breadcrumb, and task_mode
  - `test_prompt_preview_study_docs_update`: Tests that study_docs changes propagate to the preview
  - `test_prompt_preview_backpressure_update`: Tests backpressure toggle updates the preview correctly
  - `test_prompt_preview_breadcrumb_update`: Tests breadcrumb toggle updates the preview correctly
  - `test_prompt_preview_task_mode_switch`: Tests task mode (tasklist/oneoff) affects preview content
  - `test_prompt_preview_mode_toggle`: Tests mode switching updates the preview content

### Task 5: Property-Based Tests for PromptValidator - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Added 11 new Hypothesis property-based tests for PromptValidator
  - Tests cover validation of study docs, breadcrumbs, tasklist files, one-off prompts, max iterations, max stuck, and is_valid method
  - All 157 tests pass (11 new tests added to existing 146)
- **Tests:**
  - `test_valid_config_with_positive_iterations`: Tests validation with various valid max_iterations and max_stuck values
  - `test_empty_study_doc_errors`: Tests that empty study doc paths produce errors
  - `test_nonexistent_study_doc_files`: Tests that nonexistent study doc files produce errors
  - `test_breadcrumb_file_existence`: Tests breadcrumb file validation (empty path when enabled, nonexistent file)
  - `test_tasklist_file_existence`: Tests tasklist file validation (empty path when enabled, nonexistent file)
  - `test_oneoff_prompt_validation`: Tests one-off prompt validation (empty/whitespace vs valid)
   - `test_max_iterations_validation`: Tests max_iterations must be >= 0
   - `test_max_stuck_validation`: Tests max_stuck must be >= 0
   - `test_is_valid_matches_validate`: Tests that is_valid() matches validate() results
   - `test_empty_study_doc_list_valid`: Tests that empty study doc list is valid

### Task 6: Property-Based Tests for ToolbarWidget - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Added 9 new property-based tests for ToolbarWidget
  - Tests cover: button existence, ID verification, message triggering for all actions (Copy, Run Once, Run Loop, Reset, Quit), and comprehensive message firing
  - All 166 tests pass (9 new tests added to existing 157)
- **Tests:**
  - `test_toolbar_all_buttons_exist_property`: Tests all 5 buttons exist
  - `test_toolbar_copy_button_triggers_message`: Tests Copy button triggers CopyPrompt message
  - `test_toolbar_run_once_button_triggers_message`: Tests Run Once button triggers RunOnce message
  - `test_toolbar_run_loop_button_triggers_message`: Tests Run Loop button triggers RunLoop message
  - `test_toolbar_reset_button_triggers_message`: Tests Reset button triggers Reset message
  - `test_toolbar_quit_button_triggers_message`: Tests Quit button triggers Quit message
  - `test_toolbar_composes_correct_number_of_buttons`: Verifies 5 buttons are composed
  - `test_toolbar_all_buttons_have_ids`: Tests all buttons have correct IDs
  - `test_toolbar_all_buttons_fire_messages`: Tests all buttons fire their respective messages

### Task 7: Property-Based Tests for ErrorModal - COMPLETED
- **Date:** 2026-01-20
- **Changes:**
  - Added 5 new Hypothesis property-based tests for ErrorModal
  - Tests cover: initialization with various error list sizes, rendering all errors, error count verification, dismiss behavior, and OK button existence
  - All 171 tests pass (5 new tests added to existing 166)
- **Tests:**
  - `test_error_modal_property_init_with_various_errors`: Tests modal initialization with various error list sizes (0-10 errors)
  - `test_error_modal_property_renders_all_errors`: Tests that all errors are rendered with printable ASCII characters
  - `test_error_modal_property_error_count`: Tests error count matches the number of errors (1-20)
  - `test_error_modal_property_dismiss_behavior`: Tests dismiss behavior on OK button click
  - `test_error_modal_property_ok_button_exists`: Tests OK button exists and has correct label

