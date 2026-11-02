# Cerința 1: Testare Funcțională (Black-Box)

**Autor:** Victor Mura (50% contribuție)  
**Fișiere de test:** [`tests/test_ep.py`](../tests/test_ep.py), [`tests/test_bva.py`](../tests/test_bva.py), [`tests/test_ceg.py`](../tests/test_ceg.py)

---

## 1.1. Partiționarea în Clase de Echivalență (Equivalence Partitioning — EP)

Conform suportului de curs (*Functional Testing*, slide-urile 5–25), tehnica partiționării în clase de echivalență împarte domeniul de intrare și ieșire în clase disjuncte de date considerate echivalente. Se presupune că dacă un test dintr-o clasă reușește sau eșuează, programul se va comporta identic pentru toți membrii acelei clase.

### 1. Intrările Programului
Funcția `evaluate_parking_access` are 7 parametri formali:
- $q$: `company_allocated_quota` ($\mathbb{Z}$)
- $o$: `company_current_occupied` ($\mathbb{Z}$)
- $h$: `entry_hour` ($\mathbb{Z}$)
- $t$: `tier` ($\in \{\text{VIP}, \text{REGULAR}, \text{CONTRACTOR}\}$)
- $ev$: `is_electric_vehicle` ($\in \{\text{True}, \text{False}\}$)
- $sp$: `has_ev_spots_available` ($\in \{\text{True}, \text{False}\}$)
- $ovf$: `company_allows_overflow` ($\in \{\text{True}, \text{False}\}$)

### 2. Clase de Intrare (Valide și Invalide)
- **Pentru $q$ (cota alocată):**
  - $Q_1 = \{q \in \mathbb{Z} \mid q \ge 1\}$ — *valid* (cotă contractuală admisă)
  - $Q_2 = \{q \in \mathbb{Z} \mid q = 0\}$ — *invalid* (cotă nulă)
  - $Q_3 = \{q \in \mathbb{Z} \mid q < 0\}$ — *invalid* (cotă negativă)
- **Pentru $o$ (locuri ocupate):**
  - $O_1 = \{o \in \mathbb{Z} \mid 0 \le o < q\}$ — *valid sub cotă* (locuri libere disponibile)
  - $O_2 = \{o \in \mathbb{Z} \mid o = q\}$ — *valid la cotă* (cotă atinsă)
  - $O_3 = \{o \in \mathbb{Z} \mid o > q\}$ — *valid peste cotă* (depășire necesară)
  - $O_4 = \{o \in \mathbb{Z} \mid o < 0\}$ — *invalid* (contor negativ)
- **Pentru $h$ (ora de intrare):**
  - $H_1 = \{h \in \mathbb{Z} \mid 0 \le h \le 7\}$ — *valid off-peak dimineață*
  - $H_2 = \{h \in \mathbb{Z} \mid 8 \le h \le 17\}$ — *valid ore de vârf*
  - $H_3 = \{h \in \mathbb{Z} \mid 18 \le h \le 23\}$ — *valid off-peak seară*
  - $H_4 = \{h \in \mathbb{Z} \mid h < 0\}$ — *invalid* (valoare orară negativă)
  - $H_5 = \{h \in \mathbb{Z} \mid h \ge 24\}$ — *invalid* (valoare orară peste 23)
- **Pentru $t$ (statut angajat):**
  - $T_1 = \{\text{VIP}\}$, $T_2 = \{\text{REGULAR}\}$, $T_3 = \{\text{CONTRACTOR}\}$
- **Pentru vehicule electrice $(ev, sp)$:**
  - $EV_1 = \{(\text{True}, \text{True})\}$ — vehicul electric și stație disponibilă
  - $EV_2 = \{(\text{True}, \text{False})\}$ — vehicul electric, dar fără stații libere
  - $EV_3 = \{(\text{False}, *)\}$ — vehicul convențional
- **Pentru overflow $ovf$:**
  - $OVF_1 = \{\text{True}\}$, $OVF_2 = \{\text{False}\}$

### 3. Clase de Ieșire
- $I_1 = \text{AccessDecision.GRANTED\_REGULAR}$
- $I_2 = \text{AccessDecision.GRANTED\_VIP}$
- $I_3 = \text{AccessDecision.GRANTED\_EV\_CHARGING}$
- $I_4 = \text{AccessDecision.GRANTED\_PAID\_OVERFLOW}$
- $I_5 = \text{AccessDecision.DENIED\_QUOTA\_EXCEEDED}$
- $I_6 = \text{AccessDecision.DENIED\_RESTRICTED\_HOURS}$
- $I_7 = \text{ValueError("Parametri de intrare în afara domeniilor valide admise.")}$

