# Cerința 4: Modified Condition / Decision Coverage (MC/DC)

**Autor:** Natalia Moroz (50% contribuție)  
**Fișier de test:** [`tests/test_mcdc.py`](../tests/test_mcdc.py)

---

## 4.1. Fundament Teoretic MC/DC

Criteriul **MC/DC** (stabilit prin standardul aeronautic internațional *DO-178C Level A*) cere ca:
1. Fiecare punct de intrare și ieșire al metodei să fie atins.
2. Fiecare decizie din program să ia toate rezultatele posibile (Adevărat și Fals).
3. Fiecare condiție atomică dintr-o decizie să ia toate rezultatele posibile (Adevărat și Fals).
4. **Fiecare condiție atomică să demonstreze că poate afecta în mod independent rezultatul deciziei** (prin intermediul unei *perechi de independență* în care doar respectiva condiție își schimbă valoarea, celelalte condiții rămânând neschimbate sau nemascate).

Pentru o decizie compusă cu $N$ condiții atomice, numărul minim de teste necesare este **$N + 1$**.

---

## 4.2. Decizia Compusă Analizată

Am selectat decizia compusă critică de la Regula 3 (accesul la stațiile de încărcare electrică):

$$\text{Decision}_{EV} = (A \land B) \land (\neg C \lor D)$$

unde condițiile atomice sunt:
- **$A$:** `is_electric_vehicle`
- **$B$:** `has_ev_spots_available`
- **$C$:** `is_peak_hours` (deci $\neg C$ reprezintă sosirea în afara orelor de vârf)
- **$D$:** `is_within_quota` (`company_current_occupied < company_allocated_quota`)

Număr de condiții atomice: $N = 4 \implies$ Număr minim de teste MC/DC: **$4 + 1 = 5$ teste**.

---

## 4.3. Tabelul de Adevăr Complet ($2^4 = 16$ combinații)

| Combinație | $A$ | $B$ | $C$ | $D$ | $A \land B$ | $\neg C \lor D$ | $\text{Decision}_{EV}$ | Selectat în setul MC/DC |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0 | 0 | 0 | 0 | 0 | 1 | **0** | |
| 2 | 0 | 0 | 0 | 1 | 0 | 1 | **0** | |
| 3 | 0 | 0 | 1 | 0 | 0 | 0 | **0** | |
| 4 | 0 | 0 | 1 | 1 | 0 | 1 | **0** | |
| 5 | 0 | 1 | 0 | 0 | 0 | 1 | **0** | **T2 (Independență A)** |
| 6 | 0 | 1 | 0 | 1 | 0 | 1 | **0** | |
| 7 | 0 | 1 | 1 | 0 | 0 | 0 | **0** | |
| 8 | 0 | 1 | 1 | 1 | 0 | 1 | **0** | |
| 9 | 1 | 0 | 0 | 0 | 0 | 1 | **0** | **T3 (Independență B)** |
| 10 | 1 | 0 | 0 | 1 | 0 | 1 | **0** | |
| 11 | 1 | 0 | 1 | 0 | 0 | 0 | **0** | |
| 12 | 1 | 0 | 1 | 1 | 0 | 1 | **0** | |
| 13 | 1 | 1 | 0 | 0 | 1 | 1 | **1** | **T1 (Bază Adevărată)** |
| 14 | 1 | 1 | 0 | 1 | 1 | 1 | **1** | |
| 15 | 1 | 1 | 1 | 0 | 1 | 0 | **0** | **T4 (Independență C)** |
| 16 | 1 | 1 | 1 | 1 | 1 | 1 | **1** | **T5 (Independență D)** |

---

## 4.4. Perechile de Independență și Setul de Teste Minimal

Pentru a satisface criteriul MC/DC, am extras un subset optim de **5 teste**:

| Condiție Testată | Pereche de Independență | Test 1 $(D=\text{True})$ | Test 2 $(D=\text{False})$ | Justificarea Independenței |
| :---: | :---: | :---: | :---: | :--- |
| **$A$ (`is_electric_vehicle`)** | **$(T_1, T_5)$ vs $T_2$** $\to$ **$(T_1, T_2)$** | $T_1: (1, 1, 0, 0) \to \mathbf{1}$ | $T_2: (0, 1, 0, 0) \to \mathbf{0}$ | $B=1, C=0, D=0$ sunt fixe. Doar $A$ comută $1 \to 0$, forțând decizia $1 \to 0$. |
| **$B$ (`has_ev_spots_available`)** | **$(T_1, T_3)$** | $T_1: (1, 1, 0, 0) \to \mathbf{1}$ | $T_3: (1, 0, 0, 0) \to \mathbf{0}$ | $A=1, C=0, D=0$ sunt fixe. Doar $B$ comută $1 \to 0$, forțând decizia $1 \to 0$. |
| **$C$ (`is_peak_hours`)** | **$(T_1, T_4)$** | $T_1: (1, 1, 0, 0) \to \mathbf{1}$ | $T_4: (1, 1, 1, 0) \to \mathbf{0}$ | $A=1, B=1, D=0$ sunt fixe. Doar $C$ comută $0 \to 1$, forțând decizia $1 \to 0$. |
| **$D$ (`is_within_quota`)** | **$(T_5, T_4)$** | $T_5: (1, 1, 1, 1) \to \mathbf{1}$ | $T_4: (1, 1, 1, 0) \to \mathbf{0}$ | $A=1, B=1, C=1$ sunt fixe. Doar $D$ comută $1 \to 0$, forțând decizia $1 \to 0$. |

Toate cele 5 teste sunt implementate și validate în clasa `TestMCDCCoverage` din [`tests/test_mcdc.py`](../tests/test_mcdc.py).
