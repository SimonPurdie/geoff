# Breadcrumbs

- **Task 21 (State Persistence):** Implemented auto-save config in `on_config_updated()` handler. The `_save_config()` method calls `ConfigManager.save_repo_config()` with error handling. Reset functionality removes repo config file and reloads from global defaults. Widget state resets immediately for prompt preview; full UI refresh would require app restart for dynamic widgets like study docs list.

- **Task 20 (Reset Functionality):** Reset clears repo-level `.geoff/geoff.yaml` and reloads config. The prompt preview updates immediately. Note: some widgets like StudyDocsWidget with dynamic doc lists may need app restart to fully reflect defaults in their internal state.

- **Task 16 (Clipboard Integration):** Successfully implemented clipboard integration with validation. The `copy_to_clipboard()` function uses `pyperclip.copy()` and returns a boolean indicating success. The Copy Prompt handler validates the config first, builds the prompt, then copies it to clipboard. Validation failures show as error notifications. Textual's `notify()` method uses severity levels `information`, `warning`, and `error` (not `success`).

- **Task 15 (Validation System):** When testing with default PromptConfig values, the default `study_docs=["docs/SPEC.md"]`, `task_mode="tasklist"`, and `breadcrumb_enabled=True` mean validation will fail for missing files even if you're only testing a specific feature. Tests should either:
  1. Create all necessary files in the tmp_path, OR
  2. Disable features and use one-off mode with empty lists for study_docs to isolate the test case
  - This is important for future agents writing widget tests that interact with config.

- **Task 8 (Study Docs Panel):** I implemented `StudyDocsWidget` using standard `$primary` and `$secondary` CSS variables instead of `$geoff-primary` and `$geoff-secondary` as requested in the spec, because I ran into difficulties making the custom variables work in the test harness (`test_study_docs_widget.py`). The application logic works correctly. Future agents might want to revisit this to strictly adhere to the spec or fix the test setup.
- **Task 9 (Task Source Panel):** When testing `TextArea` widgets, I found that programmatic updates in tests (`widget.text = "value"`) require manually posting the `TextArea.Changed(widget)` event to trigger handlers. Also, the `TextArea.Changed` event uses `event.text_area` to access the widget, unlike `Input.Changed` which uses `event.input`.
- **Task 12 (Loop Configuration Panel):** Unlike `TextArea`, programmatic updates to `Input` widgets (`widget.value = "value"`) in tests *do* seem to trigger the `Changed` event (or at least the data binding logic worked as expected without manual event posting). Also found that `Static` (and `Label`) widgets in newer Textual versions don't easily expose their content via a `renderable` attribute for inspection; checking visibility or CSS classes is a more robust testing strategy for UI state.
- **Task 14 (Effective Prompt Preview Panel):** Confirmed the difficulty with inspecting `Static` content in tests. However, I found that calling `widget.render()` returns the content object, which can be cast to `str` for assertion purposes in simple cases (like verifying the prompt text).
