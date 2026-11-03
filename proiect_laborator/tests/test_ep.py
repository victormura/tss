"""
Cerința 1.a: Equivalence Partitioning (EP) - Testare Funcțională
Autor: Natalia Moroz (50% contribuție)

Această suită testează clasele de echivalență (valide și invalide) identificate
pentru parametrii metodei evaluate_parking_access.
"""

import pytest
import sys
import os

# Adăugăm src la PYTHONPATH pentru import corect
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from parking_gate import EmployeeTier, AccessDecision, evaluate_parking_access


class TestEquivalencePartitioning:
    """
    Clase de echivalență identificate:

    1. company_allocated_quota (q):
       - Clasa Invalidă EP-Q-INV: q <= 0 (ex: 0, -10)
       - Clasa Validă EP-Q-VAL: q > 0 (ex: 10)

    2. company_current_occupied (o):
       - Clasa Invalidă EP-O-INV: o < 0 (ex: -1)
       - Clasa Validă Sub Cotă EP-O-SUB: 0 <= o < q (ex: 5)
       - Clasa Validă La Cotă EP-O-EQUAL: o == q (ex: 10)
       - Clasa Validă Peste Cotă EP-O-OVER: o > q (ex: 12)

    3. entry_hour (h):
       - Clasa Invalidă Sub Limită EP-H-INV1: h < 0 (ex: -1)
       - Clasa Validă Off-Peak Dimineață EP-H-OFF1: 0 <= h <= 7 (ex: 6)
       - Clasa Validă Peak Hours EP-H-PEAK: 8 <= h <= 17 (ex: 10)
       - Clasa Validă Off-Peak Seară EP-H-OFF2: 18 <= h <= 23 (ex: 20)
       - Clasa Invalidă Peste Limită EP-H-INV2: h >= 24 (ex: 24)

    4. tier:
       - EP-T-VIP: EmployeeTier.VIP
       - EP-T-REG: EmployeeTier.REGULAR
       - EP-T-CON: EmployeeTier.CONTRACTOR

    5. is_electric_vehicle, has_ev_spots_available:
       - EP-EV-REQ: (True, True) -> Cerere EV satisfacută
       - EP-EV-NO-SPOT: (True, False) -> EV dar fără stație liberă
       - EP-EV-CONV: (False, ...) -> Vehicul convențional

    6. company_allows_overflow:
       - EP-OVF-TRUE: True
       - EP-OVF-FALSE: False
    """

    # --- Teste pentru clasele invalide (aruncă ValueError) ---

    @pytest.mark.parametrize("invalid_quota", [0, -10], ids=["EP-Q-INV-0", "EP-Q-INV-neg"])
    def test_ep_invalid_quota(self, invalid_quota):
        """EP-Q-INV: Cota <= 0 trebuie să arunce ValueError."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(
                company_allocated_quota=invalid_quota,
                company_current_occupied=0,
                entry_hour=10,
                tier=EmployeeTier.REGULAR,
                is_electric_vehicle=False,
                has_ev_spots_available=False,
                company_allows_overflow=False,
            )

    def test_ep_invalid_occupied(self):
        """EP-O-INV: Locuri ocupate negative trebuie să arunce ValueError."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(
                company_allocated_quota=10,
                company_current_occupied=-1,
                entry_hour=10,
                tier=EmployeeTier.REGULAR,
                is_electric_vehicle=False,
                has_ev_spots_available=False,
                company_allows_overflow=False,
            )

    @pytest.mark.parametrize("invalid_hour", [-5, 24, 30], ids=["EP-H-INV-neg", "EP-H-INV-24", "EP-H-INV-30"])
    def test_ep_invalid_entry_hour(self, invalid_hour):
        """EP-H-INV1 & EP-H-INV2: Ora < 0 sau > 23 trebuie să arunce ValueError."""
        with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):
            evaluate_parking_access(
                company_allocated_quota=10,
                company_current_occupied=5,
                entry_hour=invalid_hour,
                tier=EmployeeTier.REGULAR,
                is_electric_vehicle=False,
                has_ev_spots_available=False,
                company_allows_overflow=False,
            )

    def test_ep_enum_integrity(self):
        """Verifică integritatea claselor de echivalență Enum (apartenență și valori non-None)."""
        for member in EmployeeTier:
            assert member.value is not None
        for member in AccessDecision:
            assert member.value is not None

    # --- Teste pentru clasele valide (rezultate funcționale) ---

    def test_ep_vip_granted(self):
        """EP-T-VIP: Utilizator VIP are acces garantat oricând."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,  # chiar dacă e plin
            entry_hour=22,                # chiar dacă e noapte
            tier=EmployeeTier.VIP,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.GRANTED_VIP

    def test_ep_contractor_outside_hours_denied(self):
        """EP-T-CON + EP-H-OFF2: Contractor în afara orelor de vârf este refuzat."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=2,
            entry_hour=19,  # ora 19:00 (afara orelor 8-17)
            tier=EmployeeTier.CONTRACTOR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.DENIED_RESTRICTED_HOURS

    def test_ep_contractor_working_hours_granted(self):
        """EP-T-CON + EP-H-PEAK: Contractor în timpul programului are acces normal în cotă."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=2,
            entry_hour=10,  # ore de vârf
            tier=EmployeeTier.CONTRACTOR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.GRANTED_REGULAR

    def test_ep_ev_charging_granted_off_peak(self):
        """EP-EV-REQ + EP-H-OFF1: EV cu stație liberă în afara orelor de vârf are acces chiar peste cotă."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,  # cotă plină
            entry_hour=6,                 # off-peak
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,
            has_ev_spots_available=True,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.GRANTED_EV_CHARGING

    def test_ep_regular_within_quota(self):
        """EP-O-SUB + EP-T-REG: Angajat normal sub cotă primește GRANTED_REGULAR."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=5,
            entry_hour=11,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.GRANTED_REGULAR

    def test_ep_ev_without_free_spot(self):
        """EP-EV-NO-SPOT: Vehicul electric fără stație liberă -> tratat ca acces standard în cotă."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=5,
            entry_hour=11,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=True,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.GRANTED_REGULAR

    def test_ep_overflow_paid_granted(self):
        """EP-O-OVER + EP-OVF-TRUE: Peste cotă, dar overflow permis la ore de vârf cu diferență mică."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=12,  # diferență = 2 (< 5)
            entry_hour=11,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=True,
        )
        assert decision == AccessDecision.GRANTED_PAID_OVERFLOW

    def test_ep_quota_exceeded_denied(self):
        """EP-O-EQUAL + EP-OVF-FALSE: Cotă atinsă și fără drept de overflow -> DENIED."""
        decision = evaluate_parking_access(
            company_allocated_quota=10,
            company_current_occupied=10,
            entry_hour=11,
            tier=EmployeeTier.REGULAR,
            is_electric_vehicle=False,
            has_ev_spots_available=False,
            company_allows_overflow=False,
        )
        assert decision == AccessDecision.DENIED_QUOTA_EXCEEDED
