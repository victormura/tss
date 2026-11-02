# Cerința 6: Mutanți Ne-Echivalenți (Omorât vs. Neomorât)

**Autor:** Natalia Moroz (50% contribuție)  
**Cod sursă mutanți:** [`mutants/manual_mutants.py`](../mutants/manual_mutants.py)  
**Test de demonstrare:** [`tests/test_manual_mutants.py`](../tests/test_manual_mutants.py)

---

## 6.1. Cazul de Testare Ales

Am selectat testul de frontieră de la Cerința 1 (BVA):  
`test_bva_occupied_exactly_at_quota` din [`tests/test_bva.py`](../tests/test_bva.py).

### Parametrii cazului de testare:
- `company_allocated_quota = 10`
- `company_current_occupied = 10` (ocupat exact la nivelul cotei contractuale)
- `entry_hour = 12` (ore de vârf)
- `tier = EmployeeTier.REGULAR` (angajat normal)
- `is_electric_vehicle = False`
- `has_ev_spots_available = False`
- `company_allows_overflow = False` (compania **nu** acceptă depășirea cotei)

### Rezultatul așteptat pe programul original:
Deoarece `occupied < quota` este $10 < 10 \implies \mathbf{False}$, mașina nu primește acces standard, iar firma nu are overflow.  
Programul original returnează: **`AccessDecision.DENIED_QUOTA_EXCEEDED`**.

---

## 6.2. Mutantul Ne-Echivalent #1: OMORÂT (Killed)

### Mutația aplicată:
Operatorul de mutație: **ROR (Relational Operator Replacement)**.  
Operatorul strict `<` de la verificarea cotei este înlocuit cu `<=`.

```diff
--- src/parking_gate.py (Original)
+++ mutants/manual_mutants.py (evaluate_parking_access_mutant_killed)
@@ -68,1 +68,1 @@
-    is_within_quota = company_current_occupied < company_allocated_quota
+    is_within_quota = company_current_occupied <= company_allocated_quota
```

### De ce este omorât de test:
1. În testul ales, `occupied = 10` și `quota = 10`.
2. În mutant, expresia `10 <= 10` devine $\mathbf{True}$ (în loc de $\mathbf{False}$).
3. La Regula 4 (`if is_within_quota:`), mutantul returnează:  
   $$\text{Ieșire Mutant} = \mathbf{GRANTED\_REGULAR}$$
4. Cazul de testare verifică aserțiunea:  
   `assert res == AccessDecision.DENIED_QUOTA_EXCEEDED`
5. Testul eșuează imediat cu `AssertionError: GRANTED_REGULAR != DENIED_QUOTA_EXCEEDED`.  
   $\implies$ **Mutantul este DETECTAT și OMORÂT (Killed).**

---

## 6.3. Mutantul Ne-Echivalent #2: NE-OMORÂT (Survived)

### Mutația aplicată:
Operatorul de mutație: **AOR / Constant Replacement** pe pragul maxim admis de overflow la ore de vârf.  
Constanta `5` este înlocuită cu `4`.

```diff
--- src/parking_gate.py (Original)
+++ mutants/manual_mutants.py (evaluate_parking_access_mutant_survived)
@@ -80,1 +80,1 @@
-    if company_allows_overflow and (not is_peak_hours or overflow_count < 5):
+    if company_allows_overflow and (not is_peak_hours or overflow_count < 4):
```

### De ce este ne-echivalent în general:
Dacă am rula un test cu `company_allows_overflow = True`, la ora 12, cu `occupied = 14, quota = 10` ($\text{diff} = 4$):
- Programul original evaluează $4 < 5 \implies \mathbf{True}$ $\to$ `GRANTED_PAID_OVERFLOW`.
- Mutantul evaluează $4 < 4 \implies \mathbf{False}$ $\to$ `DENIED_QUOTA_EXCEEDED`.  
Prin urmare, programele au comportamente diferite $\implies$ **Mutantul este ne-echivalent**.

### De ce SUPRAVIEȚUIEȘTE la cazul de testare ales:
În testul `test_bva_occupied_exactly_at_quota`:
- Parametrul `company_allows_overflow` are valoarea $\mathbf{False}$.
- În instrucțiunea:
  `if company_allows_overflow and (not is_peak_hours or overflow_count < 4):`
  expresia se **scurtcircuitează** (*short-circuit evaluation*) pe primul termen (`False and ...`).
- Subexpresia mutată `overflow_count < 4` **nu este niciodată evaluată**.
- Mutantul continuă execuția către linia finală și returnează:  
  $$\text{Ieșire Mutant} = \mathbf{DENIED\_QUOTA\_EXCEEDED}$$
- Aserțiunea testului trece cu succes (`True == True`), testul fiind complet orb la prezența mutației.  
  $\implies$ **Mutantul SUPRAVIEȚUIEȘTE (Survived).**
