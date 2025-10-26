# Specification for a Semantic Interpreter

## 1. Introduction

This document specifies a "Semantic" Interpreter for the APPL language. This interpreter is a departure from the classical, syntactic interpreter, which crashes on contradiction. The Semantic Interpreter, by contrast, is designed to handle inconsistency and undeterminedness by updating its "Belief State" rather than halting.

## 2. The Belief State

The Semantic Interpreter operates on a "Belief State," as defined in the `belief_state.md` document. The Belief State is a set of beliefs about facts, where each belief can be `TRUE`, `FALSE`, `INCONSISTENT`, or `UNDETERMINED`.

## 3. The Interpretation Process

The Semantic Interpreter traverses the AST of an APPL program and updates the Belief State based on the semantics of the language. The key difference between the Semantic Interpreter and a classical interpreter is how it handles contradictions.

### 3.1. Handling Contradictions

When a classical interpreter encounters a contradiction (e.g., a fact is asserted to be both true and false), it crashes. The Semantic Interpreter, by contrast, handles contradictions by updating the Belief State.

For example, if the interpreter encounters the assertion `p` and the assertion `~p`, it will update the Belief State to `(p, INCONSISTENT)`. This allows the interpreter to continue processing the program, and it provides the agent with valuable information about the consistency of its own beliefs.

### 3.2. The `eval` Primitive

The `eval` primitive in the Semantic Interpreter is also different from the `eval` primitive in a classical interpreter. In a classical interpreter, `eval` executes a program and returns a value. In the Semantic Interpreter, `eval` executes a program and returns a new Belief State.

This allows the agent to reason about the consequences of its actions. For example, the agent can use `eval` to simulate the execution of a plan and to see how it would affect its beliefs about the world.

## 4. Conclusion

The Semantic Interpreter is a key component of the `Jules_v2` architecture. It is a powerful tool for building agents that can reason with inconsistency and undeterminedness, and it is essential for creating an agent that can survive and thrive in the paradoxical world of the `SynthPlayground`.
