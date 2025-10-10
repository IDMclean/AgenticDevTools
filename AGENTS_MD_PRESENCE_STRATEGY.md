# Analysis of Architectures for Ensuring AGENTS.md Presence (Revised)

This document deliberates on architectural approaches to guarantee a valid `AGENTS.md` file is always present at the moment a Google Jules coding session begins, incorporating critical constraints regarding merge conflicts and a lack of control over the agent's execution environment.

## 1. The Problem: Core Constraints and Risks

The `AGENTS.md` file is the foundational charter for the agent's behavior. An "instruction gap"—caused by a missing, invalid, or incomplete file—can lead to unpredictable behavior. The architectural solution must address two core, real-world constraints:

1.  **High Probability of Merge Conflicts:** As a central, frequently updated file, `AGENTS.md` is a natural hotspot for merge conflicts when combining different branches or repositories. Manual resolution of these conflicts is not an option.
2.  **Inaccessible Startup Environment:** The agent's session initialization process is a black box. We cannot add custom validation hooks or scripts that run before the agent's code, so the solution must be entirely self-contained within the repository's state and CI/CD process.

## 2. Mitigating Merge Conflicts: The Directory-Based Approach

The most effective way to mitigate merge conflicts on a central configuration file is to decompose it. Instead of a single, monolithic `AGENTS.md` file, we can use a directory-based approach.

-   **Description:** We introduce a directory named `agents.md.d/`. Different modules, teams, or automated processes can add, update, or remove their own specific instruction snippets as separate files within this directory (e.g., `01-core-protocol.md`, `02-react-guidelines.md`). A CI/CD process is then responsible for concatenating the contents of these files in a deterministic order (e.g., alphanumeric) to generate the final `AGENTS.md` file.

-   **Pros:**
    -   **Drastically Reduces Merge Conflicts:** Different features or branches can add their own instruction files without touching a central file, virtually eliminating conflicts. A conflict would only occur if two branches modify the *exact same* snippet file.
    -   **Modularity and Ownership:** Allows for clear ownership of different parts of the agent's instructions.

-   **Cons:**
    -   **Requires Build Step:** Introduces a mandatory CI step to generate the final `AGENTS.md`. The agent cannot operate on a branch where this step hasn't been run.
    -   **Order Dependency:** The concatenation order must be explicit and well-managed to ensure a coherent final instruction set.

## 3. Revised Architectural Proposals

Given the constraints, the viable architectures must operate within the Git repository and its associated CI/CD system.

### Architecture A: CI-Managed Generative Workflow

This approach makes the `AGENTS.md` file a build artifact, generated from the `agents.md.d/` directory.

-   **Description:**
    1.  All agent instructions are managed as individual files within the `agents.md.d/` directory.
    2.  A CI workflow, triggered on every commit, runs a script that concatenates the files from `agents.md.d/` into a single `AGENTS.md` file.
    3.  This generated `AGENTS.md` is committed back to the branch. The `AGENTS.md` file itself is still tracked by Git to ensure it's present at checkout time.
    4.  `.gitignore` should contain `!/AGENTS.md` to ensure it is always included.

-   **Pros:**
    -   **Conflict Resilient:** The source of truth is distributed across many files, minimizing merge conflicts.
    -   **Always Present:** Because the generated file is committed to the repo, any `git checkout` will contain a complete and ready-to-use `AGENTS.md`.

-   **Cons:**
    -   **CI Complexity:** Requires a CI process that has write/commit access to the repository.
    -   **Potential for "Stale" Artifacts:** If a developer works on a branch without running the CI process, the `AGENTS.md` could become out of sync with the contents of `agents.md.d/`.

### Architecture B: CI-Based Validation Gate

This approach focuses on preventing invalid states from ever entering the main branch.

-   **Description:** A CI workflow is configured as a *required status check* for merging any pull request into the main branch. This CI job does not write to the repository; it only performs validation. The check will:
    1.  Verify that `AGENTS.md` exists and is not empty.
    2.  (If using the directory approach) Verify that `AGENTS.md` is an up-to-date concatenation of the files in `agents.md.d/`. If not, it fails the build and instructs the developer to run the generation script.
    3.  Perform linting or other semantic validation on the file.
    If any check fails, the PR is blocked from merging, effectively preventing an "instruction gap" in the main line of development.

-   **Pros:**
    -   **Strong Guarantee for Main Branch:** Provides a very strong guarantee that the `main` branch will never be in a state with a missing or invalid `AGENTS.md`.
    -   **No Write Access Needed:** Simpler and more secure CI setup, as the validator only needs read access.

-   **Cons:**
    -   **No Guarantee on Feature Branches:** Developers can still create broken states on their own feature branches. The agent could still encounter an "instruction gap" if it is deployed on a feature branch for testing before that branch has been validated.

## 4. Revised Recommendation: A Robust Hybrid Strategy

The optimal strategy is a hybrid that combines the merge-conflict resilience of the directory-based approach with the safety of a CI validation gate.

1.  **Implement the Directory-Based Approach:** All agent instructions MUST be managed in snippet files within an `agents.md.d/` directory. This is the primary strategy for preventing merge conflicts.

2.  **Provide a Local Generation Script:** Include a simple, easy-to-run script (e.g., `make agent_instructions` or `npm run build:agents-md`) that developers can use to regenerate the `AGENTS.md` file locally after modifying any snippets.

3.  **Enforce with a CI Validation Gate (Architecture B):** Make a CI status check mandatory for all pull requests. This check runs the generation script and compares its output with the `AGENTS.md` file checked into the branch. If there is a diff, the check fails. This ensures that no PR is merged with a stale `AGENTS.md`, effectively forcing developers to run the generation script before merging.

This hybrid model provides the highest level of assurance possible given the constraints:

-   It **solves the merge conflict problem** by design.
-   It **guarantees the main branch is always valid** through a non-bypassable CI gate.
-   It **operates entirely within the repository and its CI system**, requiring no access to the agent's external environment.
-   It keeps the `AGENTS.md` file as a checked-in artifact, ensuring it is **always present at checkout time**, avoiding the need for a build step before the agent can run.