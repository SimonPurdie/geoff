# Geoff TUI Implementation Plan

## Checklist

- [x] 1. Project scaffolding with UV
- [x] 2. Core dependencies installation
- [x] 3. Config data models
- [x] 4. Config file I/O layer
- [x] 5. Three-tier config resolution
- [x] 6. Prompt assembly engine
- [x] 7. Main application container
- [x] 8. Orientation/Study Docs panel
- [x] 9. Task Source panel with mode switching
- [x] 10. Backpressure toggle panel
- [x] 11. Breadcrumb toggle panel
- [x] 12. Loop configuration panel
- [ ] 13. Action toolbar
- [ ] 14. Effective Prompt preview panel
- [ ] 15. Validation system
- [ ] 16. Clipboard integration
- [ ] 17. Opencode execution layer
- [ ] 18. Loop execution harness
- [ ] 19. Error modal dialogs
- [ ] 20. Reset functionality
- [ ] 21. State persistence on changes
- [ ] 22. Polish and UX refinement

---

## 1. Project Scaffolding
**Task:** Set up Python project structure with UV package manager, entry point at `src/geoff/main.py`, and CLI command `geoff`.

**Spec Reference:** Section 7 (Implementation Notes) - "packaged with UV (entry point in src/geoff/main.py using terminal command 'geoff')"

**Deliverables:**
- `pyproject.toml` with UV configuration
- `src/geoff/` directory structure
- `src/geoff/__init__.py`
- `src/geoff/main.py` with entry point function
- `.gitignore` for Python/UV artifacts

---

## 2. Core Dependencies
**Task:** Install and configure Textual framework and supporting libraries.

**Spec Reference:** Section 1 (Core Concepts) - "Implementation: Built with Textual for TUI"

**Deliverables:**
- Add `textual` to dependencies
- Add `pyyaml` for config file handling
- Add `pyperclip` for clipboard operations
- Pin compatible versions in `pyproject.toml`

---

## 3. Config Data Models
**Task:** Create Pydantic or dataclass models for configuration state.

**Spec Reference:** Section 2 (Persistence & Config) - config structure and defaults

**Deliverables:**
- `src/geoff/config.py` with models:
  - `PromptConfig` dataclass containing:
    - `study_docs: list[str]` (default: `["docs/SPEC.md"]`)
    - `breadcrumbs_file: str` (default: `"docs/BREADCRUMBS.md"`)
    - `task_mode: str` (default: `"tasklist"` or `"oneoff"`)
    - `tasklist_file: str` (default: `"docs/PLAN.md"`)
    - `oneoff_prompt: str` (default: `""`)
    - `backpressure_enabled: bool` (default: `True`)
    - `breadcrumb_enabled: bool` (default: `True`)
    - `max_iterations: int` (default: `0`)
    - `max_stuck: int` (default: `2`)

---

## 4. Config File I/O Layer
**Task:** Implement YAML read/write functions for config files.

**Spec Reference:** Section 2 (Persistence & Config) - "Config format: `geoff.yaml`"

**Deliverables:**
- `src/geoff/config_io.py` with functions:
  - `load_yaml(path: Path) -> dict | None` - safely load YAML, return None if missing
  - `save_yaml(path: Path, data: dict) -> None` - write YAML with error handling
  - `ensure_config_dir(path: Path) -> None` - create `.geoff/` if needed

---

## 5. Three-Tier Config Resolution
**Task:** Implement config resolution logic: built-in defaults → global config → repo-local config.

**Spec Reference:** Section 2 (Persistence & Config) - "Three-tier model"

**Deliverables:**
- `src/geoff/config_manager.py` with class `ConfigManager`:
  - `get_builtin_defaults() -> PromptConfig` - return hardcoded defaults
  - `load_global_config() -> dict` - read `~/.geoff/geoff.yaml`
  - `load_repo_config() -> dict` - read `.geoff/geoff.yaml` in cwd
  - `resolve_config() -> PromptConfig` - merge three tiers (built-in < global < repo)
  - `save_repo_config(config: PromptConfig) -> None` - persist to `.geoff/geoff.yaml`

---

## 6. Prompt Assembly Engine
**Task:** Implement prompt construction logic based on config state.

**Spec Reference:** Section 1 (Core Concepts) - "Prompt Assembly Rules"

**Deliverables:**
- `src/geoff/prompt_builder.py` with function:
  - `build_prompt(config: PromptConfig) -> str`:
    - Assemble study docs as `study <docpath>` lines
    - Render breadcrumbs as `check <breadcrumbs>` if enabled and path non-empty
    - Include tasklist instructions if `task_mode == "tasklist"`
    - Include one-off prompt text if `task_mode == "oneoff"`
    - Include IMPORTANT block if `backpressure_enabled == True`
    - Include breadcrumb instruction if `breadcrumb_enabled == True`
    - Include task update line if in tasklist mode
    - Return assembled prompt as string with proper line breaks

