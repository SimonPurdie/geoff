# Findings from Ralph Playbook Comparison

This document outlines potential lessons and improvements for `SPEC.md` based on an analysis of Geoff Huntley's `ralph-playbook`.

---

## 1. Unaddressed Ideas and Philosophies

The `ralph-playbook` introduces several core philosophies and operational details not explicitly covered in `SPEC.md`. Incorporating these could provide a more robust and aligned understanding of agent-driven development.

### 1.1 Context Management and Subagents for Memory Extension
*   **Ralph Playbook Insight**: Emphasizes maximizing "smart zone" context utilization (~40-60% of total tokens), using subagents as a memory extension (each subagent gets ~156kb that's garbage collected) to avoid polluting the main context, and prioritizing brevity for deterministic outputs.
*   **Recommendation**:
    *   Add a section or expand on "Core Concepts" to detail the importance of context efficiency and the strategic use of subagents as memory extensions to manage token limits and maintain focus.
    *   Explicitly state the preference for brevity in inputs to improve determinism.

### 1.2 Explicit "Steering Ralph" Mechanisms
*   **Ralph Playbook Insight**: Details both "upstream" steering (deterministic setup, prompt guardrails, existing code patterns, `AGENTS.md`) and "downstream" backpressure (tests, typechecks, lints, builds, often defined in `AGENTS.md`). `AGENTS.md` is a critical file for project-specific commands that enable immediate self-evaluation.
*   **Recommendation**:
    *   Expand on the "BACKPRESSURE" concept in `SPEC.md` to include a more comprehensive explanation of upstream and downstream steering.
    *   Highlight the role of a dedicated `AGENTS.md` file for defining project-specific build, test, and lint commands, emphasizing its importance in wiring backpressure.

### 1.3 "Let Ralph Ralph" and Security Philosophy
*   **Ralph Playbook Insight**: Advocates for trusting the LLM's ability to self-identify, self-correct, and self-improve, achieving "eventual consistency through iteration." Crucially, this autonomy necessitates sandboxed environments for security, due to the use of `--dangerously-skip-permissions` to bypass interactive tool approval. The philosophy: "It's not if it gets popped, it's when it gets popped. And what is the blast radius?"
*   **Recommendation**:
    *   Introduce a section on the philosophy of "Let Ralph Ralph," explaining the trust in autonomous iteration and the security implications of such autonomy.
    *   Emphasize the critical need for running agents in isolated, sandboxed environments with minimum viable access to protect credentials and private data.

### 1.4 "Move Outside the Loop" and Disposable Plan
*   **Ralph Playbook Insight**: Defines the user's role as an "environment engineer" who observes, tunes, and course-corrects (by adding "signs" for Ralph), rather than directly intervening in each task. A key aspect is the "plan is disposable" philosophy, allowing regeneration of `IMPLEMENTATION_PLAN.md` if the agent goes off track or the plan becomes stale.
*   **Recommendation**:
    *   Add a section describing the user's meta-role in managing the agent's environment and the "disposable plan" concept, including when and why to regenerate `IMPLEMENTATION_PLAN.md`. this is a good stretch goal

### 1.5 Detailed Loop Mechanics and Shared State
*   **Ralph Playbook Insight**: Explains how `loop.sh` acts as an "outer loop" where each iteration is a fresh session for a single task, and `IMPLEMENTATION_PLAN.md` serves as persistent shared state between these isolated runs. It also clarifies the "inner loop" of self-correction within a single task, driven by backpressure until tests pass.
*   **Recommendation**:
    *   Elaborate on "Looped run in Opencode" in `SPEC.md` to clarify the "outer loop" (sequential tasks across fresh sessions) and "inner loop" (self-correction within a task).
    *   Explain how `IMPLEMENTATION_PLAN.md` functions as the persistent shared state between iterations.

### 1.6 Tool-Specific Enhancements from Ralph Playbook

These are concrete, actionable ideas for enhancing the agent's capabilities and workflow, which could be integrated into `SPEC.md` as features or principles.

*   **AskUserQuestionTool for Planning**:
    *   **Insight**: Systematically clarifies requirements (JTBD, edge cases, acceptance criteria) through interactive questioning using Claude's built-in `AskUserQuestionTool` *before* `specs/*.md` are written.
    *   **Recommendation**: Integrate this into the "TASK SOURCE" or "UX Principles" sections as a method for robust requirement definition.

*   **Acceptance-Driven Backpressure**:
    *   **Insight**: Explicitly derives test requirements from acceptance criteria in `specs/*.md` during the planning phase, creating a direct, verifiable link between "what success looks like" and "what verifies it." This prevents "cheating" with placeholder implementations.
    *   **Recommendation**: Enhance the "BACKPRESSURE" element or "Design Considerations" to include the principle of acceptance-driven backpressure and the explicit derivation of test requirements within the `IMPLEMENTATION_PLAN.md`.

*   **Non-Deterministic Backpressure (LLM-as-Judge)**:
    *   **Insight**: Leverages multimodal LLMs as "judges" for subjective acceptance criteria (e.g., creative quality, aesthetics, UX feel) with binary pass/fail results. This extends backpressure to areas traditionally resistant to programmatic validation.
    *   **Recommendation**: Consider adding this as an advanced concept under "BACKPRESSURE" or "Design Considerations," highlighting how `src/lib/llm-review.ts` and `llm-review.test.ts` can demonstrate this pattern.

*   **Ralph-Friendly Work Branches**:
    *   **Insight**: Promotes scoping `IMPLEMENTATION_PLAN.md` upfront for specific work branches (using a `plan-work` mode) to ensure deterministic task selection. This avoids unreliable runtime filtering of tasks.
    *   **Recommendation**: Incorporate this workflow enhancement into "Execution Modes" or "Design Considerations" to guide users on effective branch-based development with the agent.

### 1.7 Specific Phrasing and Directives

*   **"Ultrathink"**: A keyword used in Geoff's prompts to encourage deeper reasoning.
*   **Subagent Allocation**: Specific directives like "up to 250 parallel Sonnet subagents" for studies/reads and "only 1 Sonnet subagent for build/tests" for backpressure control.
*   **"Capture the why"**: Repeated emphasis on capturing the rationale behind decisions, especially in documentation and commit messages.
*   **"Don't assume not implemented"**: A critical guardrail to ensure the agent always searches the codebase before attempting to implement something new.
*   **"Study" vs. "read"**: The playbook uses "study" more actively, implying deeper analysis.
*   **"Implement functionality completely. Placeholders and stubs waste efforts and time redoing the same work."**: A strong directive against partial implementations.

---

## 2. Areas for Improved Wording

Based on Geoff Huntley's playbook, `SPEC.md` could be refined for clarity, emphasis, and adherence to specific terminology.

### 2.1 Consistent Terminology
*   **Ralph Playbook**: Defines terms like "Job to be Done (JTBD)," "Topic of Concern," "Spec," and "Task" with clear relationships.
*   **Recommendation**: `SPEC.md` could benefit from explicitly defining these terms or aligning its "Elements" with these concepts for clearer communication, especially in "Core Concepts."

### 2.2 Emphasis on "Why"
*   **Ralph Playbook**: Consistently explains the rationale ("why") behind principles (e.g., why context is critical, why sandboxing is necessary).
*   **Recommendation**: Enrich `SPEC.md` with more explanations of the "why" behind its design choices, drawing from the philosophical underpinnings in the `ralph-playbook`. For example, *why* strict ordering is fixed, or *why* repo-local overrides are important.

### 2.3 Clearer Guardrails and Invariants
*   **Ralph Playbook**: Uses numbered "999..." sequences in prompts to denote critical guardrails and invariants.
*   **Recommendation**: While "Design Considerations" covers some of this, `SPEC.md` could explicitly state key invariant principles (e.g., for security, task completion, or data integrity) in a more prominent and unambiguous manner, perhaps adopting a similar "guardrail" section.

### 2.4 Active Verbs for Agent Instructions
*   **Ralph Playbook**: Frequently uses active verbs like "study" (implying deeper understanding), "orient," "select," "investigate," "implement," "validate."
*   **Recommendation**: Review `SPEC.md` for opportunities to use more active and directive language when describing agent actions or tool interactions, mirroring the directness seen in Geoff's prompts.

### 2.5 Promote Complete Implementations
*   **Ralph Playbook**: "Implement functionality completely. Placeholders and stubs waste efforts and time redoing the same work."
*   **Recommendation**: Add a strong statement in `SPEC.md` encouraging complete implementations and discouraging placeholders, possibly in "Design Considerations" or "UX Principles" if it relates to friction.