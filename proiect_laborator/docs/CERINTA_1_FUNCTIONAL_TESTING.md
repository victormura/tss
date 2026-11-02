# Cerința 1: Testare Funcțională (Black-Box)

**Autor:** Victor Mura (50% contribuție)  
**Fișiere de test:** [`tests/test_ep.py`](../tests/test_ep.py), [`tests/test_bva.py`](../tests/test_bva.py), [`tests/test_ceg.py`](../tests/test_ceg.py)

---

## 1.1. Equivalence Partitioning (EP) — Partiționare de Echivalență

Metoda *Equivalence Partitioning* împarte domeniul fiecărui parametru de intrare în clase de echivalență din care se alege cel puțin un reprezentant. Dacă un test dintr-o clasă reușește/eșuează, se presupune că toate datele din acea clasă vor avea același comportament.

### Identificarea Claselor de Echivalență

| Parametru | Clasă Validă (Accepted) | Clase Invalide (Rejected / Error) |
| :--- | :--- | :--- |
| `company_allocated_quota` ($q$) | **EP-Q-VAL:** $q \in [1, \infty)$ (ex: 10) | **EP-Q-INV1:** $q = 0$<br>**EP-Q-INV2:** $q < 0$ (ex: -10) |
| `company_current_occupied` ($o$) | **EP-O-SUB:** $0 \le o < q$ (sub cotă, ex: 5)<br>**EP-O-EQ:** $o = q$ (la cotă, ex: 10)<br>**EP-O-OVER:** $o > q$ (peste cotă, ex: 12) | **EP-O-INV:** $o < 0$ (ex: -1) |
| `entry_hour` ($h$) | **EP-H-OFF1:** $h \in [0, 7]$ (noapte/dimineață off-peak)<br>**EP-H-PEAK:** $h \in [8, 17]$ (ore de vârf)<br>**EP-H-OFF2:** $h \in [18, 23]$ (seară off-peak) | **EP-H-INV1:** $h < 0$ (ex: -5)<br>**EP-H-INV2:** $h \ge 24$ (ex: 24, 30) |
| `tier` | **EP-T-VIP:** `EmployeeTier.VIP`<br>**EP-T-REG:** `EmployeeTier.REGULAR`<br>**EP-T-CON:** `EmployeeTier.CONTRACTOR` | *N/A (asigurat prin tip static `Enum`)* |
| `is_electric_vehicle`, `has_ev_spots_available` | **EP-EV-OK:** `(True, True)`<br>**EP-EV-NOSPOT:** `(True, False)`<br>**EP-EV-NO:** `(False, * )` | *N/A (valori booleene)* |
| `company_allows_overflow` | **EP-OVF-YES:** `True`<br>**EP-OVF-NO:** `False` | *N/A (valori booleene)* |

---

## 1.2. Boundary Value Analysis (BVA) — Analiza Valorilor de Frontieră

Erorile software apar cel mai frecvent la frontierele intervalelor. Pentru fiecare frontieră s-au selectat valorile:
- $\text{Min} - 1$ (exterior invalid), $\text{Min}$ (frontieră inferioară), $\text{Min} + 1$ (interior)
- $\text{Max} - 1$ (interior), $\text{Max}$ (frontieră superioară), $\text{Max} + 1$ (exterior invalid)

### Matricea Valorilor de Frontieră

| Parametru / Relație | Frontiere Testate | Valori Concrete | Rezultat Așteptat |
| :--- | :---: | :---: | :--- |
| `company_allocated_quota` | $\text{Min}-1, \text{Min}, \text{Min}+1$ | `0`, `1`, `2` | `0` $\to$ `ValueError`; `1, 2` $\to$ Valid |
| `company_current_occupied` | $\text{Min}-1, \text{Min}, \text{Min}+1$ | `-1`, `0`, `1` | `-1` $\to$ `ValueError`; `0, 1` $\to$ Valid |
| `occupied` vs `quota` ($q = 10$) | $q-1, q, q+1$ | `9`, `10`, `11` | `9` $\to$ `GRANTED_REGULAR`; `10, 11` $\to$ `DENIED` |
| `entry_hour` (Limite extreme) | $0-1, 0, 1$ și $22, 23, 24$ | `-1`, `0`, `1`, `22`, `23`, `24` | `-1, 24` $\to$ `ValueError`; `0, 23` $\to$ Valid |
| `entry_hour` (Prag Peak Start) | $8-1, 8, 8+1$ | `7`, `8`, `9` | `7` $\to$ Off-peak; `8, 9` $\to$ Peak |
| `entry_hour` (Prag Peak End) | $17-1, 17, 17+1$ | `16`, `17`, `18` | `16, 17` $\to$ Peak; `18` $\to$ Off-peak |
| `overflow_count` ($o - q$ la Peak) | $5-1, 5, 5+1$ | `4`, `5`, `6` | `4` $\to$ `GRANTED_PAID_OVERFLOW`; `5, 6` $\to$ `DENIED` |

