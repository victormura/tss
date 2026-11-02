# Specificația Cerințelor Software: Smart Corporate Parking Gate

**Disciplina:** Testarea Sistemelor Software (TSS) — Proiect de laborator  
**Echipa:** Victor Mura & Natalia Moroz  
**Modulul analizat:** `evaluate_parking_access` (din `proiect_laborator/src/parking_gate.py`)

---

## 1. Descrierea Generală și Contextul Sistemului

Sistemul automatizează controlul accesului la bariera principală a unui parc de afaceri (*business campus*) de tip *multi-tenant*. În incinta campusului își desfășoară activitatea mai multe companii partenere/chiriașe, fiecare având un număr contractual prestabilit de locuri de parcare gratuite (**cotă**).

Campusul este echipat suplimentar cu:
- O zonă dedicată stațiilor de încărcare pentru vehicule electrice (**EV**).
- Locuri de rezervă pentru management și protocol (**VIP**).
- O zonă de **overflow** (acces permis peste cotă, contra cost, pe baza unei clauze de flexibilitate contractuale).

Fiecare cerere de acces este evaluată instantaneu și determinist de metoda `evaluate_parking_access`.

---

## 2. Parametrii de Intrare (Date de Testare)

| Parametru | Tip de Date | Domeniu Valid | Semnificație |
| :--- | :---: | :---: | :--- |
| `company_allocated_quota` | `int` | $q \in [1, \infty)$ | Cota contractuală de locuri rezervate gratuit companiei. |
| `company_current_occupied`| `int` | $o \in [0, \infty)$ | Numărul curent de mașini ale companiei aflate în parcare. |
| `entry_hour` | `int` | $h \in [0, 23]$ | Ora sosirii la barieră (pe ceas, format 24h). |
| `tier` | `EmployeeTier` | `REGULAR`, `VIP`, `CONTRACTOR` | Categoria de acces / rolul angajatului. |
| `is_electric_vehicle` | `bool` | `True` / `False` | Dacă vehiculul necesită încărcare electrică. |
| `has_ev_spots_available` | `bool` | `True` / `False` | Dacă există puncte de încărcare EV libere în campus. |
| `company_allows_overflow` | `bool` | `True` / `False` | Clauză contractuală: compania acceptă facturarea extra pentru locuri overflow. |

---

## 3. Deciziile Sistemului (Ieșiri Posibile)

Sistemul returnează o valoare din enumerarea `AccessDecision`:

1. `GRANTED_VIP` — Acces permis prioritar pe locurile de protocol rezervate conducerii.
2. `DENIED_RESTRICTED_HOURS` — Acces refuzat pentru colaboratori externi în afara orelor de program.
3. `GRANTED_EV_CHARGING` — Acces aprobat și ghidat către zona stațiilor de încărcare electrică.
4. `GRANTED_REGULAR` — Acces aprobat pe un loc standard gratuit din cota companiei.
5. `GRANTED_PAID_OVERFLOW` — Acces aprobat peste cotă în regim de suprataxare flexibilă.
6. `DENIED_QUOTA_EXCEEDED` — Acces respins; cota firmei este plină și nu se acceptă depășirea.

---

## 4. Reguli Funcționale și Ierarhia Deciziilor

Evaluarea se efectuează secvențial conform următoarei ierarhii de priorități:

### Regula 0 (R0 - Validare defensivă):
Dacă oricare dintre condițiile următoare este adevărată, funcția aruncă o excepție `ValueError`:
- `company_allocated_quota <= 0`
- `company_current_occupied < 0`
- `entry_hour < 0` sau `entry_hour > 23`

### Regula 1 (R1 - Protocol VIP):
Dacă `tier == EmployeeTier.VIP`, accesul este aprobat imediat cu decizia `GRANTED_VIP`, indiferent de gradul de ocupare al cotei firmei sau de oră.

### Regula 2 (R2 - Restricții Securitate Subcontractori):
Dacă `tier == EmployeeTier.CONTRACTOR`, accesul este permis exclusiv în orele normale de lucru (intervalul orar $[8, 17]$, inclusiv). Dacă $h < 8$ sau $h > 17$, se returnează `DENIED_RESTRICTED_HOURS`.

### Regula 3 (R3 - Stații Încărcare EV - Nucleu MC/DC):
Dacă vehiculul este electric (`is_electric_vehicle == True`) **ȘI** există stații EV libere (`has_ev_spots_available == True`), accesul la încărcare `GRANTED_EV_CHARGING` este acordat dacă:
- *Fie* nu suntem la ore de vârf ($h < 8$ sau $h > 17$),
- *Fie* firma mai are locuri în cota proprie (`company_current_occupied < company_allocated_quota`).

### Regula 4 (R4 - Acces Standard în Cotă):
Dacă numărul de mașini ocupate este strict mai mic decât cota firmei (`company_current_occupied < company_allocated_quota`), accesul se acordă gratuit: `GRANTED_REGULAR`.

### Regula 5 (R5 - Politica de Suprataxare Overflow):
Dacă cota este epuizată, dar firma are bifată opțiunea `company_allows_overflow == True`:
- Dacă sosirea este în afara orelor de vârf ($\neg \text{is\_peak}$), accesul `GRANTED_PAID_OVERFLOW` este permis.
- Dacă sosirea este la ore de vârf ($\text{is\_peak}$), accesul `GRANTED_PAID_OVERFLOW` este permis **doar dacă** numărul de locuri depășite este strict mai mic de 5 ($\text{occupied} - \text{quota} < 5$).

### Regula 6 (R6 - Respingere Implicită):
În oricare alt caz, accesul este refuzat cu decizia `DENIED_QUOTA_EXCEEDED`.
