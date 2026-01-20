# Geoff — TUI Prompt Constructor Spec

**Purpose:**
Personal productivity tool for composing, persisting, and executing coding-agent prompts in WSL. Focused on low-friction mouse-first configuration, reusable prompt elements, and seamless execution in Opencode.

**Implementation:** Built with Textual for TUI.

---

## 1. Core Concepts

**Prompt Elements (strict fixed order):**

1. **Orientation / Study Docs**

   ```
   study <docname> <optional docnote>
   ```

   * Multiple docs supported; add/remove inline via `[+ Add Doc]`.
   * Persisted per repo or defaults from global config; editable in-place.
   * Each doc is a manually-entered filepath relative to execution directory.
   * Default: `docs/SPEC.md`

2. **Task Source (mutually exclusive, required)** — choose one:

   * **Tasklist-driven:**

     ```
     follow <tasklist> and choose the most important item to address. Complete that item and no other.
     ```
     
     * Default: `docs/PLAN.md`
     
   * **One-off prompt (ephemeral):**

     * Last-used persisted per repo; editable inline **only when this mode is selected**.
     * Multiline text area with standard text editing (Ctrl+C/X/V, text selection, Shift+Enter or Ctrl+Enter for newlines).
     * Plain text only (markdown supported but not rendered).
     * Entered via inline text box when this mode is active.

   * **Mode selection:** Radio buttons or toggle to switch between tasklist and one-off patterns. Exactly one mode must always be selected. Switching modes updates the effective prompt preview immediately.

3. **Backpressure**

   ```
   IMPORTANT:
   - After implementing functionality or resolving problems, run the tests for that unit of code that was improved.
   - If functionality is missing then it's your job to add it as per the application specifications.
   - after performing your task run the tests
   - when tests pass, commit to deploy changes
   ```

   * Enabled by default; toggle via checkbox.
   * When disabled, entire IMPORTANT block is omitted from effective prompt.

4. **Breadcrumb**

   ```
   if you ran into difficulties due to a lack of information about the project or environment, which you then resolved, leave a note about it in <breadcrumbs> to help future agents. For example, if you run commands multiple times before learning the correct command.
   IMPORTANT: keep <breadcrumbs> operational only - status updates and progress notes do not belong there.
   ```

   * Enabled by default; toggle via checkbox.
   * `<breadcrumbs>` refers to the breadcrumbs file configured in Orientation section.
   * Breadcrumbs file rendered with `check` directive instead of `study` (lighter emphasis).
   * When disabled, entire breadcrumb instruction is omitted from effective prompt.
   * If breadcrumb file path is empty but checkbox enabled, error on attempted run.
   * Default: `docs/BREADCRUMBS.md`

5. **Task Update**

   ```
   Update <tasklist> when the task is done. If you discover issues, immediately update <tasklist> with your findings. When resolved, update <tasklist> and remove the item.
   ```

   * Automatically linked to tasklist mode; appears/disappears with mode selection.
   * No separate checkbox; controlled by Task Source mode choice.
   * When in one-off mode, both "study tasklist" and "update tasklist" are suppressed.

**Ordering:** Orientation → Task Source → Backpressure → Breadcrumb → Task Update (implicit)

**Prompt Assembly Rules:**
- Tasklist mode: includes "follow <tasklist> and choose the most important item to address. Complete that item and no other.", "Update <tasklist> when the task is done. If you discover issues, immediately update <tasklist> with your findings. When resolved, update <tasklist> and remove the item." (at end)
- One-off mode: suppresses both tasklist-related lines; shows user's one-off prompt text in place of task instruction
- Backpressure enabled: includes full IMPORTANT block with test and commit requirements
- Backpressure disabled: omits entire IMPORTANT block
- Breadcrumb enabled: includes breadcrumb instruction with `<breadcrumbs>` reference
- Breadcrumb disabled: omits breadcrumb instruction
- Study docs: rendered as `study <docpath>` for each doc in the list
- Breadcrumbs file: rendered as `check <breadcrumbs>` (lighter emphasis than study)

---

## 2. Persistence & Config

* **Three-tier model:**

  1. Built-in defaults
  2. User-wide config (`~/.geoff/geoff.yaml`)
  3. Repo-local overrides in `.geoff/geoff.yaml`
  
* **Config format:** `geoff.yaml` - structure flexible, add fields as needed.

