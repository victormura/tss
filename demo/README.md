# Foundational Property-Based Testing (FPBT) în Haskell

Acest proiect implementează tehnica **Foundational Property-Based Testing (FPBT)** în Haskell și o compară direct, pas cu pas, cu **Property-Based Testing (PBT) convențional** (în stil QuickCheck).

Lucrarea de referință este articolul seminal:
> **Zoe Paraskevopoulou, Cătălin Hrițcu, Maxime Dénès, Leonidas Lampropoulos, Benjamin C. Pierce.**  
> *“Foundational Property-Based Testing.”* International Conference on Interactive Theorem Proving (ITP 2015).  
> <https://lemonidas.github.io/pdf/Foundational.pdf>

---

## 1. Problema: De ce PBT convențional nu este suficient?

În PBT convențional (QuickCheck, Hypothesis etc.), un generator este o **cutie neagră probabilistică** de tip `Seed -> Size -> A`. Verificatorul execută $N$ eșantioane pseudo-aleatoare și raportează:
```
+++ OK, passed 100 tests.
```

Această abordare empirică suferă de trei vulnerabilități fundamentale:

1. **Incompletitudinea generatorului (Falsă siguranță / False Confidence):**  
   Dacă generatorul are un unghi mort (de exemplu, produce doar tranzacții în `RON` și omite `EUR` și `USD`), testul raportează *100 de teste trecute*, deși codul are un bug critic pentru celelalte monede. PBT convențional nu poate ști ce valori **nu** au fost generate.
2. **Generatoare nevalide (Erori false / Spurious Counterexamples):**  
   Dacă generatorul produce intrări care încalcă precondiția de business (de exemplu sume negative sau ID-uri invalide), testul eșuează dând vina pe codul testat (SUT), irosind timpul dezvoltatorilor pe bug-uri care aparțin de fapt generatorului.
3. **Discrepanța dintre verificator și specificație (Checker Drift):**  
   Dacă verificatorul executabil omite verificarea unui câmp (de exemplu verifică doar suma, ignorând moneda), codul eronat trece testele fără avertisment.

---

## 2. Soluția: Foundational Property-Based Testing

În Foundational PBT, generatoarele și verificatorii primesc o **semantică denotațională formală**:

- **Semantica generatorului (`semGen`):**  
  $$\text{semGen} : G(A) \to \mathcal{P}(A)$$  
  Mulțimea tuturor valorilor pe care generatorul le poate produce cu probabilitate nenulă.
- **Semantica verificatorului (`semChecker`):**  
  Propoziția logică conform căreia niciun rezultat produs de generator nu este un contraexemplu.

Înainte de testare, cadrul foundational verifică trei teoreme formale:

1. **Corectitudinea generatorului (Generator Soundness):**  
   $$\forall x \in \text{semGen}(G),\; \Phi(x)$$  
   *Fiecare valoare generată respectă precondiția/invariantul de domeniu.*
2. **Completitudinea generatorului (Generator Completeness / Adequacy):**  
   $$\forall x \in \text{Domain},\; \Phi(x) \implies x \in \text{semGen}(G)$$  
   *Generatorul poate acoperi toate cazurile valide din domeniu (fără unghiuri moarte).*
3. **Fidelitatea verificatorului (Checker Fidelity):**  
   $$\forall x \in \text{semGen}(G),\; \text{Checker}(x) \iff \text{Spec}(x)$$  
   *Verificatorul executabil corespunde întocmai specificației logice.*

---

## 3. Arhitectura implementării în Haskell

Sistemul este împărțit în două module:

1. **`FoundationalPBT.hs`**:
   - `data FGen a`: Monadă care poartă atât funcția de eșantionare pseudo-aleatoare (`Seed -> Int -> (a, Seed)`), cât și semantica denotațională exactă `semGen : FGen a -> Set a`.
   - Combinatori certificați: `returnFGen`, `bindFGen`, `elementsFGen`, `chooseIntFGen`, `suchThatFGen`, `frequencyFGen`, `sizedFGen`.
   - Motor de verificare formală: `verifySoundness`, `verifyCompleteness`, `verifyFidelity`.
   - Pipeline de certificare: `runFoundationalTest`.
