"""
Cerința 5: Mutant de Ordinul 1 Echivalent
Autor: Natalia Moroz (50% contribuție)

Un mutant de ordinul 1 obținut prin modificarea unei singure instrucțiuni (operator relațional).
Mutantul este SEMANTIC ECHIVALENT cu programul original pentru întregul spațiu de intrare.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from parking_gate import EmployeeTier, AccessDecision


def evaluate_parking_access_equivalent_mutant(
    company_allocated_quota: int,
    company_current_occupied: int,
    entry_hour: int,
    tier: EmployeeTier,
    is_electric_vehicle: bool,
    has_ev_spots_available: bool,
    company_allows_overflow: bool,
) -> AccessDecision:
    """
    MUTANT DE ORDINUL 1 ECHIVALENT:
    Instrucțiunea originală:
        is_peak_hours = (8 <= entry_hour <= 17)
    Instrucțiunea mutată:
        is_peak_hours = (7 < entry_hour < 18)

    Demonstrație de Echivalență Semantică:
    Parametrul entry_hour este de tip întreg (int: h in Z).
    Pentru oricare h întreg:
        (h >= 8) <===> (h > 7)
        (h <= 17) <===> (h < 18)
    Prin urmare, conjuncția:
        (8 <= h <= 17) <===> (7 < h < 18)
    este o tautologie pe domeniul numerelor întregi.
    Niciun set de teste (EP, BVA, CEG, MC/DC sau generat aleator) nu poate ucide
    acest mutant, deoarece comportamentul său extern este strict identic cu originalul.
    """
    if (
        company_allocated_quota <= 0
        or company_current_occupied < 0
        or entry_hour < 0
        or entry_hour > 23
    ):
        raise ValueError("Parametri de intrare în afara domeniilor valide admise.")

    # <<< MUTAȚIE ECHIVALENTĂ DE ORDINUL 1 >>>
    is_peak_hours = (7 < entry_hour < 18)

    if tier == EmployeeTier.VIP:
        return AccessDecision.GRANTED_VIP

    if tier == EmployeeTier.CONTRACTOR and not is_peak_hours:
        return AccessDecision.DENIED_RESTRICTED_HOURS

    is_within_quota = company_current_occupied < company_allocated_quota
    if is_electric_vehicle and has_ev_spots_available and (not is_peak_hours or is_within_quota):
        return AccessDecision.GRANTED_EV_CHARGING

    if is_within_quota:
        return AccessDecision.GRANTED_REGULAR

    overflow_count = company_current_occupied - company_allocated_quota
    if company_allows_overflow and (not is_peak_hours or overflow_count < 5):
        return AccessDecision.GRANTED_PAID_OVERFLOW

    return AccessDecision.DENIED_QUOTA_EXCEEDED
