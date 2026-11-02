"""
Verificarea Proprietății de Echivalență a Mutantului (Cerința 5)
Autor: Victor Mura (50% contribuție)
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mutants")))

from parking_gate import EmployeeTier, AccessDecision, evaluate_parking_access
from equivalent_mutant import evaluate_parking_access_equivalent_mutant


class TestEquivalentMutantVerification:

    @pytest.mark.parametrize("hour", list(range(0, 24)))
    def test_equivalence_across_all_24_hours(self, hour):
        """
        Testează exhaustiv pentru fiecare oră din intervalul [0, 23] că
        programul original și mutantul echivalent produc exact același rezultat.
        """
        for tier in EmployeeTier:
            for is_ev in (True, False):
                for has_spots in (True, False):
                    for allows_ovf in (True, False):
                        # Cazul 1: Sub cotă
                        orig_sub = evaluate_parking_access(10, 5, hour, tier, is_ev, has_spots, allows_ovf)
                        mut_sub = evaluate_parking_access_equivalent_mutant(10, 5, hour, tier, is_ev, has_spots, allows_ovf)
                        assert orig_sub == mut_sub

                        # Cazul 2: Peste cotă
                        orig_over = evaluate_parking_access(10, 12, hour, tier, is_ev, has_spots, allows_ovf)
                        mut_over = evaluate_parking_access_equivalent_mutant(10, 12, hour, tier, is_ev, has_spots, allows_ovf)
                        assert orig_over == mut_over
