# A Belief State Model for Paraconsistent Agents

## 1. Introduction

This document specifies a "Belief State" model for an agent that can reason with inconsistency and undeterminedness. This model is a departure from the classical "world state" model, which can only represent a single, consistent state of the world. The Belief State model, by contrast, can represent a set of beliefs about the world, which may be inconsistent or incomplete.

## 2. The Belief Set

The core of the Belief State model is the "Belief Set," which is a set of "Beliefs." A Belief is a pair `(fact, value)`, where `fact` is a proposition and `value` is one of the following four values:

*   `TRUE`: The agent believes the fact to be true.
*   `FALSE`: The agent believes the fact to be false.
*   `INCONSISTENT`: The agent believes the fact to be both true and false.
*   `UNDETERMINED`: The agent has no belief about the fact.

## 3. Operations on the Belief Set

The Belief Set is manipulated by a set of operations that are based on the principles of paraconsistent logic. These operations allow the agent to update its beliefs in a way that is consistent with the evidence it has observed.

### 3.1. `add_belief(fact, value)`

This operation adds a new belief to the Belief Set. If a belief about the fact already exists, the new belief is merged with the existing belief according to the following rules:

| Existing Value | New Value | Merged Value |
| :--- | :--- | :--- |
| `TRUE` | `TRUE` | `TRUE` |
| `TRUE` | `FALSE` | `INCONSISTENT` |
| `FALSE` | `TRUE` | `INCONSISTENT` |
| `FALSE` | `FALSE` | `FALSE` |
| `INCONSISTENT`| any | `INCONSISTENT` |
| `UNDETERMINED`| any | new value |

### 3.2. `query_belief(fact)`

This operation returns the value of a belief in the Belief Set. If no belief about the fact exists, it returns `UNDETERMINED`.

## 4. Conclusion

The Belief State model is a powerful tool for building agents that can reason with inconsistency and undeterminedness. It is a key component of the `Jules_v2` architecture, and it is essential for creating an agent that can survive and thrive in the paradoxical world of the `SynthPlayground`.
