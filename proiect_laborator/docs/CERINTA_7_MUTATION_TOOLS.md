# Cerința 7: Generarea Automată a Mutanților cu Două Unelte (Mutation Tools)

**Autor:** Victor Mura (50% contribuție)  
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

| Unealtă de Mutație | Mutanți Total | Mutanți Omorâți (Killed) | Mutanți Supraviețuiți | Scor Mutație Brut | Scor Ajustat (Fără Echivalenți) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tool 1: `mutmut`** | **40** | **40** | **0** | **100.0%** | **100.0%** |
| **Tool 2: `cosmic-ray`** | **101** | **99** | **2** | **98.02%** | **100.0%** (2 mutanți `is` echivalenți) |

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
- `ReplaceComparisonOperator`: Rotație sistematică între toți operatorii relaționali (`Lt_Eq`, `Lt_LtE`, `LtE_Lt`, `Gt_Eq`, `Eq_Is`, etc.).
- `ReplaceAndWithOr` și `ReplaceOrWithAnd`: Mutații pe conjuncții și disjuncții booleene.
- `NumberReplacer`: Mutație pe numere întregi ($0 \to 1, 1 \to 0, n \to n+1$).
- `ReplaceBinaryOperator`: Mutații pe operatori aritmetici (ex: `Sub_Add`, `Sub_Mod`).
- *Nu generează mutații pe constantele din declarațiile de clase `Enum`.*

---

## 7.3. Explicarea Detaliată a Mutanților și a Optimizării Testelor

Inițial, pe setul de bază, supraviețuiseră 10 mutanți la `mutmut` și 3 mutanți la `cosmic-ray`. Printr-o analiză riguroasă a cauzelor, am optimizat suita de teste pentru a atinge eficiență maximă:

1. **Uciderea mutanților pe declarațiile `Enum` (Mutanții 1–9 din `mutmut`):**  
   `mutmut` substituia `auto()` cu `None` (`REGULAR = None`). Am introdus în `tests/test_ep.py` testul `test_ep_enum_integrity`, care verifică aserțiunea `assert member.value is not None` pentru fiecare membru. Toți cei 9 mutanți au fost omorâți instantaneu.
2. **Uciderea mutantului pe mesajul excepției (Mutantul 19 din `mutmut`):**  
   Linia 54: `raise ValueError("Parametri de intrare...")` $\implies$ `raise ValueError("XXParametri...")`.  
   Am ancorat aserțiunile de excepție din `test_ep.py` și `test_bva.py` folosind expresii regulate exacte:  
   `with pytest.raises(ValueError, match=r"^Parametri de intrare în afara domeniilor valide admise\.$"):`.  
   Astfel, prefixul `XX...XX` eșuează aserțiunea regex și mutantul este omorât.
3. **Uciderea mutantului aritmetic `Sub_Mod` din `cosmic-ray`:**  
   Operatorul înlocuia `overflow_count = occupied - quota` cu `occupied % quota`. Deoarece toate testele inițiale foloseau `quota = 10` și `occupied = 14, 15, 16`, operațiile dădeau același rezultat ($x - 10 \equiv x \pmod{10}$). Am adăugat testul `test_bva_overflow_non_decimal_quota_discriminant` cu `quota = 4` și `occupied = 11`, unde $11 - 4 = 7 \ge 5$ (refuzat), dar $11 \pmod 4 = 3 < 5$ (admis eronat). Mutantul a fost omorât.
4. **Mutanții supraviețuitori rămași (2 mutanți `Eq_Is` în `cosmic-ray`):**  
   Singurii 2 mutanți supraviețuitori din întregul proiect sunt:  
   - `tier == EmployeeTier.VIP` $\to$ `tier is EmployeeTier.VIP`  
   - `tier == EmployeeTier.CONTRACTOR` $\to$ `tier is EmployeeTier.CONTRACTOR`  
   În Python, membrii de `Enum` sunt *singletons canonici*. Verificarea de egalitate `==` și verificarea de identitate `is` sunt **100% semantic și matematic echivalente**. Niciun test din lume nu poate ucide acești doi mutanți, fiind un exemplu clasic de mutant echivalent de limbaj.  
   Scorul ajustat al proiectului este așadar **100.0%**.

### Comparație între eficacitatea testelor de la Pct 1 vs Pct 4:
- **Testele de la Punctul 1 (EP + BVA + CEG):** Omoară toți mutanții de pe ramurile de validare a limitelor și fluxurile principale (scor ~70% la mutmut).
- **Testele de la Punctul 4 (MC/DC):** Sunt specializate pe decizia compusă a stațiilor EV. Rulate singure, au un scor mai mic (~40%), deoarece nu exercită ramurile de overflow sau orele contractorilor; totuși, pe decizia compusă `(A and B) and (not C or D)`, setul MC/DC omoară 100% din mutanții generați de operatorii `ReplaceAndWithOr` și `ReplaceComparisonOperator`.
- **Setul combinat:** Asigură uciderea tuturor mutanților semantici viabili, demonstrând că testarea funcțională combinată cu testarea MC/DC atinge un nivel de verificare echivalent standardelor industriale de înaltă integritate.
