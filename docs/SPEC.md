# Geoff — Prompt Construction & Execution Tool (WSL)

**Purpose:**
A personal productivity tool for composing, persisting, and executing coding-agent prompts. Enables low-friction reuse of structured prompt elements, with optional looping execution in Opencode.

---

## 1. Core Concepts

**Elements:**
Named, reusable pieces of prompts with strict ordering. Persistent variables are editable, “sticky,” and scoped to global defaults, user config, or per-repo `.geoff` overrides.

* **PROJECT ORIENTATION**

  ```
  study <docname> <optional docnote>
  ```
* **TASK SOURCE (modal, required)** — choose one:

  * **Tasklist-driven**: agent selects from a persisted tasklist

    ```
    study <tasklist> and pick the most important thing to do.
    ```
  * **One-off prompt**: ephemeral user-supplied instruction (persisted, editable, last-used remembered)
* **BACKPRESSURE**

  ```
  IMPORTANT:
  - author property based tests or unit tests (whichever is best)
  - after performing your task run the tests
  - when tests pass, commit to deploy changes
  ```
* **TASK UPDATE** (only valid in tasklist mode)

  ```
  update <tasklist> when the task is done
  ```
* **BREADCRUMB**

  ```
  if you ran into difficulties due to a lack of information about the project or environment, which you then resolved, leave a note about it in <notedoc> to help future agents.
  ```

**Ordering is fixed:** Orientation → Task Source → Backpressure → Bookkeeping.

---

## 2. Persistence & Config

* **Global defaults** (built-in)
* **User-wide config**
* **Repo-local overrides** in `.geoff/` folder
* All doc fields, tasklists, and one-off prompts are persisted and easily editable.
* **Visible effective config** view recommended to prevent surprises.

---

## 3. Execution Modes

1. **Copy to clipboard** — for external use
2. **Single-run in Opencode** — executes the prompt once
3. **Looped run in Opencode** — external harness script:

   * Computes repo hash to detect progress
   * Stops if “stuck” for configurable iterations
   * Independent of agent knowledge; agent sees only atomic task

---

## 4. UX Principles

* Minimal friction: all persistent variables editable in-place
* Modal task source prevents incompatible element combinations
* Defaults to last-used tasklist or one-off prompt
* No need for named one-offs; they are ephemeral

---

## 5. Design Considerations

* Strict ordering avoids complexity; elements are not rearrangeable
* Tasklist mode enforces paired TASK SELECTION + TASK UPDATE
* One-off mode disables tasklist-related elements
* Repo-level `.geoff` folder provides scoped overrides, mirroring git patterns
* Loop execution treats repo-level changes as progress, independent of task semantics
