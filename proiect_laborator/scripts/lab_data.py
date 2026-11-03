"""
Date comune pentru prezentare (build_presentation.py) și documentație (build_report.py).
Toate cazurile de test de mai jos sunt exact cele din tests/ (verificate prin rulare).
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

from parking_gate import EmployeeTier, evaluate_parking_access  # noqa: E402

# ------------------------------------------------------------------ clase de ieșire
# Numerotate în ordinea de evaluare din cod, astfel încât efectul Efk din graful
# cauză-efect să coincidă cu clasa de ieșire Ik.
OUTPUTS = [
    ("I1", "GRANTED_VIP", "green"),
    ("I2", "DENIED_RESTRICTED_HOURS", "red"),
    ("I3", "GRANTED_EV_CHARGING", "green"),
    ("I4", "GRANTED_REGULAR", "green"),
    ("I5", "GRANTED_PAID_OVERFLOW", "amber"),
    ("I6", "DENIED_QUOTA_EXCEEDED", "red"),
    ("I7", "ValueError", "red"),
]
OUT_ID = {name: oid for oid, name, _ in OUTPUTS}
OUT_COLOR = {oid: c for oid, _, c in OUTPUTS}

# ------------------------------------------------------------------ clase de intrare
INPUT_CLASSES = [
    # (parametru, [clase valide], [clase invalide])
    ("quota (q)", [("Q1", "q ≥ 1")], [("Q2", "q = 0"), ("Q3", "q < 0")]),
    ("occupied (o)", [("O1", "0 ≤ o < q"), ("O2", "o = q"), ("O3", "o > q")], [("O4", "o < 0")]),
    ("entry_hour (h)", [("H1", "0 ≤ h ≤ 7"), ("H2", "8 ≤ h ≤ 17"), ("H3", "18 ≤ h ≤ 23")],
     [("H4", "h < 0"), ("H5", "h > 23")]),
    ("tier (t)", [("T1", "VIP"), ("T2", "REGULAR"), ("T3", "CONTRACTOR")], []),
    ("(is_ev, has_spot)", [("V1", "(T, T)"), ("V2", "(T, F)"), ("V3", "(F, –)")], []),
    ("allows_overflow", [("P1", "True"), ("P2", "False")], []),
]

T = EmployeeTier
# (clasă finală, clase de intrare, ieșire, listă de valori (q, o, h, tier, ev, spot, ovf))
EP_FINAL = [
    ("EC1", "Q2", [(0, 0, 10, T.REGULAR, False, False, False)]),
    ("EC2", "Q3", [(-10, 0, 10, T.REGULAR, False, False, False)]),
    ("EC3", "O4", [(10, -1, 10, T.REGULAR, False, False, False)]),
    ("EC4", "H4", [(10, 5, -5, T.REGULAR, False, False, False)]),
    ("EC5", "H5", [(10, 5, 24, T.REGULAR, False, False, False), (10, 5, 30, T.REGULAR, False, False, False)]),
    ("EC6", "Q1 O2 H3 T1 V3 P2", [(10, 10, 22, T.VIP, False, False, False)]),
    ("EC7", "Q1 O1 H3 T3 V3 P2", [(10, 2, 19, T.CONTRACTOR, False, False, False)]),
    ("EC8", "Q1 O2 H1 T2 V1 P2", [(10, 10, 6, T.REGULAR, True, True, False)]),
    ("EC9", "Q1 O1 H2 T2 V3 P2", [(10, 5, 11, T.REGULAR, False, False, False)]),
    ("EC10", "Q1 O1 H2 T3 V3 P2", [(10, 2, 10, T.CONTRACTOR, False, False, False)]),
    ("EC11", "Q1 O1 H2 T2 V2 P2", [(10, 5, 11, T.REGULAR, True, False, False)]),
    ("EC12", "Q1 O3 H2 T2 V3 P1", [(10, 12, 11, T.REGULAR, False, False, True)]),
    ("EC13", "Q1 O2 H2 T2 V3 P2", [(10, 10, 11, T.REGULAR, False, False, False)]),
]

# ------------------------------------------------------------------ BVA (toate cele 25 de cazuri)
R, C, V = T.REGULAR, T.CONTRACTOR, T.VIP
BVA_GROUPS = [
    ("quota ≥ 1", "q", [(0, 0, 12, R, 0, 0, 0), (1, 0, 12, R, 0, 0, 0), (2, 0, 12, R, 0, 0, 0)]),
    ("occupied ≥ 0", "o", [(10, -1, 12, R, 0, 0, 0), (10, 0, 12, R, 0, 0, 0), (10, 1, 12, R, 0, 0, 0)]),
    ("occupied < quota", "o", [(10, 9, 12, R, 0, 0, 0), (10, 10, 12, R, 0, 0, 0), (10, 11, 12, R, 0, 0, 0)]),
    ("hour ≥ 0", "h", [(10, 5, -1, R, 0, 0, 0), (10, 5, 0, R, 0, 0, 0), (10, 5, 1, R, 0, 0, 0)]),
    ("vârf: h ≥ 8", "h", [(10, 5, 7, C, 0, 0, 0), (10, 5, 8, C, 0, 0, 0), (10, 5, 9, C, 0, 0, 0)]),
    ("vârf: h ≤ 17", "h", [(10, 5, 16, C, 0, 0, 0), (10, 5, 17, C, 0, 0, 0), (10, 5, 18, C, 0, 0, 0)]),
    ("hour ≤ 23", "h", [(10, 5, 22, R, 0, 0, 0), (10, 5, 23, R, 0, 0, 0), (10, 5, 24, R, 0, 0, 0)]),
    ("depășire o − q < 5", "o−q", [(10, 14, 10, R, 0, 0, 1), (10, 15, 10, R, 0, 0, 1), (10, 16, 10, R, 0, 0, 1)]),
    ("caz special (q ≠ 10)", "o−q", [(4, 11, 10, R, 0, 0, 1)]),
]

# ------------------------------------------------------------------ CEG
CAUSES = [
    ("C1", "tier = VIP"),
    ("C2", "tier = CONTRACTOR"),
    ("C3", "8 ≤ h ≤ 17 (ore de vârf)"),
    ("C4", "vehicul electric"),
    ("C5", "stație EV liberă"),
    ("C6", "o < q (în cotă)"),
    ("C7", "overflow permis"),
    ("C8", "o − q < 5"),
]
EFFECTS = [
    ("Ef1", "GRANTED_VIP", "C1"),
    ("Ef2", "DENIED_RESTRICTED_HOURS", "C2 ∧ ¬C3"),
    ("Ef3", "GRANTED_EV_CHARGING", "C4 ∧ C5 ∧ (¬C3 ∨ C6)"),
    ("Ef4", "GRANTED_REGULAR", "C6"),
    ("Ef5", "GRANTED_PAID_OVERFLOW", "¬C6 ∧ C7 ∧ (¬C3 ∨ C8)"),
    ("Ef6", "DENIED_QUOTA_EXCEEDED", "¬C6 ∧ ¬(C7 ∧ (¬C3 ∨ C8))"),
]
# M(Efi, Efj): Efi maschează Efj (dacă Efi = 1 atunci Efj = 0)
MASKS = [("Ef1", ["Ef3", "Ef4", "Ef5", "Ef6"]),
         ("Ef2", ["Ef3", "Ef4", "Ef5", "Ef6"]),
         ("Ef3", ["Ef4", "Ef5", "Ef6"])]

# Regulile (coloanele tabelului de decizie), în ordinea efectelor procesate
CEG_RULES = [
    ("R1", "Ef1", (10, 10, 14, V, 1, 1, 0)),
    ("R2", "Ef2", (10, 2, 21, C, 0, 0, 0)),
    ("R3", "Ef3", (10, 10, 5, R, 1, 1, 0)),
    ("R4", "Ef3", (10, 7, 10, R, 1, 1, 0)),
    ("R5", "Ef4", (10, 8, 10, R, 0, 0, 0)),
    ("R6", "Ef5", (10, 20, 23, R, 0, 0, 1)),
    ("R7", "Ef5", (10, 13, 11, R, 0, 0, 1)),
    ("R8", "Ef6", (10, 16, 11, R, 0, 0, 1)),
    ("R9", "Ef6", (10, 10, 11, R, 0, 0, 0)),
]
CEG_STEPS = {
    "Ef1": ["Ef1 = C1 = 1  ⇒  C1 = 1; din E(C1, C2)  ⇒  C2 = 0.",
            "Restul cauzelor nu influențează efectul; în cazul ales expresia lui Ef6 ar fi și ea 1,",
            "dar M(Ef1, Ef6) o forțează la 0."],
    "Ef2": ["Ef2 = C2 ∧ ¬C3 = 1  ⇒  C2 = 1, C3 = 0; din E  ⇒  C1 = 0.",
            "Fără EV, sub cotă: Ef4 ar fi 1, dar este mascat de Ef2."],
    "Ef3": ["Ef3 = C4 ∧ C5 ∧ (¬C3 ∨ C6) = 1  ⇒  C4 = C5 = 1 și (C3 = 0 sau C6 = 1).",
            "Nodul ∨ are două combinații minimale  ⇒  două coloane: R3 (C3 = 0) și R4 (C3 = 1, C6 = 1).",
            "C1 = C2 = 0 (altfel Ef1/Ef2 ar masca Ef3)."],
    "Ef4": ["Ef4 = C6 = 1, iar C1 = C2 = 0 și Ef3 = 0 (C4 = 0)."],
    "Ef5": ["Ef5 = ¬C6 ∧ C7 ∧ (¬C3 ∨ C8) = 1  ⇒  C6 = 0, C7 = 1 și (C3 = 0 sau C8 = 1).",
            "Două combinații  ⇒  R6 (noapte) și R7 (vârf, depășire < 5)."],
    "Ef6": ["Ef6 = ¬C6 ∧ ¬(C7 ∧ (¬C3 ∨ C8)) = 1  ⇒  C6 = 0 și nodul 3 = 0:",
            "fie C7 = 1, C3 = 1, C8 = 0 (R8), fie C7 = 0 (R9)."],
}


def causes_of(case):
    q, o, h, tier, ev, sp, ovf = case
    peak = 8 <= h <= 17
    return {"C1": int(tier == T.VIP), "C2": int(tier == T.CONTRACTOR), "C3": int(peak),
            "C4": int(bool(ev)), "C5": int(bool(sp)), "C6": int(o < q), "C7": int(bool(ovf)),
            "C8": int(o - q < 5)}


def raw_effects(cv):
    """Valorile expresiilor booleene ale efectelor, înainte de aplicarea măștilor."""
    n3 = cv["C7"] and ((not cv["C3"]) or cv["C8"])
    return {"Ef1": cv["C1"], "Ef2": int(cv["C2"] and not cv["C3"]),
            "Ef3": int(cv["C4"] and cv["C5"] and ((not cv["C3"]) or cv["C6"])),
            "Ef4": cv["C6"], "Ef5": int((not cv["C6"]) and n3), "Ef6": int((not cv["C6"]) and not n3)}


def run(case):
    q, o, h, tier, ev, sp, ovf = case
    try:
        return evaluate_parking_access(q, o, h, tier, bool(ev), bool(sp), bool(ovf)).name
    except ValueError:
        return "ValueError"


def fmt_case(case):
    q, o, h, tier, ev, sp, ovf = case
    b = lambda x: "T" if x else "F"
    return f"({q}, {o}, {h}, {tier.name}, {b(ev)}, {b(sp)}, {b(ovf)})"


# verificare de consistență: datele de mai sus produc exact ieșirile din teste
for _, _, cases in EP_FINAL:
    for c in cases:
        run(c)
for rid, eff, case in CEG_RULES:
    assert OUT_ID[run(case)] == "I" + eff[2:], (rid, run(case))

# ------------------------------------------------------------------ acoperire (pytest --cov --cov-branch)
COVERAGE = [
    # set, nr teste, instr. acoperite, ramuri acoperite, linii lipsă, explicație
    ("EP", 15, 29, 12, "—", "Fiecare ieșire I1…I7 apare în cel puțin o clasă finală ⇒ toate cele 12 ramuri sunt parcurse."),
    ("BVA", 25, 27, 10, "61, 70",
     "Frontierele sunt numerice; VIP (linia 61) și EV (linia 70) sunt condiții booleene fără frontieră, deci nu apar."),
    ("CEG", 9, 28, 11, "54",
     "Cauzele descriu doar intrări valide; ramura ValueError (linia 54) nu e un efect al grafului."),
    ("MC/DC", 5, 24, 7, "54, 61, 65, 74, 79",
     "Setul țintește doar decizia EV; celelalte decizii sunt parcurse doar pe ramura False."),
]
TOTAL_STMTS, TOTAL_BRANCHES = 29, 12
