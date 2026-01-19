This stuff is not to be implemented without express user approval. Agents get out of here, this file isnt for you.

# PLANNING, HOW TO PLAN, PLANMAKING PROMPTS, that sort of thing
*   **AskUserQuestionTool for Planning**:
    *   **Insight**: Systematically clarifies requirements (JTBD, edge cases, acceptance criteria) through interactive questioning using Claude's built-in `AskUserQuestionTool` *before* `specs/*.md` are written.
    *   **Recommendation**: Integrate this into the "TASK SOURCE" or "UX Principles" sections as a method for robust requirement definition.


#  Better Backpressure
    *   **Acceptance-Driven Backpressure**:
    *   **Insight**: Explicitly derives test requirements from acceptance criteria in `specs/*.md` during the planning phase, creating a direct, verifiable link between "what success looks like" and "what verifies it." This prevents "cheating" with placeholder implementations.
    *   **Recommendation**: Enhance the "BACKPRESSURE" element or "Design Considerations" to include the principle of acceptance-driven backpressure and the explicit derivation of test requirements within the `IMPLEMENTATION_PLAN.md`.

*   **Non-Deterministic Backpressure (LLM-as-Judge)**:
    *   **Insight**: Leverages multimodal LLMs as "judges" for subjective acceptance criteria (e.g., creative quality, aesthetics, UX feel) with binary pass/fail results. This extends backpressure to areas traditionally resistant to programmatic validation.
    *   **Recommendation**: Consider adding this as an advanced concept under "BACKPRESSURE" or "Design Considerations," highlighting how `src/lib/llm-review.ts` and `llm-review.test.ts` can demonstrate this pattern.