---

## 7. Main Application Container
**Task:** Create Textual App class with layout structure.

**Spec Reference:** Section 3 (Mouse-First TUI Layout)

**Deliverables:**
- `src/geoff/app.py` with class `GeoffApp(App)`:
  - Initialize with `ConfigManager`
  - Load config on startup
  - Define CSS for layout (left panel + bottom preview + toolbar)
  - **CRITICAL:** Use unique CSS variable names prefixed with `$geoff_` to avoid conflicts with Textual reserved names (e.g., `$geoff_panel`, `$geoff_primary_color`, NOT `$panel` or `$primary`)
  - Compose widgets in proper hierarchy
  - Handle app-level events (quit, reset)

---

## 8. Orientation/Study Docs Panel
**Task:** Create widget for study docs list with inline editing and [+ Add Doc] button.

**Spec Reference:** Section 1 (Core Concepts) - "Orientation / Study Docs", Section 4 - "[+ Add Doc] behavior"

**Deliverables:**
- `src/geoff/widgets/study_docs.py` with class `StudyDocsWidget(Static)`:
  - Display list of doc paths as editable input fields
  - Each doc has `[X]` close button for removal
  - `[+ Add Doc]` button opens text input for new filepath
  - Breadcrumbs field separate (always visible, no remove button)
  - On change: trigger config update and prompt rebuild
  - Support ESC to cancel inline edits

---

## 9. Task Source Panel with Mode Switching
**Task:** Create widget for task source selection (tasklist vs one-off) with radio buttons.

**Spec Reference:** Section 1 (Core Concepts) - "Task Source (mutually exclusive, required)", Section 4 - "Mode switching"

**Deliverables:**
- `src/geoff/widgets/task_source.py` with class `TaskSourceWidget(Static)`:
  - Radio button group for mode selection (tasklist / one-off)
  - When tasklist mode: show editable input field for tasklist path
  - When one-off mode: show multiline TextArea for prompt entry
  - Support Ctrl+C/X/V, text selection, Shift+Enter for newlines in TextArea
  - Mode switch immediately updates effective prompt preview
  - On change: trigger config update and prompt rebuild

---

## 10. Backpressure Toggle Panel
**Task:** Create widget for backpressure checkbox.

**Spec Reference:** Section 1 (Core Concepts) - "Backpressure"

**Deliverables:**
- `src/geoff/widgets/backpressure.py` with class `BackpressureWidget(Static)`:
  - Checkbox labeled "Enforce tests & commit"
  - Default: checked (enabled)
  - On toggle: update config and trigger prompt rebuild

---

## 11. Breadcrumb Toggle Panel
**Task:** Create widget for breadcrumb checkbox.

**Spec Reference:** Section 1 (Core Concepts) - "Breadcrumb"

**Deliverables:**
- `src/geoff/widgets/breadcrumb.py` with class `BreadcrumbWidget(Static)`:
  - Checkbox labeled "Leave breadcrumbs"
  - Default: checked (enabled)
  - On toggle: update config and trigger prompt rebuild

---

## 12. Loop Configuration Panel
**Task:** Create widget for max iterations input with visual indicator for unlimited mode.

**Spec Reference:** Section 4 (Interaction Principles) - "Max iterations user-configurable"

**Deliverables:**
- `src/geoff/widgets/loop_config.py` with class `LoopConfigWidget(Static)`:
  - Input field for max iterations (integer, default: 0)
  - Validation: must be >= 0
  - Display infinity symbol (∞) next to input when value is 0 (indicating no limit)
  - Also include input for max_stuck (integer, default: 2)
  - On change: update config (no prompt rebuild needed)

---

## 13. Action Toolbar
**Task:** Create widget with action buttons.

**Spec Reference:** Section 4 (Interaction Principles) - "Actions"

**Deliverables:**
- `src/geoff/widgets/toolbar.py` with class `ToolbarWidget(Static)`:
  - Buttons: `[Copy Prompt]` `[Run Once]` `[Run Loop]` `[Reset]` `[Quit]`
  - Emit events on button press
  - Handle in main app: Copy Prompt, Run Once, Run Loop, Reset, Quit

---

## 14. Effective Prompt Preview Panel
**Task:** Create read-only scrollable preview of assembled prompt.

**Spec Reference:** Section 3 (Mouse-First TUI Layout) - "Effective Prompt (scrollable, always visible at bottom)"

**Deliverables:**
- `src/geoff/widgets/prompt_preview.py` with class `PromptPreviewWidget(Static)`:
  - Display assembled prompt as plain text
  - Scrollable (no auto-scroll)
  - Read-only (no editing)
  - No syntax highlighting
  - Update reactively when config changes

---

## 15. Validation System
**Task:** Implement validation logic for prompt execution.

**Spec Reference:** Section 4 (Interaction Principles) - "Validation"

