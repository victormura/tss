"""
Cerința 4: Modified Condition / Decision Coverage (MC/DC)
Autor: Natalia Moroz (50% contribuție)

Decizia compusă analizată (Regula 3 - Stații EV):
  Decision = (A and B) and (not C or D)
unde:
  A = is_electric_vehicle
  B = has_ev_spots_available
  C = is_peak_hours
  D = is_within_quota (company_current_occupied < company_allocated_quota)

Setul minimal de 5 teste MC/DC (N + 1 pentru N = 4 condiții atomice):
  T1: (A=1, B=1, C=0, D=0) -> Decision = True
  T2: (A=0, B=1, C=0, D=0) -> Decision = False   [Pereche independență A: (T1, T2)]
  T3: (A=1, B=0, C=0, D=0) -> Decision = False   [Pereche independență B: (T1, T3)]
  T4: (A=1, B=1, C=1, D=0) -> Decision = False   [Pereche independență C: (T1, T4)]
  T5: (A=1, B=1, C=1, D=1) -> Decision = True    [Pereche independență D: (T4, T5)]
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from parking_gate import EmployeeTier, AccessDecision, evaluate_parking_access


class TestMCDCCoverage:

    def test_mcdc_t1_base_true_off_peak(self):
        """
        T1: A=1, B=1, C=0 (ora 6, off-peak), D=0 (occupied=10, quota=10, not within quota)
        not C = True -> (A and B) and (True or False) = True
        Rezultat așteptat: GRANTED_EV_CHARGING.
        """
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=6,  # off-peak -> C=0
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,   # A=1
            has_ev_spots_available=True,  # B=1
            company_allows_overflow=False,
        )
        assert res == AccessDecision.GRANTED_EV_CHARGING

    def test_mcdc_t2_independence_a(self):
        """
        T2: A=0, B=1, C=0, D=0
        Doar A devine False față de T1.
        Decizia devine False -> Vehiculul nu este direcționat la EV (merge la respingere cotă).
        Pereche de independență pentru condiția A: (T1, T2).
        """
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=6,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,   # A=0 (MUTAT)
            has_ev_spots_available=True,  # B=1
            company_allows_overflow=False,
        )
        # Decizia EV a devenit False! Rezultatul este DENIED_QUOTA_EXCEEDED
        assert res != AccessDecision.GRANTED_EV_CHARGING
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_mcdc_t3_independence_b(self):
        """
        T3: A=1, B=0, C=0, D=0
        Doar B devine False față de T1 (nu mai sunt stații libere).
        Decizia devine False -> Pereche de independență pentru condiția B: (T1, T3).
        """
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=6,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,     # A=1
            has_ev_spots_available=False,  # B=0 (MUTAT)
            company_allows_overflow=False,
        )
        assert res != AccessDecision.GRANTED_EV_CHARGING
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_mcdc_t4_independence_c(self):
        """
        T4: A=1, B=1, C=1 (ora 10, peak), D=0 (occupied=10, quota=10, not within quota)
        Doar C devine True (ore de vârf) față de T1.
        not C devine False -> (A and B) and (False or False) = False.
        Decizia devine False -> Pereche de independență pentru condiția C: (T1, T4).
        """
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=10,  # peak -> C=1 (MUTAT)
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,    # A=1
            has_ev_spots_available=True,  # B=1
            company_allows_overflow=False,
        )
        assert res != AccessDecision.GRANTED_EV_CHARGING
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_mcdc_t5_independence_d(self):
        """
        T5: A=1, B=1, C=1, D=1 (occupied=7, quota=10, within quota)
        Doar D devine True față de T4.
        not C or D = False or True = True -> Decizia redevine True.
        Pereche de independență pentru condiția D: (T4, T5).
        """
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=7,  # D=1 (MUTAT)
            entry_hour=10,               # C=1
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,    # A=1
            has_ev_spots_available=True,  # B=1
            company_allows_overflow=False,
        )
        assert res == AccessDecision.GRANTED_EV_CHARGING
