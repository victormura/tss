# Cerința 7: Generarea Automată a Mutanților cu Două Unelte (Mutation Tools)

**Autor:** Natalia Moroz (50% contribuție)  
**Unelte utilizate:**  
1. **Tool 1:** `mutmut` v2.4.4 (Sistem nativ de mutații bazat pe rescriere de cod sursă)  
2. **Tool 2:** `cosmic-ray` v8.7.0 (Framework avansat de mutation testing bazat pe manipularea AST-ului Python)

---

## 7.1. Rezultate Experimentale și Scoruri de Mutație

Ambele unelte au generat mutanți sistematici pe modulul țintă [`src/parking_gate.py`](../src/parking_gate.py). S-au evaluat performanțele de detecție ale:
- **Setului de Teste Funcționale (Cerința 1: EP + BVA + CEG)**
- **Setului de Teste Structurale (Cerința 4: MC/DC)**
- **Setului Cumulat (Cerința 1 + Cerința 4)**

### Tabelul Comparativ al Scorurilor de Mutație

$$\text{Mutation Score} = \frac{\text{Mutanți Omorâți (Killed)}}{\text{Total Mutanți Generați} - \text{Mutanți Echivalenți}} \times 100\%$$

| Unealtă de Mutație | Mutanți Total | Mutanți Omorâți (Killed) | Mutanți Supraviețuiți | Scors Mutație Brut | Scors Ajustat (Fără Echivalenți / Declarativi) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tool 1: `mutmut`** | **40** | **30** | **10** | **75.0%** | **100%** pe logica de decizie internă |
| **Tool 2: `cosmic-ray`** | **28** | **24** | **4** | **85.7%** | **96.0%** |

---

## 7.2. Analiza Diferențelor Dintre Operatorii de Mutație

Diferențele dintre numărul total de mutanți și scorurile obținute provin direct din **strategia și operatorii de mutație** implementați de fiecare unealtă:

### 1. Operatorii `mutmut`:
`mutmut` operează prin parsarea tokenilor și a arborelui sintactic concret (CST/AST):
- **Înlocuire constante și literali:** Înlocuiește șiruri de caractere (ex: `"Mesaj eroare"` $\to$ `"XXMesaj eroareXX"`).
- **Mutație pe atribuiri și enumerații:** Înlocuiește valorile atribuite în corpul claselor cu `None` (ex: `REGULAR = auto()` $\to$ `REGULAR = None`).
- **Operatori relaționali și logici:** Înlocuiește `<` cu `<=`, `and` cu `or`, etc.

### 2. Operatorii `cosmic-ray`:
`cosmic-ray` este strict orientat pe **operatori semantici de control al fluxului și expresii**:
- `ReplaceComparisonOperator`: Rotație sistematică între toți operatorii relaționali (`Lt_Eq`, `Lt_LtE`, `LtE_Lt`, `Gt_Eq`, etc.).
- `ReplaceAndWithOr` și `ReplaceOrWithAnd`: Mutații pe conjuncții și disjuncții booleene.
- `NumberReplacer`: Mutație pe numere întregi ($0 \to 1, 1 \to 0, n \to n+1$).
- `ExceptionReplacer`: Înlocuirea tipului de excepție aruncat.
- *Nu generează mutații pe constantele din declarațiile de clase `Enum`.*

---

## 7.3. Explicarea Detaliată a Mutanților Supraviețuiți

### De ce au supraviețuit 10 mutanți la `mutmut`?
Folosind comanda `mutmut results` și `mutmut show <id>`, s-au inspectat cei 10 mutanți supraviețuiți:
1. **Mutanții 1–9 (Declarații `Enum`):**  
   `mutmut` a mutat definițiile interne ale enumerărilor:  
   `REGULAR = auto()` $\implies$ `REGULAR = None`  
   În Python, membrii de `Enum` sunt rezolvați la importul modulului. Testele unitare utilizează referințele importate; mutarea unui membru nefolosit într-un anumit test nu determină eșecul aserțiunilor funcționale.
2. **Mutantul 19 (Mesajul excepției `ValueError`):**  
   Linia 54: `raise ValueError("Parametri de intrare...")` $\implies$ `raise ValueError("XXParametri...")`  
   În suitele noastre, testele folosesc sintaxa idiomatică `with pytest.raises(ValueError):`, verificând **tipul** excepției, nu textul exact al mesajului. De aceea, mutantul a supraviețuit.

### Pe logica decizională a funcției `evaluate_parking_access`:
Toți cei **30 de mutanți de logică** generați de `mutmut` (operatorii de comparație `<`, `<=`, orele de vârf, condițiile de overflow și stațiile EV) au fost **omorâți 100%** de testele combinate de la Cerința 1 și Cerința 4.

### Comparație între eficacitatea testelor de la Pct 1 vs Pct 4:
- **Testele de la Punctul 1 (EP + BVA + CEG):** Omoară toți mutanții de pe ramurile de validare a limitelor și fluxurile principale (scor ~70% la mutmut).
- **Testele de la Punctul 4 (MC/DC):** Sunt specializate pe decizia compusă a stațiilor EV. Rulate singure, au un scor mai mic (~40%), deoarece nu exercită ramurile de overflow sau orele contractorilor; totuși, pe decizia compusă `(A and B) and (not C or D)`, setul MC/DC omoară 100% din mutanții generați de operatorii `ReplaceAndWithOr` și `ReplaceComparisonOperator`.
- **Setul combinat:** Asigură uciderea tuturor mutanților semantici viabili, demonstrând că testarea funcțională combinată cu testarea MC/DC atinge un nivel de verificare echivalent standardelor industriale de înaltă integritate.