**Deliverables:**
- `src/geoff/validator.py` with class `PromptValidator`:
  - `validate(config: PromptConfig) -> list[str]` - return list of error messages:
    - Check required filepaths are non-empty when features enabled
    - Check breadcrumbs path non-empty if breadcrumb checkbox enabled
    - Check task source is configured (tasklist path or one-off prompt)
    - Check file existence for all referenced paths
    - Check max_iterations >= 0
    - Check max_stuck >= 0
    - Return empty list if valid
  - Called before Copy Prompt, Run Once, Run Loop actions

---

## 16. Clipboard Integration
**Task:** Implement Copy Prompt functionality.

**Spec Reference:** Section 4 (Interaction Principles) - "Copy Prompt: copies assembled effective prompt to clipboard"

**Deliverables:**
- `src/geoff/clipboard.py` with function:
  - `copy_to_clipboard(text: str) -> bool` - use pyperclip, return success status
- Integrate into Copy Prompt button handler:
  - Validate prompt
  - If valid: copy to clipboard, show success message
  - If invalid: show error modal

---

## 17. Opencode Execution Layer
**Task:** Implement Run Once functionality with prompt passed directly to Opencode with switches.

**Spec Reference:** Section 4 (Interaction Principles) - "Run Once: validates prompt, then exits TUI to terminal and executes Opencode"

**Deliverables:**
- `src/geoff/executor.py` with function:
  - `execute_opencode_once(prompt: str) -> None`:
    - Exit TUI cleanly
    - Execute `opencode run "<prompt>" --log-level INFO` with prompt passed inline
    - Use subprocess with proper argument escaping (not shell=True for security)
    - Terminal shows Opencode output directly

---

## 18. Loop Execution Harness
**Task:** Implement Run Loop functionality with change detection and stuck iteration handling.

**Spec Reference:** Section 4 (Interaction Principles) - "Run Loop", Section 4 - "Loop Implementation"

**Deliverables:**
- `src/geoff/executor.py` - extend with function:
  - `execute_opencode_loop(prompt: str, max_iterations: int, max_stuck: int) -> None`:
    - Exit TUI cleanly
    - Implement loop with iteration counter (starting at 1)
    - Before each iteration: compute hash of repository state (git tree hash or directory hash)
    - Execute `opencode run "<prompt>" --log-level INFO`
    - After each iteration: compute hash again and compare
    - Track consecutive "stuck" iterations (no changes detected)
    - Break if stuck count reaches `max_stuck` (default: 2)
    - Sleep 2 seconds between iterations
    - If `max_iterations == 0`: run indefinitely (until stuck or manual cancel)
    - If `max_iterations > 0`: break after reaching limit
    - Allow manual cancellation (Ctrl+C) at any time
    - No return to TUI after completion
    - Log iteration number, stuck count, and termination reason

---

## 19. Error Modal Dialogs
**Task:** Create modal dialog widget for validation errors.

**Spec Reference:** Section 4 (Interaction Principles) - "Validation: show modal error dialog"

**Deliverables:**
- `src/geoff/widgets/error_modal.py` with class `ErrorModal(ModalScreen)`:
  - Display error message text
  - `[OK]` button to dismiss
  - Triggered by validation failures on Copy/Run actions
  - Show list of error messages from validator

---

## 20. Reset Functionality
**Task:** Implement Reset button to wipe repo-local config and restore global defaults.

**Spec Reference:** Section 4 (Interaction Principles) - "Reset: resets all fields to global config defaults"

**Deliverables:**
- In `src/geoff/app.py`:
  - `reset_to_defaults()` method:
    - Delete repo-local `.geoff/geoff.yaml` file if it exists
    - Reload config from global `~/.geoff/geoff.yaml` only (falling back to built-in defaults if global doesn't exist)
    - Update all widgets to reflect global defaults
    - Rebuild effective prompt preview
    - This ensures a clean slate at repo level

---

## 21. State Persistence on Changes
**Task:** Auto-save config changes to repo-local `.geoff/geoff.yaml`.

**Spec Reference:** Section 2 (Persistence & Config) - "Changes made in TUI save to repo-local `.geoff/geoff.yaml` automatically"

**Deliverables:**
- In `src/geoff/app.py`:
  - Hook into all config change events (doc edits, mode switches, toggles)
  - On any change: call `ConfigManager.save_repo_config()`
  - Ensure `.geoff/` directory exists before writing
  - Handle write errors gracefully

---

## 22. Polish and UX Refinement
**Task:** Final aesthetic pass and usability improvements.

**Spec Reference:** Section 6 (Design Considerations) - "Textual-based TUI should be visually polished"

**Deliverables:**
- CSS styling for clean, professional appearance
- Consistent spacing and alignment
- Clear visual hierarchy (panels, sections, buttons)
- Responsive layout testing
- Keyboard navigation improvements (optional, mouse-first is primary)
- User feedback messages (success confirmations, clear error states)
- README.md with usage instructions and examples