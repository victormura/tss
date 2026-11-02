"""
Demonstrație Programatică a Cerinței 6 (Mutant Omorât vs. Neomorât)
Autor: Natalia Moroz (50% contribuție)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mutants")))

from parking_gate import EmployeeTier, AccessDecision, evaluate_parking_access
from manual_mutants import evaluate_parking_access_mutant_killed, evaluate_parking_access_mutant_survived


class TestManualMutantsVerification:

    def test_original_program_behavior(self):
        """Programul original returnează corect DENIED_QUOTA_EXCEEDED la test_bva_occupied_exactly_at_quota."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=12,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_mutant_killed_is_detected_and_fails(self):
        """
        Mutantul 1 (< transformat în <=):
        Testul original se așteaptă la DENIED_QUOTA_EXCEEDED.
        Dar mutantul returnează GRANTED_REGULAR!
        Prin urmare, testul eșuează -> MUTANTUL ESTE OMORÂT (Killed).
        """
        mutant_res = evaluate_parking_access_mutant_killed(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=12,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        # Verificăm că mutantul produce un rezultat diferit (anomalie detectată de test)
        assert mutant_res != AccessDecision.DENIED_QUOTA_EXCEEDED
        assert mutant_res == AccessDecision.GRANTED_REGULAR

    def test_mutant_survived_escapes_this_test(self):
        """
        Mutantul 2 (overflow_count < 5 transformat în < 4):
        Pentru acest caz de test, company_allows_overflow = False.
        Mutantul returnează exact DENIED_QUOTA_EXCEEDED (același ca originalul).
        Testul trece neobservat -> MUTANTUL SUPRAVIEȚUIEȘTE (Survived).
        """
        mutant_res = evaluate_parking_access_mutant_survived(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=12,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        # Testul nu observă diferența
        assert mutant_res == AccessDecision.DENIED_QUOTA_EXCEEDED
