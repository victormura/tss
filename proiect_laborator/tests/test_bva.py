"""
Cerința 1.b: Boundary Value Analysis (BVA) - Testare la Frontieră
Autor: Natalia Moroz (50% contribuție)

Această suită testează valorile de frontieră identificate pentru limitele numerice
și deciziile relaționale din metoda evaluate_parking_access:
  - Valori min - 1, min, min + 1
  - Valori max - 1, max, max + 1
  - Frontiere decizionale interne (q - 1, q, q + 1; diferență overflow 4, 5, 6)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from parking_gate import EmployeeTier, AccessDecision, evaluate_parking_access


class TestBoundaryValueAnalysis:

    # --- 1. Frontiere pentru company_allocated_quota (Min valid = 1) ---

    def test_bva_quota_below_min_invalid(self):
        """Frontieră q = 0 (min - 1) -> Invalid (aruncă ValueError)."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(0, 0, 12, EmployeeTier.REGULAR, False, False, False)

    def test_bva_quota_at_min_valid(self):
        """Frontieră q = 1 (min valid) cu o = 0 -> Valid (GRANTED_REGULAR)."""
        res = evaluate_parking_access(1, 0, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_quota_above_min_valid(self):
        """Frontieră q = 2 (min + 1) cu o = 0 -> Valid (GRANTED_REGULAR)."""
        res = evaluate_parking_access(2, 0, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    # --- 2. Frontiere pentru company_current_occupied (Min valid = 0) ---

    def test_bva_occupied_below_min_invalid(self):
        """Frontieră o = -1 (min - 1) -> Invalid (aruncă ValueError)."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(10, -1, 12, EmployeeTier.REGULAR, False, False, False)

    def test_bva_occupied_at_min_valid(self):
        """Frontieră o = 0 (min valid) -> Valid."""
        res = evaluate_parking_access(10, 0, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_occupied_above_min_valid(self):
        """Frontieră o = 1 (min + 1) -> Valid."""
        res = evaluate_parking_access(10, 1, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    # --- 3. Frontiere pentru relația de ocupare: occupied vs quota (q = 10) ---

    def test_bva_occupied_just_below_quota(self):
        """Frontieră o = 9 (q - 1) -> Încă sub cotă -> GRANTED_REGULAR."""
        res = evaluate_parking_access(10, 9, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_occupied_exactly_at_quota(self):
        """Frontieră o = 10 (q) -> Cotă atinsă -> DENIED_QUOTA_EXCEEDED."""
        res = evaluate_parking_access(10, 10, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_bva_occupied_just_above_quota(self):
        """Frontieră o = 11 (q + 1) -> Depășire cotă fără overflow -> DENIED_QUOTA_EXCEEDED."""
        res = evaluate_parking_access(10, 11, 12, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    # --- 4. Frontiere pentru entry_hour [0, 23] și Peak Hours [8, 17] ---

    def test_bva_hour_below_absolute_min_invalid(self):
        """Frontieră h = -1 (0 - 1) -> Invalid."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(10, 5, -1, EmployeeTier.REGULAR, False, False, False)

    def test_bva_hour_at_absolute_min(self):
        """Frontieră h = 0 (min valid) -> Off-peak noaptea."""
        res = evaluate_parking_access(10, 5, 0, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_above_min(self):
        """Frontieră h = 1 (min + 1) -> Off-peak."""
        res = evaluate_parking_access(10, 5, 1, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_just_before_peak(self):
        """Frontieră h = 7 (8 - 1) -> Ultima oră off-peak de dimineață (Contractor respins)."""
        res = evaluate_parking_access(10, 5, 7, EmployeeTier.CONTRACTOR, False, False, False)
        assert res == AccessDecision.DENIED_RESTRICTED_HOURS

    def test_bva_hour_at_peak_start(self):
        """Frontieră h = 8 -> Prima oră de vârf (Contractor permis)."""
        res = evaluate_parking_access(10, 5, 8, EmployeeTier.CONTRACTOR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_just_after_peak_start(self):
        """Frontieră h = 9 (8 + 1) -> În plin interval de vârf."""
        res = evaluate_parking_access(10, 5, 9, EmployeeTier.CONTRACTOR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_just_before_peak_end(self):
        """Frontieră h = 16 (17 - 1) -> Încă oră de vârf."""
        res = evaluate_parking_access(10, 5, 16, EmployeeTier.CONTRACTOR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_at_peak_end(self):
        """Frontieră h = 17 -> Ultima oră de vârf inclusă."""
        res = evaluate_parking_access(10, 5, 17, EmployeeTier.CONTRACTOR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_just_after_peak_end(self):
        """Frontieră h = 18 (17 + 1) -> Prima oră off-peak de seară (Contractor respins)."""
        res = evaluate_parking_access(10, 5, 18, EmployeeTier.CONTRACTOR, False, False, False)
        assert res == AccessDecision.DENIED_RESTRICTED_HOURS

    def test_bva_hour_just_before_absolute_max(self):
        """Frontieră h = 22 (23 - 1) -> Valid."""
        res = evaluate_parking_access(10, 5, 22, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_at_absolute_max(self):
        """Frontieră h = 23 (max valid) -> Valid."""
        res = evaluate_parking_access(10, 5, 23, EmployeeTier.REGULAR, False, False, False)
        assert res == AccessDecision.GRANTED_REGULAR

    def test_bva_hour_above_absolute_max_invalid(self):
        """Frontieră h = 24 (23 + 1) -> Invalid (aruncă ValueError)."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(10, 5, 24, EmployeeTier.REGULAR, False, False, False)

    # --- 5. Frontiere pentru pragul de overflow la ore de vârf: (occupied - quota < 5) ---

    def test_bva_overflow_just_below_threshold(self):
        """Frontieră diff = 4 (5 - 1) la ore de vârf -> Permis GRANTED_PAID_OVERFLOW."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=14,  # diff = 4
            entry_hour=10,                # peak hour
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.GRANTED_PAID_OVERFLOW

    def test_bva_overflow_exactly_at_threshold(self):
        """Frontieră diff = 5 la ore de vârf -> Respins (limita este strict < 5)."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=15,  # diff = 5
            entry_hour=10,                # peak hour
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_bva_overflow_above_threshold(self):
        """Frontieră diff = 6 (5 + 1) la ore de vârf -> Respins."""
        res = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=16,  # diff = 6
            entry_hour=10,                # peak hour
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED

    def test_bva_overflow_non_decimal_quota_discriminant(self):
        """
        Test discriminant împotriva operatorului de mutație Sub_Mod (% în loc de -).
        Pentru quota=4 și occupied=11:
          - Corect: 11 - 4 = 7 >= 5 -> DENIED_QUOTA_EXCEEDED
          - Mutant Sub_Mod (%): 11 % 4 = 3 < 5 -> GRANTED_PAID_OVERFLOW (detectat și ucis)
        """
        res = evaluate_parking_access(
            company_allocated_quota=4,
            company_current_occupied=11,
            entry_hour=10,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert res == AccessDecision.DENIED_QUOTA_EXCEEDED
