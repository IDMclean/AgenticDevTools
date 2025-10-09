# Post-Mortem Report: [Task Name/ID]

**Task ID:** `[UUID]`
**Completion Date:** `[ISO_8601_TIMESTAMP]`

---

## 1. Objective

*A concise, one-sentence description of the goal of this task.*

---

## 2. Plan vs. Reality Analysis

### Initial Plan Summary
*Provide a high-level summary of the initial, validated plan.*

### Execution Analysis
*Analyze the `activity.log.jsonl` for this task. Compare the executed steps against the initial plan. Note any significant deviations, unexpected errors, or inefficiencies.*

-   **Deviations from Plan:** *Did the agent have to take unplanned steps? Why?*
-   **Tool Failures/Retries:** *Which tools failed or required retries? What was the root cause?*
-   **Inefficient Queries:** *Were any RAG queries (internal or external) ineffective or noisy? How could they be improved?*

---

## 3. Root Cause Analysis

*For the most significant deviations or failures identified above, perform a root cause analysis. What was the fundamental breakdown?*

-   **Finding 1:**
    -   **Symptom:** *e.g., The agent tried to use a deprecated API.*
    -   **Root Cause:** *e.g., The "Temporal Orientation" phase failed to retrieve the latest version of the library's documentation, causing the agent to rely on its outdated internal knowledge.*

-   **Finding 2:**
    -   **Symptom:**
    -   **Root Cause:**

---

## 4. Actionable Lessons for Future Tasks

*Based on the root cause analysis, generate concrete, actionable lessons. Each lesson should be a clear directive that can inform future planning and execution.*

### Lesson 1:
**Observation:** *e.g., Semantic search on `llms.txt` for "database connection" returned outdated information.*
**Directive:** *e.g., Future plans must prioritize external RAG for library-specific configurations over internal conceptual documents. The internal documents are for architectural principles, not implementation details.*

### Lesson 2:
**Observation:**
**Directive:**

---

## 5. Knowledge Core Update Recommendations

*Suggest specific updates to the Knowledge Core artifacts that would have prevented the failures in this task.*

-   **Artifact:** `[e.g., knowledge_core/llms.txt]`
    **Recommendation:** `[e.g., Add a new section clarifying the project's official database connection strategy and deprecating the old method.]`

-   **Artifact:** `[e.g., tooling/custom-linters]`
    **Recommendation:** `[e.g., Develop a new linter to detect usage of the now-deprecated `connect_db()` function.]`