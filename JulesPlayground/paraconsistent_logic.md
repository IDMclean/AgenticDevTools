# Formalization of the Non-Classical Logic of APPL

## 1. Introduction

This document provides a formalization of the non-classical logic that underpins the APPL language. This logic, which we will call Paradefinite Light Linear Logic (PLLL), is a substructural logic that integrates principles from Logics of Formal Inconsistency (LFI) and Logics of Formal Undeterminedness (LFU) into the framework of Light Linear Logic (LLL).

## 2. Syntax

The language of PLLL is an extension of the language of propositional Light Linear Logic. In addition to the standard connectives of LLL, we add four new unary operators:

*   **Paraconsistent Negation:** `~A`
*   **Consistency Operator:** `oA`
*   **Paracomplete Co-negation:** `-A`
*   **Undeterminedness Operator:** `*A`

## 3. Semantics

The semantics of PLLL are defined by a set of inference rules in a Gentzen-style sequent calculus. The core of the logic is the principle of "gentle explosion," which states that a contradiction only leads to triviality in the presence of an explicit assertion of consistency.

### 3.1. Core Inference Rules

The following are the core inference rules for the paradefinite operators:

| Operator | Rule Name | Inference Rule |
| :--- | :--- | :--- |
| **Paraconsistent** | `~R` | `Γ, A' ⊢ Δ` / `Γ, ~A ⊢ Δ` |
| **Negation (~)** | `~L` | `Γ ⊢ Δ, A` / `Γ ⊢ Δ, (~A)'` |
| **Consistency (o)** | `oR` | `Γ ⊢ Δ, A` and `Γ ⊢ Δ, ~A` / `Γ ⊢ Δ, oA` |
| **(Gentle Explosion)** | `oL` | `Γ, A, ~A, oA ⊢ Δ` |
| **Paracomplete** | `-R` | `Γ, A ⊢ Δ` / `Γ, -A ⊢ Δ` |
| **Co-negation (-)** | `-L` | `Γ ⊢ Δ, A'` / `Γ ⊢ Δ, (-A)'` |
| **Undeterminedness (*)**| `*R` | `Γ ⊢ Δ, A, -A` / `Γ ⊢ Δ, *A` |
| **(Gentle Excluded Middle)**| `*L` | `Γ, *A ⊢ Δ, A` and `Γ, *A ⊢ Δ, -A` |

### 3.2. Interaction Rules

The interaction rules govern the behavior of the paradefinite operators with respect to the additive, multiplicative, and exponential connectives of LLL. These rules are designed to preserve the resource-sensitive nature of the logic.

#### 3.2.1. Additives

*   `o(&)-Intro`: `Γ ⊢ Δ, oA` and `Γ ⊢ Δ, oB` / `Γ ⊢ Δ, o(A & B)`
*   `*(+)-Intro`: `Γ ⊢ Δ, *A, *B` / `Γ ⊢ Δ, *(A + B)`

#### 3.2.2. Multiplicatives

*   `o(x)-Intro`: `Γ ⊢ Δ, oA` and `Γ' ⊢ Δ', oB` / `Γ, Γ' ⊢ Δ, Δ', o(A x B)`
*   `*(par)-Intro`: `Γ ⊢ Δ, *A` and `Γ' ⊢ Δ', *B` / `Γ, Γ' ⊢ Δ, Δ', *(A par B)`

#### 3.2.3. Exponentials

*   `!oR`: `?Γ ⊢ oA, ?Δ` / `?Γ ⊢ !(oA), ?Δ`
*   `!o-distrib`: `Γ ⊢ !oA, Δ` / `Γ ⊢ o!A, Δ`

## 4. Conclusion

This formalization of PLLL provides a solid foundation for understanding the logic of the APPL language. It is a powerful and expressive logic that is well-suited for reasoning about complex and uncertain domains.
