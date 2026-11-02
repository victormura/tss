"""
Sistem de Control Acces Parcare Corporate Multi-Tenant (Smart Parking Gate).
Modulul principal implementează logica decizională pentru accesul vehiculelor
aparținând companiilor chiriașe într-un campus de afaceri.
"""

from enum import Enum, auto


class EmployeeTier(Enum):
    REGULAR = auto()      # Angajat standard
    VIP = auto()          # Management / Protocol
    CONTRACTOR = auto()   # Subcontractor extern / Temporar


class AccessDecision(Enum):
    GRANTED_REGULAR = auto()         # Acces gratuit în limita cotei companiei
    GRANTED_VIP = auto()             # Acces garantat necondiționat pe loc VIP
    GRANTED_EV_CHARGING = auto()     # Acces redirecționat la stația de încărcare EV
    GRANTED_PAID_OVERFLOW = auto()   # Acces suplimentar aprobat cu tarifare overflow
    DENIED_QUOTA_EXCEEDED = auto()   # Acces refuzat - cota companiei este epuizată
    DENIED_RESTRICTED_HOURS = auto() # Acces refuzat - în afara programului permis


def evaluate_parking_access(
    company_allocated_quota: int,
    company_current_occupied: int,
    entry_hour: int,
    tier: EmployeeTier,
    is_electric_vehicle: bool,
    has_ev_spots_available: bool,
    company_allows_overflow: bool,
) -> AccessDecision:
    """
    Evaluează cererea de acces a unui vehicul la bariera campusului corporate.

    :param company_allocated_quota: Numărul de locuri contractate de companie (> 0).
    :param company_current_occupied: Numărul curent de locuri ocupate de companie (>= 0).
    :param entry_hour: Ora curentă de intrare pe ceas (interval valid [0, 23]).
    :param tier: Statutul / rolul angajatului (EmployeeTier).
    :param is_electric_vehicle: True dacă vehiculul este complet electric / plug-in hybrid.
    :param has_ev_spots_available: True dacă există cel puțin un punct de încărcare EV liber.
    :param company_allows_overflow: True dacă firma permite depășirea cotei contra cost.
    :return: AccessDecision decizia automată a barierei.
    :raises ValueError: Dacă parametrii numerici sunt în afara domeniilor valide admise.
    """
    # 0. Validare defensivă a parametrilor de intrare (Boundary Value / Equivalence)
    if (
        company_allocated_quota <= 0
        or company_current_occupied < 0
        or entry_hour < 0
        or entry_hour > 23
    ):
        raise ValueError("Parametri de intrare în afara domeniilor valide admise.")

    # Ore de vârf / program normal de lucru al campusului: 08:00 - 17:59
    is_peak_hours = (8 <= entry_hour <= 17)

    # 1. Prioritate VIP: Acces garantat necondiționat pe locuri rezervate de protocol
    if tier == EmployeeTier.VIP:
        return AccessDecision.GRANTED_VIP

    # 2. Securitate Subcontractori: Acces interzis în afara orelor de program (noaptea)
    if tier == EmployeeTier.CONTRACTOR and not is_peak_hours:
        return AccessDecision.DENIED_RESTRICTED_HOURS

    # 3. Stații de încărcare vehicule electrice (EV) - Condiție compusă (Nucleu MC/DC)
    is_within_quota = company_current_occupied < company_allocated_quota
    if is_electric_vehicle and has_ev_spots_available and (not is_peak_hours or is_within_quota):
        return AccessDecision.GRANTED_EV_CHARGING

    # 4. Acces standard în cota gratuită a companiei
    if is_within_quota:
        return AccessDecision.GRANTED_REGULAR

    # 5. Politica de depășire cotă (Overflow plătit pe companie)
    overflow_count = company_current_occupied - company_allocated_quota
    if company_allows_overflow and (not is_peak_hours or overflow_count < 5):
        return AccessDecision.GRANTED_PAID_OVERFLOW

    # 6. Cota epuizată și overflow nepermis / indisponibil
    return AccessDecision.DENIED_QUOTA_EXCEEDED
