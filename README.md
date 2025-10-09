# The Symbiont Development Environment

## Overview

This repository is a cutting-edge development environment designed for a symbiotic partnership between a human developer and the AI agent, Jules. The primary objective is to create a self-aware, self-improving system where Jules can autonomously execute and learn from complex software engineering tasks.

The core of this environment is a meticulously engineered architecture that provides Jules with a persistent, external "memory" and a rigorous, multi-stage protocol for task execution. This system is designed to overcome the inherent limitations of Large Language Models by grounding the agent in a rich, automatically updated model of the codebase and the current state of external technologies.

## Core Architecture: The Agent and its Knowledge Core

The agent's operation is governed by a detailed protocol that structures its entire workflow, from understanding the task to learning from the outcome. This process is powered by the **Knowledge Core**, a dedicated directory of machine-readable artifacts that function as the agent's external world model.

### The Agent Protocol (`AGENTS.md`)

All of the agent's work is guided by the master protocol defined in `AGENTS.md`. This is not a static document but a detailed, algorithm-like set of instructions that dictates how the agent reasons about and executes tasks. The protocol is divided into six distinct phases:

1.  **Phase 1: Temporal Orientation:** The agent orients itself to the current state of external technologies, mitigating its outdated internal knowledge.
2.  **Phase 2: Deconstruction & Internal Contextualization:** The agent analyzes the task and uses the Knowledge Core to understand the relevant code entities and their dependencies.
3.  **Phase 3: Multi-Modal Information Retrieval (RAG):** The agent gathers deep context by querying internal knowledge artifacts (ASTs, conceptual docs) and performing Just-In-Time external web searches for the latest best practices.
4.  **Phase 4: Planning & Self-Correction:** The agent generates a detailed, evidence-based plan and uses an internal "critic" to rigorously verify and refine it.
5.  **Phase 5: Execution & Logging:** The agent executes the validated plan, logging every action in a structured, machine-readable format for later analysis.
6.  **Phase 6: Post-Mortem & Knowledge Update:** The agent analyzes the results of its work to identify lessons and improve its future performance.

### The Knowledge Core (`knowledge_core/`)

This directory is the heart of the agent's "awareness." It contains a suite of artifacts that are automatically generated and updated by CI/CD workflows, ensuring the agent always has an accurate model of the repository.

-   **`dependency_graph.json`**: An explicit, repository-wide dependency graph.
-   **`symbols.json`**: A universal symbol map for precise code navigation.
-   **`asts/`**: A directory of Abstract Syntax Trees for deep structural analysis of code.
-   **`llms.txt`**: A curated, LLM-friendly corpus of project-specific documentation.
-   **`temporal_orientation.md`**: A cached summary of the current state of external technologies.

## The Self-Improvement Loop

This environment is designed for continuous learning. The agent's key feedback mechanisms are:

-   **Structured Logging (`logs/activity.log.jsonl`):** Every action, query, and decision is logged in a machine-readable format, creating a rich dataset of the agent's problem-solving process.
-   **Post-Mortems (`postmortem.md`):** At the end of each task, the agent analyzes its performance to identify successes, failures, and root causes.
-   **Meta-RAG:** The agent is required to consult its own past activity logs and post-mortems when starting a new task, allowing it to learn from its own history and avoid repeating mistakes.

This closed-loop system of **Context -> Action -> Reflection -> Learning** is what makes this a true Symbiont Environment, where the agent's capabilities grow with every task it performs.