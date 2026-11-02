# Cerința 5: Mutant de Ordinul 1 Echivalent

**Autor:** Natalia Moroz (50% contribuție)  
**Cod sursă mutant:** [`mutants/equivalent_mutant.py`](../mutants/equivalent_mutant.py)  
**Test de validare a echivalenței:** [`tests/test_equivalent_mutant.py`](../tests/test_equivalent_mutant.py)

---

## 5.1. Noțiunea de Mutant Echivalent

În testarea prin mutații (*Mutation Testing*), un mutant este considerat **de ordinul 1** dacă este generat prin aplicarea unui singur operator de mutație la o singură locație sintactică din codul sursă.

Un mutant $M$ este **echivalent** cu programul original $P$ dacă produce exact aceeași ieșire pentru **orice** intrare posibilă din spațiul de intrare:
$$\forall x \in \text{Domain}, \quad M(x) = P(x)$$

> **Consecință directă:** Un mutant echivalent este **imposibil de omorât** de orice suită de teste (oricât de completă ar fi aceasta). Prezența mutanților echivalenți scade artificial scorul de mutație brut (*raw mutation score*).

---

## 5.2. Mutația Implementată

În metoda `evaluate_parking_access`, s-a aplicat operatorul **ROR (Relational Operator Replacement)** combinat cu înlocuirea constantelor de frontieră:

```diff
--- src/parking_gate.py (Programul Original)
+++ mutants/equivalent_mutant.py (Mutantul de Ordin 1)
@@ -57,1 +57,1 @@
-    is_peak_hours = (8 <= entry_hour <= 17)
+    is_peak_hours = (7 < entry_hour < 18)
```

---

## 5.3. Demonstrația Matematică de Echivalență

1. **Tipul de date al intrării:**  
   Parametrul `entry_hour` este declarat și constrâns ca număr întreg:
   $$h \in \mathbb{Z}$$

2. **Proprietatea de discretizare a mulțimii numerelor întregi:**  
   Pe mulțimea $\mathbb{Z}$, pentru orice $h$:
   $$h \ge 8 \iff h > 7$$
   $$h \le 17 \iff h < 18$$

3. **Echivalența conjuncției logice:**  
   Prin urmare, expresia originală:
   $$\text{Expr}_{\text{orig}}(h) = (h \ge 8) \land (h \le 17)$$
   este strict logic echivalentă cu expresia mutată:
   $$\text{Expr}_{\text{mut}}(h) = (h > 7) \land (h < 18)$$

4. **Identitatea stărilor interne și a valorilor returnate:**  
   Variabila booleană `is_peak_hours` primește exact aceeași valoare de adevăr în mutant ca și în programul original pentru toate valorile posibile $h \in \{0, 1, \dots, 23\}$. Întrucât nicio altă linie din program nu a fost modificată, $M(x) = P(x)$ pentru orice tuplu de intrare $x$.

---

## 5.4. Verificarea Empirică Exhaustivă

Proprietatea de echivalență a fost validată experimental în suita [`tests/test_equivalent_mutant.py`](../tests/test_equivalent_mutant.py) prin rularea unui produs cartezian pe:
- Toate cele 24 de ore ale zilei ($h \in [0, 23]$)
- Toate categoriile de angajați (`REGULAR`, `VIP`, `CONTRACTOR`)
- Toate combinațiile posibile de mașini electrice (`is_ev`), stații libere (`has_spots`), flexibilitate overflow (`allows_overflow`) și nivele de ocupare (sub cotă vs. peste cotă).

În toate cazurile testate (sute de execuții), rezultatele programului original și ale mutantului au fost **100% identice**, confirmând matematic și practic echivalența mutantului.
