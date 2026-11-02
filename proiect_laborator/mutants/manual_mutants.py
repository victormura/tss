"""
Cerința 6: Mutanți Ne-Echivalenți (Omorât vs. Neomorât)
Autor: Natalia Moroz (50% contribuție)

Cazul de testare ales de la Punctul 1 (BVA):
  test_bva_occupied_exactly_at_quota:
    quota = 10, occupied = 10, hour = 12, tier = REGULAR,
    is_electric = False, has_ev_spots = False, allows_overflow = False
    Rezultat așteptat: AccessDecision.DENIED_QUOTA_EXCEEDED
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from parking_gate import EmployeeTier, AccessDecision


def evaluate_parking_access_mutant_killed(
    company_allocated_quota: int,
    company_current_occupied: int,
    entry_hour: int,
    tier: EmployeeTier,
    is_electric_vehicle: bool,
    has_ev_spots_available: bool,
    company_allows_overflow: bool,
) -> AccessDecision:
    """
    MUTANT NE-ECHIVALENT #1 (OMORÂT de test):
    Operator de mutație: ROR (Relational Operator Replacement)
    Linia modificată:
      Original: is_within_quota = company_current_occupied < company_allocated_quota
      Mutat:    is_within_quota = company_current_occupied <= company_allocated_quota  # [< în <=]
    """
    if (
        company_allocated_quota <= 0
        or company_current_occupied < 0
        or entry_hour < 0
        or entry_hour > 23
    ):
        raise ValueError("Parametri de intrare în afara domeniilor valide admise.")

    is_peak_hours = (8 <= entry_hour <= 17)

    if tier == EmployeeTier.VIP:
        return AccessDecision.GRANTED_VIP

    if tier == EmployeeTier.CONTRACTOR and not is_peak_hours:
        return AccessDecision.DENIED_RESTRICTED_HOURS

    # <<< MUTAȚIE AICI: '<' înlocuit cu '<=' >>>
    is_within_quota = company_current_occupied <= company_allocated_quota

    if is_electric_vehicle and has_ev_spots_available and (not is_peak_hours or is_within_quota):
        return AccessDecision.GRANTED_EV_CHARGING

    if is_within_quota:
        return AccessDecision.GRANTED_REGULAR

    overflow_count = company_current_occupied - company_allocated_quota
    if company_allows_overflow and (not is_peak_hours or overflow_count < 5):
        return AccessDecision.GRANTED_PAID_OVERFLOW

    return AccessDecision.DENIED_QUOTA_EXCEEDED


def evaluate_parking_access_mutant_survived(
    company_allocated_quota: int,
    company_current_occupied: int,
    entry_hour: int,
    tier: EmployeeTier,
    is_electric_vehicle: bool,
    has_ev_spots_available: bool,
    company_allows_overflow: bool,
) -> AccessDecision:
    """
    MUTANT NE-ECHIVALENT #2 (NE-OMORÂT / SUPRAVIEȚUIT la testul ales):
    Operator de mutație: AOR (Arithmetic/Relational Operator Replacement pe prag overflow)
    Linia modificată:
      Original: overflow_count < 5
      Mutat:    overflow_count < 4  # [5 în 4]
    
    De ce supraviețuiește testului test_bva_occupied_exactly_at_quota:
    Deoarece în acel test company_allows_overflow = False, condiția se scurtcircuitează
    înainte de a evalua pragul de overflow. Astfel, comportamentul observabil pentru
    acel test rămâne identic (DENIED_QUOTA_EXCEEDED), iar mutantul scapă neomorât.
    """
    if (
        company_allocated_quota <= 0
        or company_current_occupied < 0
        or entry_hour < 0
        or entry_hour > 23
    ):
        raise ValueError("Parametri de intrare în afara domeniilor valide admise.")

    is_peak_hours = (8 <= entry_hour <= 17)

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
    # <<< MUTAȚIE AICI: '< 5' înlocuit cu '< 4' >>>
    if company_allows_overflow and (not is_peak_hours or overflow_count < 4):
        return AccessDecision.GRANTED_PAID_OVERFLOW

    return AccessDecision.DENIED_QUOTA_EXCEEDED
