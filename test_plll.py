import pytest
from plll_prover import prove, Sequent, Atom, LinNeg, ParaNeg, ParaCompNeg, Consistency, Weaken

# --- Test Fixtures ---

@pytest.fixture
def A(): return Atom('A')
@pytest.fixture
def B(): return Atom('B')

# --- Tests for the Refined Gentle Explosion ---

def test_refined_gentle_explosion_succeeds(A, B):
    """Refined Gentle Explosion: A, ~A, •?A |- ?B should be provable"""
    antecedent = (A, ParaNeg(A), Consistency(Weaken(A)))
    succedent = (Weaken(B),)
    assert prove(Sequent(antecedent, succedent))

def test_refined_gentle_explosion_fails_without_weakened_succedent(A, B):
    """Refined Gentle Explosion Fails: A, ~A, •?A |- B should NOT be provable"""
    antecedent = (A, ParaNeg(A), Consistency(Weaken(A)))
    succedent = (B,)
    assert prove(Sequent(antecedent, succedent)) == False

def test_gentle_explosion_fails_without_modality(A, B):
    """Gentle Explosion Fails: A, ~A, •A |- ?B should NOT be provable"""
    antecedent = (A, ParaNeg(A), Consistency(A))
    succedent = (Weaken(B),)
    assert prove(Sequent(antecedent, succedent)) == False

def test_standard_explosion_still_fails(A, B):
    """Standard Explosion: A, ~A |- B should still NOT be provable"""
    antecedent = (A, ParaNeg(A))
    succedent = (B,)
    assert prove(Sequent(antecedent, succedent)) == False