---

## 1.3. Cause-Effect Graphing (CEG) — Graful Cauză-Efect

### 1. Catalogul Cauzelor (Intrări Logice)
- **$C_1$:** `tier == EmployeeTier.VIP`
- **$C_2$:** `tier == EmployeeTier.CONTRACTOR`
- **$C_3$:** `8 <= entry_hour <= 17` ($\text{is\_peak\_hours}$)
- **$C_4$:** `is_electric_vehicle == True`
- **$C_5$:** `has_ev_spots_available == True`
- **$C_6$:** `company_current_occupied < company_allocated_quota` ($\text{is\_within\_quota}$)
- **$C_7$:** `company_allows_overflow == True`
- **$C_8$:** `(company_current_occupied - company_allocated_quota) < 5` ($\text{overflow} < 5$)

### 2. Constrângeri pe Cauze
- **Exclusivitate $E(C_1, C_2)$:** Un angajat nu poate fi simultan `VIP` și `CONTRACTOR`.

### 3. Noduri Intermediare (Porți Logice)
- $I_1 = \text{NOT}(C_3)$ — sosire în afara orelor de vârf
- $I_2 = C_2 \land I_1$ — contractor în afara programului
- $I_3 = C_4 \land C_5$ — vehicul EV cu încărcător disponibil
- $I_4 = I_1 \lor C_6$ — condiție relaxată pentru EV (noaptea sau sub cotă)
- $I_5 = I_3 \land I_4$ — acces aprobat la stația EV
- $I_6 = I_1 \lor C_8$ — condiție relaxată pentru overflow
- $I_7 = C_7 \land I_6$ — drept de overflow aprobat

### 4. Catalogul Efectelor (Ieșiri)
- **$E_1$:** `GRANTED_VIP`
- **$E_2$:** `DENIED_RESTRICTED_HOURS`
- **$E_3$:** `GRANTED_EV_CHARGING`
- **$E_4$:** `GRANTED_REGULAR`
- **$E_5$:** `GRANTED_PAID_OVERFLOW`
- **$E_6$:** `DENIED_QUOTA_EXCEEDED`

### 5. Tabelul de Decizie Derivat din Graf

| Regula | $C_1$ | $C_2$ | $C_3$ | $C_4$ | $C_5$ | $C_6$ | $C_7$ | $C_8$ | Efect Activat | Test Asociat în `test_ceg.py` |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **R1** | 1 | 0 | * | * | * | * | * | * | **$E_1$ (`GRANTED_VIP`)** | `test_ceg_rule1_vip_access` |
| **R2** | 0 | 1 | 0 | * | * | * | * | * | **$E_2$ (`DENIED_RESTRICTED_HOURS`)** | `test_ceg_rule2_contractor_outside_peak` |
| **R3** | 0 | 0 | 0 | 1 | 1 | * | * | * | **$E_3$ (`GRANTED_EV_CHARGING`)** | `test_ceg_rule3_ev_off_peak` |
| **R4** | 0 | 0 | 1 | 1 | 1 | 1 | * | * | **$E_3$ (`GRANTED_EV_CHARGING`)** | `test_ceg_rule4_ev_peak_within_quota` |
| **R5** | 0 | 0 | * | 0 | * | 1 | * | * | **$E_4$ (`GRANTED_REGULAR`)** | `test_ceg_rule5_regular_within_quota` |
| **R6** | 0 | 0 | 0 | 0 | * | 0 | 1 | * | **$E_5$ (`GRANTED_PAID_OVERFLOW`)** | `test_ceg_rule6_overflow_off_peak` |
| **R7** | 0 | 0 | 1 | 0 | * | 0 | 1 | 1 | **$E_5$ (`GRANTED_PAID_OVERFLOW`)** | `test_ceg_rule7_overflow_peak_under_5` |
| **R8** | 0 | 0 | 1 | 0 | * | 0 | 1 | 0 | **$E_6$ (`DENIED_QUOTA_EXCEEDED`)** | `test_ceg_rule8_denied_overflow_peak_exceeded_limit` |
| **R9** | 0 | 0 | * | 0 | * | 0 | 0 | * | **$E_6$ (`DENIED_QUOTA_EXCEEDED`)** | `test_ceg_rule9_denied_no_overflow_policy` |