2. **`Main.hs`**:
   - Modelul de business: tipul `Transaction` (ID pozitiv, sumă în bani $\ge 0$, monedele `RON`, `EUR`, `USD`).
   - SUT: `encode` și `decode` corecte, vs. `encodeBug` (bug deliberat care forțează moneda la `RON`).
   - Cinci experimente comparative rulate direct în consolă.

---

## 4. Rulare

Din acest director:

```sh
cabal run
```

Sau direct cu compilatorul GHC (fără dependențe externe din Hackage, folosind doar `base` și `containers`):

```sh
ghc -O2 Main.hs FoundationalPBT.hs -o demo && ./demo
```

Dacă folosiți Docker:

```sh
docker run --rm -v "$PWD:/workspace" -w /workspace/demo haskell:9.6-slim cabal run
```

---

## 5. Cele 5 experimente demonstrate

| Experiment | Situație testată | Comportament PBT convențional | Comportament Foundational PBT |
| :--- | :--- | :--- | :--- |
| **1. Generator Incomplet** | `encodeBug` + `fgenRonOnlyTx` | `+++ OK, passed 100 tests.` <br>**(Trecere falsă periculoasă!)** | Calculează `semGen`, detectează acoperire de doar 33% și **respinge suita de teste**. |
| **2. Generator Nevalid** | `encode` corect + `fgenUnsoundTx` (ID negativ) | `*** Failed!` <br>**(Dă vina pe codul corect!)** | Verifică `semGen \subseteq \Phi`, **izolează bug-ul în generator** și protejează codul testat. |
| **3. Verificator Eronat** | `encodeBug` + `checkBuggyChecker` (ignoră moneda) | `+++ OK, passed 100 tests.` <br>**(Derivă netestată)** | Verifică `Checker \iff Spec` și **respinge verificatorul infidel**. |
| **4. Testare Certificată pe Cod Eronat** | `encodeBug` + `fgenCompleteTx` | Eșuează probabilistic. | Toate certificatele trec, apoi găsește și micșorează (**shrink**) contraexemplul minimal garantat valid: `Transaction {id = 1, cents = 0, currency = EUR}`. |
| **5. Testare Certificată pe Cod Corect** | `encode` corect + `fgenCompleteTx` | 100 de teste trecute fără garanție formală. | **Certificat formal emis**: 100% acoperire a claselor de echivalență, generator valid și verificator echivalent cu specificația. |

---

## 6. Tabel recapitulativ

| Dimensiune | PBT convențional (QuickCheck) | Foundational PBT (FPBT) |
| :--- | :--- | :--- |
| **Reprezentarea generatorului** | Cutie neagră (`Seed -> Size -> a`) | Monadă cu semantică denotațională (`semGen : G a -> Set a`) |
| **Generator incomplet** | Trecere silențioasă (**fals pozitiv**) | Detectat formal & respins |
| **Generator nevalid** | Eșec fals (**eroare învinuită greșit**) | Detectat formal & izolat |
| **Discrepanță în verificator** | Netestată, poate trece erori | Detectată prin contraexemple la nivel de specificație |
| **Garanție de acoperire** | Pur statistică | Completitudine demonstrată ($\text{Domain} \subseteq \text{semGen}$) |
| **Origine teoretică** | Claessen & Hughes (ICFP 2000) | Paraskevopoulou et al. (ITP 2015) |

> **Concluzia proiectului:**  
> Testarea bazată pe proprietăți cu fundamente formale nu se mulțumește să testeze programul; **ea verifică matematic și codul de testare (generatoarele și verificatorii)!**
