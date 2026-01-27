# Breadcrumbs

- **Textual Widget Styling (Task 24):** 
  - Use `DEFAULT_CSS` (not `CSS`) for Textual widget styling to ensure proper inheritance in test environments.
  - Define all required CSS variables (`$geoff-primary`, `$geoff-secondary`, etc.) within each widget's `DEFAULT_CSS` block; they cannot be inherited from the App's CSS.
  - Textual CSS does not support `font-family`, `font-size`, or `line-height` properties.
  - Use only valid Textual CSS properties: `background`, `color`, `border`, `padding`, `margin`, `text-style`, `layout`, etc.

- **Hypothesis Property Testing (Task 23):**
  - Use `st.sampled_from` with specific alphabets instead of raw `st.text()` to avoid generating strings with control characters that get stripped or altered by TUI components.

- **Testing ModalScreens (Task 19):** 
  - `ModalScreen` widgets are not queryable via `app.query_one()` when pushed to the screen stack. Access them through `app.screen_stack[-1]` to verify their content and state.
  - Verification of a modal's presence can be done by checking `len(app.screen_stack) > 1`.

- **Integration Testing with Default Config (Task 15):** 
  - The default `PromptConfig` (`study_docs=["docs/SPEC.md"]`, etc.) means validation will fail for missing files even when testing unrelated features. Tests must either create these placeholder files or explicitly use a config that disables those features (e.g., one-off mode with empty lists).

- **CSS Variable Issues in Tests (Task 8):** 
  - Difficulties making custom CSS variables (like `$geoff-primary`) work in the test harness (`test_study_docs_widget.py`). Standard `$primary` and `$secondary` were used as a workaround.

- **Testing TextArea vs Input (Task 9, 12):**
  - Programmatic updates to `TextArea` in tests (`widget.text = "value"`) require manually posting a `TextArea.Changed(widget)` event. `Input` widgets trigger `Changed` events automatically on `widget.value = "value"`.
  - `TextArea.Changed` event uses `event.text_area` to access the widget, while `Input.Changed` uses `event.input`.

- **Inspecting Static Content in Tests (Task 12, 14, 19):**
  - `Static` and `Label` widgets in newer Textual versions do not easily expose content via a `renderable` attribute. Use `str(widget.render())` to inspect the content object for assertions.

- **Hypothesis Deadline in Async Tests (Task 25):**
  - Property-based tests with multiple async operations (e.g., clicking, pausing) may exceed the default 200ms deadline. Add `deadline=None` to `@settings()` decorator to disable the deadline check for slow tests.
  - Example: `@settings(max_examples=15, deadline=None)`

- **Widget Config Object Handling (Task 25):**
  - The `update_from_config()` method in widgets like TaskSourceWidget replaces the widget's internal config object (`self.config = config`) rather than updating a shared config. Tests checking config state should query `widget.config` instead of the original config object passed to the app.

- **Syntax Error in Test Files (Current Task):**
  - When running pytest, discovered a pre-existing syntax error in `test_prompt_preview_widget.py` (line 237): `else:` without a corresponding `if` statement. Fixed by changing to `elif task_mode == "oneoff":` to properly handle the task mode conditional logic.

- **Hypothesis Function-Scoped Fixture Health Check:**
  - Property-based tests using `@given` with pytest fixtures like `tmp_path` trigger a `FailedHealthCheck` for function-scoped fixtures. Suppress this by adding `suppress_health_check=[HealthCheck.function_scoped_fixture]` to the `@settings()` decorator.
  - Example: `@settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])`

- **Breadcrumb File Auto-Creation (Current Task):**
  - Modified `PromptValidator` to automatically create blank breadcrumb files instead of erroring when they're missing.
  - Only applies to breadcrumb files - other missing files (study docs, tasklists) still error as before.
  - File creation includes proper parent directory creation and error handling for invalid paths or permission issues.
  - Tests updated to verify new behavior: missing breadcrumb files are created and valid, while invalid paths still generate errors.

- **Ambiguity in Test Assertions (Task 26):**
  - Prompt contains "IMPORTANT:" in both the Backpressure section and the Breadcrumb Instruction section.
  - Tests checking for backpressure absence must assert against specific backpressure lines (e.g., "- After implementing functionality") rather than the "IMPORTANT:" string alone to avoid false positives.
