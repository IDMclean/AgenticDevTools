from collections import namedtuple
from functools import lru_cache

# --- Data Structures ---

class Atom(namedtuple('Atom', 'name')):
    def __str__(self):
        return self.name

class LinNeg(namedtuple('LinNeg', 'formula')):
    def __str__(self):
        return f"{self.formula}'"

class ParaNeg(namedtuple('ParaNeg', 'formula')):
    def __str__(self):
        return f"~{self.formula}"

class ParaCompNeg(namedtuple('ParaCompNeg', 'formula')):
    def __str__(self):
        return f"-{self.formula}"

class Consistency(namedtuple('Consistency', 'formula')):
    def __str__(self):
        return f"•{self.formula}"

class Weaken(namedtuple('Weaken', 'formula')):
    def __str__(self):
        return f"?{self.formula}"


Sequent = namedtuple('Sequent', 'antecedent succedent')

# --- Prover Logic ---

@lru_cache(maxsize=None)
def prove(sequent):
    """
    Implements the refined gentle explosion rule: A, ~A, •?A |- ?B
    """
    antecedent = tuple(sequent.antecedent)
    succedent = tuple(sequent.succedent)

    # Strict Axiom Rule: A |- A
    if len(antecedent) == 1 and len(succedent) == 1 and antecedent[0] == succedent[0]:
        return True

    # --- Refined Gentle Explosion Rule ---
    # To prove A, ~A, •?A |- ?B, the proof succeeds.
    if len(succedent) == 1 and isinstance(succedent[0], Weaken):
        # Look for the contradiction A, ~A
        for formula1 in antecedent:
            for formula2 in antecedent:
                if isinstance(formula2, ParaNeg) and formula2.formula == formula1:
                    # Contradiction found. Look for •?A
                    for formula3 in antecedent:
                        if isinstance(formula3, Consistency) and isinstance(formula3.formula, Weaken) and formula3.formula.formula == formula1:
                            return True

    # --- Standard Rules of Inference (applied backwards) ---

    # ~L
    for i, formula in enumerate(antecedent):
        if isinstance(formula, ParaNeg):
            context = antecedent[:i] + antecedent[i+1:]
            new_sequent = Sequent(antecedent=context, succedent=succedent + (formula.formula,))
            if prove(new_sequent):
                return True

    # -R
    for i, formula in enumerate(succedent):
        if isinstance(formula, ParaCompNeg):
            context = succedent[:i] + succedent[i+1:]
            new_sequent = Sequent(antecedent=antecedent + (formula.formula,), succedent=context)
            if prove(new_sequent):
                return True

    # Double Negations (Involutive)
    for i, formula in enumerate(antecedent):
        if isinstance(formula, (ParaNeg, ParaCompNeg)) and isinstance(formula.formula, (ParaNeg, ParaCompNeg)) and type(formula) == type(formula.formula):
            context = antecedent[:i] + antecedent[i+1:]
            new_sequent = Sequent(antecedent=context + (formula.formula.formula,), succedent=succedent)
            if prove(new_sequent):
                return True
    for i, formula in enumerate(succedent):
        if isinstance(formula, (ParaNeg, ParaCompNeg)) and isinstance(formula.formula, (ParaNeg, ParaCompNeg)) and type(formula) == type(formula.formula):
            context = succedent[:i] + succedent[i+1:]
            new_sequent = Sequent(antecedent=antecedent, succedent=context + (formula.formula.formula,))
            if prove(new_sequent):
                return True

    # Linear Negation
    for i, formula in enumerate(antecedent):
        if isinstance(formula, LinNeg):
            context = antecedent[:i] + antecedent[i+1:]
            new_sequent = Sequent(antecedent=context, succedent=succedent + (formula.formula,))
            if prove(new_sequent):
                return True
    for i, formula in enumerate(succedent):
        if isinstance(formula, LinNeg):
            context = succedent[:i] + succedent[i+1:]
            new_sequent = Sequent(antecedent=antecedent + (formula.formula,), succedent=context)
            if prove(new_sequent):
                return True

    return False