* **Persistence behavior:**
  - Global config provides baseline defaults
  - Repo-local config starts empty (or doesn't exist)
  - Changes made in TUI save to repo-local `.geoff/geoff.yaml` automatically
  - Each repo maintains isolated state (last-used one-off prompts, doc selections, etc.)
  - To modify global defaults, manually edit `~/.geoff/geoff.yaml`

* **Built-in defaults:**
  - Study docs: `docs/SPEC.md`
  - Tasklist: `docs/PLAN.md`
  - Breadcrumbs: `docs/BREADCRUMBS.md`
  - Backpressure: enabled
  - Breadcrumb: enabled
  - Max iterations: 0

* User has contract to provide files at specified paths; config stores filepath references only.

* Visible effective config recommended to show active values.

---

## 3. Mouse-First TUI Layout

```
+------------------------------------------------------------+
| GEOFF - Prompt Constructor                                 |
+----------------------+-------------------------------------+
| Orientation / Study Docs                                   |
|------------------------------------------------------------|
| Docs: [docs/SPEC.md] [+ Add Doc]                           |
| Breadcrumbs: [docs/BREADCRUMBS.md]                         |
+------------------------------------------------------------+
| Task Source (mutually exclusive, required)                 |
|  (•) Tasklist Mode: [docs/PLAN.md]                         |
|  ( ) One-off Prompt: [                                     |
|                       text area for prompt entry           |
|                      ]                                     |
+------------------------------------------------------------+
| Backpressure                                               
|  [x] Enforce tests & commit
+------------------------------------------------------------+
| Breadcrumb                                                 
|  [x] Leave breadcrumbs
+------------------------------------------------------------+
| Loop Configuration                                         
|  Max iterations: [0]
+------------------------------------------------------------+
| Actions                                                    |
| [Copy Prompt] [Run Once] [Run Loop] [Reset] [Quit]         |
+------------------------------------------------------------+
| Effective Prompt (scrollable, always visible at bottom)    |
| ---------------------------------------------------------  |
| study docs/SPEC.md                                         |
| check docs/BREADCRUMBS.md                                  |
| follow docs/PLAN.md and choose the most important item to  |
| address. Complete that item and no other.                  |
| IMPORTANT:                                                 |
| - After implementing functionality or resolving problems,  |
| run the tests for that unit of code that was improved.     |
| - If functionality is missing then it's your job to add it |
| as per the application specifications.                     |
| - after performing your task run the tests                 |
| - when tests pass, commit to deploy changes                |
| if you ran into difficulties due to lack of info...        |
| Update docs/PLAN.md when the task is done. If you discover |
| issues, immediately update docs/PLAN.md with your findings.|
| When resolved, update docs/PLAN.md and remove the item.    |
| ---------------------------------------------------------  |
```

**Panels:**

* **Left panel:** stacked prompt elements with editable fields.
* **Bottom panel:** scrollable "Effective Prompt" preview (read-only, no auto-scroll, no syntax highlighting).
* **Action toolbar:** always-visible `[Copy] [Run Once] [Run Loop] [Reset] [Quit]`.
* **Error dialogs:** modal dialogs appear for validation failures on attempted run.

---

## 4. Interaction Principles

* **Mouse-first:** all toggles, text fields, and buttons clickable; no keyboard required.

* **Inline editing:** 
  - Click doc fields to edit filepaths directly
  - Click breadcrumbs field to edit filepath directly
  - One-off prompts editable inline **only when one-off mode is active** (multiline text area)
  - Tasklist filepath editable inline **only when tasklist mode is active**
  - Standard text editing supported: Ctrl+C/X/V, text selection, Shift+Enter or Ctrl+Enter for newlines in multiline fields
  - ESC cancels/undos inline edits

* **Mode switching:** 
  - Radio buttons or toggle switches between tasklist and one-off patterns
  - Exactly one mode always selected (mutually exclusive)
  - Switching modes updates effective prompt preview immediately
  - No modal dialogs needed for mode selection

* **Validation:**
  - No real-time validation during editing
  - Validation occurs only on attempted action (Run Once, Run Loop, Copy Prompt)
  - Invalid/empty required filepaths when feature enabled: show modal error dialog
  - Empty breadcrumbs path when breadcrumb checkbox enabled: show modal error dialog
  - Missing task source configuration: show modal error dialog
  - Nonexistent files: show modal error dialog on run attempt
  - All errors allow user to resolve before retrying
  - Copy Prompt validates just like Run actions (same error modals)

* **[+ Add Doc] behavior:**
  - Opens text input for manual filepath entry (relative to execution directory)
  - Docs can be removed after adding (close button `[X]` on each doc chip/field)
  - Breadcrumbs field has no dedicated remove button (always present, can be emptied)

* **Actions:**

  * **Copy Prompt:** copies assembled effective prompt to clipboard (validates first, shows error modal if invalid)
  * **Run Once:** validates prompt, then exits TUI to terminal and executes Opencode with prompt passed directly (not via temp file)
  * **Run Loop:** validates prompt, then exits TUI completely and launches loop that runs Opencode repeatedly until user cancels, max iterations reached, or repo becomes stuck (no changes detected for `max_stuck` consecutive iterations). Loop runs in subprocess outside TUI, does not return to TUI after completion. Before each iteration, computes hash of repository state; after iteration completes, recomputes hash and compares. If hashes match (no changes), increments stuck counter; if hashes differ, resets stuck counter to 0. Breaks loop if stuck counter reaches `max_stuck` (default: 2). Sleeps 2 seconds between iterations. If `max_iterations == 0` (default), runs indefinitely until stuck or manually cancelled. If `max_iterations > 0`, also breaks after reaching iteration limit. Each iteration executes `opencode run "<prompt>" --log-level INFO`.
  * **Reset:** resets all fields to global config defaults (from `~/.geoff/geoff.yaml`)
  * **Quit:** closes TUI

* **Opencode execution:**
  - Prompt passed directly to Opencode (not via temp file)
  - Similar pattern to: `opencode run "<prompt>" --log-level INFO` but with prompt passed inline
  - TUI exits before execution, terminal shows Opencode output directly

* **Loop Implementation:**
  - TUI exits completely when loop starts
  - Loop state managed by bash loop (external to TUI)
  - Loop continues until: (a) user manually cancels, or (b) max iterations reached
  - Max iterations user-configurable in TUI (default: 0 (no limit))
  - Each iteration runs Opencode with the same assembled prompt
  - No return to TUI after loop completes

* **Validation:**
  - Invalid doc paths: show modal error on attempted run
  - Missing task source: show modal error on attempted run
  - Nonexistent tasklist: show modal error on attempted run
  - All errors allow user to resolve before retrying

---

## 5. Defaults

| Element                  | Default / Behavior                         |
| ------------------------ | ------------------------------------------ |
| Orientation / Study Docs | `docs/SPEC.md`; inline editable            |
| Breadcrumbs              | `docs/BREADCRUMBS.md`; inline editable     |
| Task Source              | Tasklist mode; inline editable             |
| Tasklist                 | `docs/PLAN.md`; inline editable            |
| One-off prompt           | Last-used per repo; multiline editable     |
| Backpressure             | Enabled                                    |
| Breadcrumb               | Enabled                                    |
| Max iterations           | 0 (no limit) (user configurable)           |
| Effective Prompt         | Always visible at bottom; scrollable       |

---

## 6. Design Considerations

* Strict ordering avoids misconfiguration; elements are not rearrangeable.

* One-off mode automatically suppresses tasklist-specific elements (study/update tasklist).

* Repo-level `.geoff/geoff.yaml` mirrors git patterns for scoped overrides.

* Multiple TUI instances can run simultaneously in different terminals/repos without conflict (each maintains independent state).

* Loop-run uses external bash harness; agent only sees atomic task.

* All persistent fields editable in-place to reduce friction.

* Textual-based TUI should be visually polished; additional aesthetic pass may be done with agent afterwards.

* Effective Prompt panel is read-only preview; users cannot edit directly in this view.

* Variable substitution (`<docname>`, `<tasklist>`, `<breadcrumbs>`) resolves to user-provided filepaths; user responsible for ensuring files exist at specified locations.

* Should work identically on WSL, native Linux, and macOS (no WSL-specific dependencies).

---

## 7. Implementation Notes

**Multi-instance Support:**
- Multiple Geoff instances can run concurrently in different terminals
- Each instance operates independently on its respective repo
- No shared state between instances beyond filesystem-based config files
- Config file writes are per-repo, avoiding cross-contamination

**Platform Compatibility:**
- Should work identically on WSL, native Linux, and macOS
- No WSL-specific code required
- Standard Unix filesystem conventions assumed