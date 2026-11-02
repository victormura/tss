# Cerința 2: Analiză Comparativă a Nivelului de Acoperire de Cod (Code Coverage)

**Autor:** Victor Mura (50% contribuție)  
**Utilitar de acoperire utilizat:** `coverage.py` v7.13.0 via `pytest-cov` v5.0.0 (cu opțiunea de branch coverage `--cov-branch`).

---

## 2.1. Rezultate Masurate Separat

Fiecare set de teste de la Cerința 1 (a, b și c) a fost executat complet izolat împotriva modulului țintă [`src/parking_gate.py`](../src/parking_gate.py).

### Tabel Comparativ de Acoperire

| Set de Teste | Nr. Teste | Linii Acoperite (Statements) | Ramuri Acoperite (Branch Coverage) | Acoperire Totală | Linii / Ramuri Neacoperite |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1.a) Equivalence Partitioning (EP)** | 13 | **29 / 29 (100%)** | **12 / 12 (100%)** | **100%** | *Niciuna (acoperire completă)* |
| **1.b) Boundary Value Analysis (BVA)** | 24 | **27 / 29 (93%)** | **10 / 12 (83%)** | **90%** | Liniile 61, 70 (Regula VIP și ramura EV neexercitată) |
| **1.c) Cause-Effect Graphing (CEG)** | 9 | **28 / 29 (96%)** | **11 / 12 (91%)** | **95%** | Linia 54 (`raise ValueError` pe inputuri invalide) |

---

## 2.2. Comentarii și Analiză Comparativă a Rezultatelor

### 1. Equivalence Partitioning (EP) — Eficiență maximă de acoperire (100%)
- **De ce a atins 100%:** Prin definiție, partiționarea de echivalență obligă testerul să selecteze cel puțin o clasă de date validă și una invalidă pentru **fiecare** flux și regulă a sistemului. Suita EP a inclus cazuri de excepție (`ValueError`), acces VIP, acces de noapte, EV charging și ambele ramuri de overflow.
- **Limitare:** Deși atinge 100% branch coverage, EP nu verifică dacă programul deviază la frontierele numerice (de exemplu, un off-by-one error la ora `17:00` sau cota `occupied == quota` nu este detectat dacă reprezentantul ales este `occupied = 5`).

### 2. Boundary Value Analysis (BVA) — Focus pe robustețea frontierelor (90%)
- **Puncte forte:** BVA a exercitat exhaustiv frontierele critice (`-1, 0, 1`, `7, 8, 9`, `16, 17, 18`, `22, 23, 24`, prag overflow `4, 5, 6`). A acoperit ramurile de validare a datelor și deciziile cantitative.
- **De ce a scăzut acoperirea la 90%:** Valorile de frontieră se aplică variabilelor ordonate (numerice). Parametri precum `EmployeeTier.VIP` sau stările calitative ale mașinilor electrice nu au „valori de frontieră”, motiv pentru care testele strict orientate pe BVA nu au executat ramura VIP (linia 61) sau combinația complexă de stații EV.

### 3. Cause-Effect Graphing (CEG) — Optimizarea deciziilor compuse (95%)
- **Puncte forte:** Cu doar 9 cazuri de testare (cel mai mic set), CEG a atins 95% acoperire globală și a acoperit toate combinațiile logice ale regulilor de afaceri.
- **De ce lipsește linia 54:** Graful Cauză-Efect s-a concentrat pe cauzele logice ale specificației operaționale valide. Validarea defensivă a parametrilor de sistem (date corupte) nu a fost modelată ca o „cauză de business” în graf, motiv pentru care ramura de excepție a rămas neacoperită în acest set izolat.

### Concluzie
Cele trei tehnici sunt **complementare**:
- **BVA** este indispensabilă pentru prevenirea erorilor de tip *off-by-one*.
- **CEG** este indispensabilă pentru testarea logicii decizionale complexe cu un număr minim de teste.
- **EP** asigură că nicio categorie majoră de date nu este omisă.
