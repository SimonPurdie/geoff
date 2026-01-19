# Geoff — TUI Prompt Constructor Spec

**Purpose:**
Personal productivity tool for composing, persisting, and executing coding-agent prompts in WSL. Focused on low-friction mouse-first configuration, reusable prompt elements, and seamless execution in Opencode.

---

## 1. Core Concepts

**Prompt Elements (strict fixed order):**

1. **Orientation / Study Docs**

   ```
   study <docname> <optional docnote>
   ```

   * Multiple docs supported; add/remove inline via `[+ Add Doc]`.
   * Persisted per repo or last-used globally; editable in-place.

2. **Task Source (modal, required)** — choose one:

   * **Tasklist-driven:**

     ```
     study <tasklist> and pick the most important thing to do.
     ```
   * **One-off prompt (ephemeral):**

     * Last-used persisted; editable inline.
     * Entered via modal or inline text box.

3. **Backpressure**

   ```
   IMPORTANT:
   - author property based tests or unit tests (whichever is best)
   - after performing your task run the tests
   - when tests pass, commit to deploy changes
   ```

   * Enabled by default; toggle via checkbox.

4. **Breadcrumb**

   ```
   if you ran into difficulties due to a lack of information about the project or environment, which you then resolved, leave a note about it in <notedoc> to help future agents.
   ```

   * Enabled by default; toggle via checkbox.

5. **Task Update**

   ```
   update <tasklist> when the task is done
   ```

   * Automatically linked to tasklist mode; no separate checkbox.

**Ordering:** Orientation → Task Source → Backpressure → Breadcrumb → Task Update (implicit)

---

## 2. Persistence & Config

* **Three-tier model:**

  1. Built-in defaults
  2. User-wide config
  3. Repo-local overrides in `.geoff/` folder
* All docs, tasklists, variables, and one-off prompts are persisted and editable.
* Visible effective config recommended to show overrides.

---

## 3. Mouse-First TUI Layout

```
+-------------------------------------------------------------+
| GEOFF - Prompt Constructor                                  |
+----------------------+--------------------------------------+
| Orientation / Study Docs                                    |
|-------------------------------------------------------------|
| Docs: [docs/PROJECT.md] [docs/TUI_REFACTOR.md] [+ Add Doc] |
| Notes: [docs/NOTES.md]                                      |
+----------------------+
| Task Source (modal, required)                               |
|  (•) Tasklist Mode                                         |
|  ( ) One-off Prompt                                        |
|  [Select Tasklist / Enter One-off Prompt]                  |
+----------------------+
| Backpressure                                               
|  [x] Enforce tests & commit
+----------------------+
| Breadcrumb                                                 
|  [x] Leave notes for future agents
+----------------------+
| Actions                                                     |
| [Copy Prompt] [Run Once] [Run Loop] [Quit]                 |
+----------------------+
| Effective Prompt (scrollable, always visible at bottom)    |
| --------------------------------------------------------- |
| study docs/PROJECT.md # to orient yourself                |
| study docs/TUI_REFACTOR.md # current feature spec         |
| check docs/NOTES.md # previous agents may have left info  |
| IMPORTANT:                                                |
| - author property based tests or unit tests (whichever)   |
| - after performing your task run the tests                |
| - when tests pass, commit to deploy changes              |
| if you ran into difficulties due to lack of info...       |
| update <tasklist> when the task is done                   |
| --------------------------------------------------------- |
```

**Panels:**

* **Left panel:** stacked prompt elements with editable fields.
* **Bottom panel:** scrollable “Effective Prompt” preview.
* **Action toolbar:** always-visible `[Copy] [Run Once] [Run Loop] [Quit]`.
* **Modals:** task source selection or ephemeral one-off prompt input.

---

## 4. Interaction Principles

* **Mouse-first:** all toggles, text fields, and buttons clickable; no keyboard required.
* **Inline editing:** click doc fields or one-off prompts to edit directly.
* **Modal flows:** task source selection pops automatically if missing.
* **Actions:**

  * **Copy Prompt:** copies assembled prompt to clipboard
  * **Run Once / Run Loop:** exits TUI to terminal, where Opencode output is displayed
  * **Quit:** closes TUI

---

## 5. Defaults

| Element                  | Default / Behavior                         |
| ------------------------ | ------------------------------------------ |
| Orientation / Study Docs | Last-used doc(s); inline editable          |
| Task Source              | Tasklist mode if tasks exist, else one-off |
| Backpressure             | Enabled                                    |
| Task Update              | Linked automatically to tasklist mode      |
| Breadcrumb               | Enabled                                    |
| Loop-run                 | Disabled; configurable via menu            |
| Effective Prompt         | Always visible at bottom; scrollable       |

---

## 6. Design Considerations

* Strict ordering avoids misconfiguration; elements are not rearrangeable.
* One-off mode disables tasklist-specific elements automatically.
* Repo-level `.geoff` folder mirrors git patterns for scoped overrides.
* Loop-run uses external harness; agent only sees atomic task.
* All persistent fields editable in-place to reduce friction.