### 4. Clase de Echivalență Finale și Cazuri de Test
Conform modelului consacrat din curs, combinăm clasele de intrare și ieșire într-un set reprezentativ de teste:

| Clasă Finală | Clasă Intrare Activă | Ieșire Așteptată | Date de Test Concrete $(q, o, h, t, ev, sp, ovf)$ | ID Test în `test_ep.py` |
| :---: | :--- | :---: | :--- | :--- |
| **C1** | $Q_2$ ($q = 0$) | $I_7$ | $(0, 0, 10, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_invalid_quota[0]` |
| **C2** | $Q_3$ ($q = -10$) | $I_7$ | $(-10, 0, 10, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_invalid_quota[-10]` |
| **C3** | $O_4$ ($o = -1$) | $I_7$ | $(10, -1, 10, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_invalid_occupied` |
| **C4** | $H_4$ ($h = -5$) | $I_7$ | $(10, 5, -5, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_invalid_entry_hour[-5]` |
| **C5** | $H_5$ ($h = 24$) | $I_7$ | $(10, 5, 24, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_invalid_entry_hour[24]` |
| **C6** | $H_5$ ($h = 30$) | $I_7$ | $(10, 5, 30, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_invalid_entry_hour[30]` |
| **C7** | $Q_1, O_1, H_2, T_1$ (VIP) | $I_2$ | $(10, 5, 12, \text{VIP}, \text{F}, \text{F}, \text{F})$ | `test_ep_vip_access_granted` |
| **C8** | $Q_1, O_1, H_3, T_3$ (Contractor noaptea) | $I_6$ | $(10, 5, 20, \text{CONTRACTOR}, \text{F}, \text{F}, \text{F})$ | `test_ep_contractor_outside_hours_denied` |
| **C9** | $Q_1, O_1, H_2, T_3$ (Contractor ziua) | $I_1$ | $(10, 5, 12, \text{CONTRACTOR}, \text{F}, \text{F}, \text{F})$ | `test_ep_contractor_working_hours_granted` |
| **C10** | $Q_1, O_3, H_1, T_2, EV_1$ (EV off-peak) | $I_3$ | $(10, 12, 6, \text{REGULAR}, \text{T}, \text{T}, \text{F})$ | `test_ep_ev_charging_granted_off_peak` |
| **C11** | $Q_1, O_1, H_2, T_2, EV_3$ (Standard) | $I_1$ | $(10, 5, 12, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_regular_within_quota` |
| **C12** | $Q_1, O_3, H_2, T_2, OVF_1$ (Overflow plătit) | $I_4$ | $(10, 12, 12, \text{REGULAR}, \text{F}, \text{F}, \text{T})$ | `test_ep_overflow_paid_granted` |
| **C13** | $Q_1, O_2, H_2, T_2, OVF_2$ (Cotă plină) | $I_5$ | $(10, 10, 12, \text{REGULAR}, \text{F}, \text{F}, \text{F})$ | `test_ep_quota_exceeded_denied` |
| **C14** | Verificare integritate tipuri Enum | — | Asigurare valori nenule pe `EmployeeTier` și `AccessDecision` | `test_ep_enum_integrity` |

---

## 1.2. Analiza Valorilor de Frontieră (Boundary Value Analysis — BVA)

Conform cursului (*Functional Testing*, slide-urile 26–35), defectele software se aglomerează la granițele claselor de echivalență. Pentru fiecare domeniu numeric $D = [\text{Min}, \text{Max}]$, testăm:
$$\{\text{Min}-1, \text{Min}, \text{Min}+1, \text{Max}-1, \text{Max}, \text{Max}+1\}$$

### 1. Frontiere Identificate
- **Pentru $q$ (minim valid = 1):** Frontiere: $0$ (invalid), $1$ (minim valid), $2$ (interior).
- **Pentru $o$ (minim valid = 0):** Frontiere: $-1$ (invalid), $0$ (minim valid), $1$ (interior).
- **Pentru relația $o < q$ ($q = 10$):** Frontiere: $9$ ($q-1$, sub cotă), $10$ ($q$, cota atinsă), $11$ ($q+1$, peste cotă).
- **Pentru $h$ (ziua orară $[0, 23]$):**
  - Limite extreme: $-1, 0, 1$ și $22, 23, 24$.
  - Prag început ore de vârf ($h=8$): $7$ (off-peak), $8$ (prima oră de vârf), $9$ (vârf).
  - Prag sfârșit ore de vârf ($h=17$): $16$ (vârf), $17$ (ultima oră de vârf), $18$ (off-peak seară).
- **Pentru pragul de overflow la ore de vârf ($o - q < 5$):**
  - Diferențe de depășire: $4$ ($5-1$, admis), $5$ (prag strict, refuzat), $6$ ($5+1$, refuzat).
- **Caz special / discriminant numeric de frontieră:**
  - $q = 4, o = 11$: diferență $11 - 4 = 7 \ge 5$ (refuzat), prevenind pseudo-echivalența cu operatorul modulo ($11 \pmod 4 = 3$).

### 2. Matricea de Testare BVA (25 de teste implementate în `tests/test_bva.py`)

| Frontieră Testată | Puncte Testate | Date de Intrare $(q, o, h, \dots)$ | Rezultat Așteptat | Ce defect previne? |
| :--- | :---: | :--- | :--- | :--- |
| $q \ge 1$ | $0, 1, 2$ | $(0, 0, 12) \dots (2, 0, 12)$ | $0 \to \text{ValueError}$; $1, 2 \to \text{GRANTED\_REGULAR}$ | Erori de verificare cotă nulă/negativă |
| $o \ge 0$ | $-1, 0, 1$ | $(10, -1, 12) \dots (10, 1, 12)$ | $-1 \to \text{ValueError}$; $0, 1 \to \text{GRANTED\_REGULAR}$ | Contor de locuri decrementat sub zero |
| $o$ vs $q = 10$ | $9, 10, 11$ | $(10, 9, 12), (10, 10, 12), (10, 11, 12)$ | $9 \to \text{REGULAR}$; $10, 11 \to \text{DENIED}$ | Înlocuirea eronată a operatorului $<$ cu $\le$ |
| $h \in [0, 23]$ (extremități) | $-1, 0, 1, 22, 23, 24$ | $h \in \{-1, 0, 1, 22, 23, 24\}$ | $-1, 24 \to \text{ValueError}$; restul valide | Indexare orară invalidă |
| $h$ prag start vârf | $7, 8, 9$ | Contractor la $h \in \{7, 8, 9\}$ | $7 \to \text{DENIED\_HOURS}$; $8, 9 \to \text{REGULAR}$ | Pornirea eronată a programului la ora 9 |
| $h$ prag final vârf | $16, 17, 18$ | Contractor la $h \in \{16, 17, 18\}$ | $16, 17 \to \text{REGULAR}$; $18 \to \text{DENIED\_HOURS}$ | Prelungirea eronată a programului după ora 18 |
| $o - q < 5$ la vârf | $4, 5, 6$ | Overflow activ, $o \in \{14, 15, 16\}$ la $q=10$ | $14 \to \text{OVERFLOW}$; $15, 16 \to \text{DENIED}$ | Depășirea pragului limită de 5 mașini |
| Cotă non-zecimală | $q=4, o=11$ | $q=4, o=11, h=10, ovf=\text{True}$ | $\text{DENIED\_QUOTA\_EXCEEDED}$ | Discriminant mutație `occupied % quota` |

---

## 1.3. Graful Cauză-Efect (Cause-Effect Graphing — CEG)

Conform suportului de curs (*Functional Testing*, slide-urile 270–380) și metodologiei Glenford Myers, graful cauză-efect este o reprezentare formală a logicii booleene dintre condițiile de intrare (**Cauze**) și răspunsurile sistemului (**Efecte**).

### 1. Notații Formale de Curs Utilizate
- $\longrightarrow$ **Implies:** dacă $C$ este 1, atunci efectul $Ef$ este 1.
- $\xrightarrow{\quad\sim\quad}$ **Not-Implies:** dacă $\neg C$ este 1 (deci $C=0$), atunci efectul $Ef$ este 1.
- $\xrightarrow{\quad\land\quad}$ **And-Implies:** dacă $C_1 \land C_2$ este 1, atunci efectul $Ef$ este 1.
- $\xrightarrow{\quad\lor\quad}$ **Or-Implies:** dacă $C_1 \lor C_2$ este 1, atunci efectul $Ef$ este 1.
- **Constrângere între cauze $E(C_1, C_2)$ (Exclusive):** cel mult una dintre cauzele $C_1, C_2$ poate lua valoarea 1 ($C_1 \land C_2 = 0$).
- **Constrângere între efecte $M(E_1, E_2, \dots)$ (Masks):** activarea unui efect prioritar maschează evaluarea efectelor inferioare ($E_1 > E_2 > E_3 > E_4 > E_5 > E_6$).

### 2. Catalogul Cauzelor ($C$)
- **$C_1$:** `tier == EmployeeTier.VIP` (angajat protocol)
- **$C_2$:** `tier == EmployeeTier.CONTRACTOR` (subcontractor)
- **$C_3$:** `8 <= entry_hour <= 17` (sosire la ore de vârf)
- **$C_4$:** `is_electric_vehicle == True` (vehicul electric)
- **$C_5$:** `has_ev_spots_available == True` (stație liberă)
- **$C_6$:** `company_current_occupied < company_allocated_quota` (în cota gratuită)
- **$C_7$:** `company_allows_overflow == True` (drept de overflow contractual)
- **$C_8$:** `(company_current_occupied - company_allocated_quota) < 5` (depășire $< 5$)

### 3. Constrângeri pe Cauze
- **$E(C_1, C_2)$:** Un angajat aparține unei singure categorii (nu poate fi simultan `VIP` și `CONTRACTOR`).

### 4. Catalogul Efectelor ($E$)
- **$E_1$:** `AccessDecision.GRANTED_VIP`
- **$E_2$:** `AccessDecision.DENIED_RESTRICTED_HOURS`
- **$E_3$:** `AccessDecision.GRANTED_EV_CHARGING`
- **$E_4$:** `AccessDecision.GRANTED_REGULAR`
- **$E_5$:** `AccessDecision.GRANTED_PAID_OVERFLOW`
- **$E_6$:** `AccessDecision.DENIED_QUOTA_EXCEEDED`

### 5. Graful Cauză-Efect (Reprezentare Grafică Mermaid)

```mermaid
flowchart LR
    subgraph CAUZE["Cauze (Condiții de Intrare)"]
        C1["C1: tier == VIP"]
        C2["C2: tier == CONTRACTOR"]
        C3["C3: ore de vârf (08-17)"]
        C4["C4: vehicul electric"]
        C5["C5: stație EV liberă"]
        C6["C6: ocupate < cotă"]
        C7["C7: overflow permis"]
        C8["C8: depășire < 5"]
    end

    %% Constrângere Exclusive între C1 și C2
    C1 -.-|E: Exclusiv| C2

    subgraph OPERATORI["Relații Logice"]
        NOT_C3(("~ NOT"))
        AND_C2_NOTC3(("^ AND"))
        AND_EV(("^ AND"))
        OR_EV(("v OR"))
        AND_EV_FINAL(("^ AND"))
        OR_OVF(("v OR"))
        AND_OVF_FINAL(("^ AND"))
    end

    subgraph EFECTE["Efecte (Ieșiri Decizionale)"]
        E1["E1: GRANTED_VIP"]
        E2["E2: DENIED_RESTRICTED_HOURS"]
        E3["E3: GRANTED_EV_CHARGING"]
        E4["E4: GRANTED_REGULAR"]
        E5["E5: GRANTED_PAID_OVERFLOW"]
        E6["E6: DENIED_QUOTA_EXCEEDED"]
    end

    %% Relații
    C1 --> E1

    C3 --> NOT_C3
    C2 --> AND_C2_NOTC3
    NOT_C3 --> AND_C2_NOTC3
    AND_C2_NOTC3 --> E2

    C4 --> AND_EV
    C5 --> AND_EV
    NOT_C3 --> OR_EV
    C6 --> OR_EV
    AND_EV --> AND_EV_FINAL
    OR_EV --> AND_EV_FINAL
    AND_EV_FINAL --> E3

    C6 --> E4

    NOT_C3 --> OR_OVF
    C8 --> OR_OVF
    C7 --> AND_OVF_FINAL
    OR_OVF --> AND_OVF_FINAL
    AND_OVF_FINAL --> E5

    %% Altfel
    OPERATORI -.->|altfel (implicit)| E6
```

---

### 6. Procedura de Creare a Tabelului de Decizie (Conform Cursului)

Conform algoritmului prezentat în suportul de curs (slide-urile 370–380):
1. **Se inițializează tabelul de decizie gol.**
2. **Pentru fiecare efect $E_i \in \{E_1, \dots, E_6\}$, se găsesc combinațiile de cauze care produc apariția efectului ($E_i = 1$):**
   - **Pentru $E_1$:** $C_1 = 1 \implies C_2 = 0$ (prin $E(C_1, C_2)$). Toate celelalte cauze sunt indiferente ($-$). $\implies$ **Regula 1 (R1)**.
   - **Pentru $E_2$:** $C_2 \land \neg C_3 = 1 \implies C_2 = 1, C_3 = 0, C_1 = 0$. $\implies$ **Regula 2 (R2)**.
   - **Pentru $E_3$:** $C_4 \land C_5 \land (\neg C_3 \lor C_6) = 1$, cu $C_1=0, C_2=0$:
     - *Soluția 1 (off-peak):* $C_3 = 0, C_4 = 1, C_5 = 1, C_6 = -$ $\implies$ **Regula 3 (R3)**.
     - *Soluția 2 (ore de vârf):* $C_3 = 1, C_4 = 1, C_5 = 1, C_6 = 1$ $\implies$ **Regula 4 (R4)**.
   - **Pentru $E_4$:** $C_6 = 1$, cu $C_1=0, C_2=0, C_4=0$ (pentru a nu declanșa EV) $\implies$ **Regula 5 (R5)**.
   - **Pentru $E_5$:** $C_7 \land (\neg C_3 \lor C_8) = 1$, cu $C_6=0$:
     - *Soluția 1 (off-peak):* $C_3 = 0, C_6 = 0, C_7 = 1, C_8 = -$ $\implies$ **Regula 6 (R6)**.
     - *Soluția 2 (ore de vârf sub 5):* $C_3 = 1, C_6 = 0, C_7 = 1, C_8 = 1$ $\implies$ **Regula 7 (R7)**.
   - **Pentru $E_6$:** Cota este epuizată și nu există drept de acces:
     - *Soluția 1 (ore de vârf cu depășire $\ge 5$):* $C_3 = 1, C_6 = 0, C_7 = 1, C_8 = 0$ $\implies$ **Regula 8 (R8)**.
     - *Soluția 2 (fără clauză de overflow):* $C_6 = 0, C_7 = 0$ $\implies$ **Regula 9 (R9)**.

---

### 7. Tabelul de Decizie Final (Format Standard de Curs)

Tabelul conține $N = p + q = 8 + 6 = 14$ linii pentru cauze și efecte, plus rândurile de date concrete de intrare (*Input*) și rezultat (*Output*), dispuse pe 9 coloane (*Reguli de Testare*):

| Secțiune | Variabilă / Condiție | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cauze** | **$C_1$** (tier = VIP) | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | **$C_2$** (tier = CONTRACTOR) | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | **$C_3$** (ore de vârf: 08–17) | – | **0** | **0** | **1** | – | **0** | **1** | **1** | – |
| | **$C_4$** (vehicul electric) | – | – | **1** | **1** | **0** | **0** | **0** | **0** | **0** |
| | **$C_5$** (stație EV liberă) | – | – | **1** | **1** | – | – | – | – | – |
| | **$C_6$** (ocupate $<$ cotă) | – | – | – | **1** | **1** | **0** | **0** | **0** | **0** |
| | **$C_7$** (overflow permis) | – | – | – | – | – | **1** | **1** | **1** | **0** |
| | **$C_8$** (depășire $< 5$) | – | – | – | – | – | – | **1** | **0** | – |
| **Efecte** | **$E_1$** (`GRANTED_VIP`) | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | **$E_2$** (`DENIED_RESTRICTED_HOURS`) | 0 | **1** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | **$E_3$** (`GRANTED_EV_CHARGING`) | 0 | 0 | **1** | **1** | 0 | 0 | 0 | 0 | 0 |
| | **$E_4$** (`GRANTED_REGULAR`) | 0 | 0 | 0 | 0 | **1** | 0 | 0 | 0 | 0 |
| | **$E_5$** (`GRANTED_PAID_OVERFLOW`) | 0 | 0 | 0 | 0 | 0 | **1** | **1** | 0 | 0 |
| | **$E_6$** (`DENIED_QUOTA_EXCEEDED`) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **1** | **1** |
| **Input** | `(quota, occupied, hour)` | (10, 5, 12) | (10, 5, 20) | (10, 12, 6) | (10, 5, 12) | (10, 5, 12) | (10, 12, 20) | (10, 12, 12) | (10, 16, 12) | (10, 12, 12) |
| | `tier` | VIP | CONTRACTOR | REGULAR | REGULAR | REGULAR | REGULAR | REGULAR | REGULAR | REGULAR |
| | `(is_ev, has_spots, overflow)` | (F, F, F) | (F, F, F) | (T, T, F) | (T, T, F) | (F, F, F) | (F, F, T) | (F, F, T) | (F, F, T) | (F, F, F) |
| **Output** | **Decizie Returnată** | **E1** | **E2** | **E3** | **E3** | **E4** | **E5** | **E5** | **E6** | **E6** |
| **Test** | **Metodă în `test_ceg.py`** | `rule1` | `rule2` | `rule3` | `rule4` | `rule5` | `rule6` | `rule7` | `rule8` | `rule9` |

Toate cele 9 cazuri de test sunt implementate în fișierul [`tests/test_ceg.py`](../tests/test_ceg.py) și trec cu succes.
