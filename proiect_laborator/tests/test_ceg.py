"""
Cerința 1.c: Cause-Effect Graphing (CEG) - Testare pe Bază de Graf Cauză-Efect
Autor: Natalia Moroz (50% contribuție)

Această suită implementează cazurile de testare derivate direct din Tabelul de Decizie
obținut prin analiza Grafului Cauză-Efect:
  - Cauze: C1 (VIP), C2 (Contractor), C3 (PeakHours), C4 (EV), C5 (SpotEV),
           C6 (WithinQuota), C7 (AllowsOverflow), C8 (OverflowDiff < 5)
  - Efecte: E1 (VIP), E2 (DeniedHours), E3 (EVCharging), E4 (Regular),
            E5 (PaidOverflow), E6 (DeniedQuota)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from parking_gate import EmployeeTier, AccessDecision, evaluate_parking_access


class TestCauseEffectGraphing:

    def test_ceg_rule1_vip_access(self):
        """Regula 1: C1=1 -> E1=1 (GRANTED_VIP). Restul cauzelor sunt 'don't care'."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=14,
            tier=EmployeeTier.VIP,
            is_electric_vehicle=True,
            has_ev_spots_available=True,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.GRANTED_VIP

    def test_ceg_rule2_contractor_outside_peak(self):
        """Regula 2: C1=0, C2=1, C3=0 -> E2=1 (DENIED_RESTRICTED_HOURS)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=2,
            entry_hour=21,  # C3=0 (off-peak)
            tier=EmployeeTier.CONTRACTOR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.DENIED_RESTRICTED_HOURS

    def test_ceg_rule3_ev_off_peak(self):
        """Regula 3: C1=0, C2=0, C3=0 (off-peak), C4=1, C5=1 -> E3=1 (GRANTED_EV_CHARGING)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,  # chiar dacă cota e plină
            entry_hour=5,                 # off-peak (C3=0)
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,
            has_ev_spots_available=True,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.GRANTED_EV_CHARGING

    def test_ceg_rule4_ev_peak_within_quota(self):
        """Regula 4: C1=0, C2=0, C3=1 (peak), C4=1, C5=1, C6=1 (within quota) -> E3=1."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=7,   # C6=1
            entry_hour=10,                # C3=1
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,
            has_ev_spots_available=True,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.GRANTED_EV_CHARGING

    def test_ceg_rule5_regular_within_quota(self):
        """Regula 5: C1=0, C2=0, C4=0, C6=1 -> E4=1 (GRANTED_REGULAR)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=8,  # sub cotă
            entry_hour=10,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.GRANTED_REGULAR

    def test_ceg_rule6_overflow_off_peak(self):
        """Regula 6: C1=0, C2=0, C4=0, C6=0, C7=1 (overflow), C3=0 (off-peak) -> E5=1 (PAID_OVERFLOW)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=20,  # depășire mare, dar e noapte
            entry_hour=23,                # off-peak
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.GRANTED_PAID_OVERFLOW

    def test_ceg_rule7_overflow_peak_under_5(self):
        """Regula 7: C1=0, C2=0, C4=0, C6=0, C7=1, C3=1 (peak), C8=1 (diff < 5) -> E5=1 (PAID_OVERFLOW)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=13,  # diff = 3 (< 5)
            entry_hour=11,                # peak
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.GRANTED_PAID_OVERFLOW

    def test_ceg_rule8_denied_overflow_peak_exceeded_limit(self):
        """Regula 8: C1=0, C2=0, C4=0, C6=0, C7=1, C3=1 (peak), C8=0 (diff >= 5) -> E6=1 (DENIED_QUOTA)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=16,  # diff = 6 (>= 5)
            entry_hour=11,                # peak
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_ceg_rule9_denied_no_overflow_policy(self):
        """Regula 9: C1=0, C2=0, C4=0, C6=0, C7=0 -> E6=1 (DENIED_QUOTA_EXCEEDED)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,  # la cotă
            entry_hour=11,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED
