# Proiect de Laborator: Smart Corporate Multi-Tenant Parking Gate

**Disciplina:** Testarea Sistemelor Software (TSS)  
**Instituție:** Universitatea din București — Facultatea de Matematică și Informatică  
**Program de Master:** Ingineria Sistemelor Software (Master IS), Anul II  
**Echipa de Proiect:**
- **Victor Mura** — Contribuție 50%
- **Natalia Moroz** — Contribuție 50%

---

## 📋 Structura Proiectului și Repartizarea Cerințelor

Proiectul acoperă integral cerințele 1–7 din ghidul de laborator, conform contribuțiilor declarate:

| Cerință | Titlu Cerință | Membru Responsabil | Pondere | Documentație / Cod Sursă |
| :---: | :--- | :---: | :---: | :--- |
| **1** | **Testare Funcțională (EP, BVA, CEG)** | **Natalia Moroz** | 20% | [`docs/CERINTA_1_FUNCTIONAL_TESTING.md`](docs/CERINTA_1_FUNCTIONAL_TESTING.md)<br>Teste: [`tests/test_ep.py`](tests/test_ep.py), [`tests/test_bva.py`](tests/test_bva.py), [`tests/test_ceg.py`](tests/test_ceg.py) |
| **2** | **Analiză Acoperire de Cod (Coverage)** | **Natalia Moroz** | 15% | [`docs/CERINTA_2_CODE_COVERAGE.md`](docs/CERINTA_2_CODE_COVERAGE.md)<br>Rapoarte obținute cu `pytest-cov` |
| **3** | **Testare Structurală (CFG, V(G), Căi Independente)** | **Victor Mura** | 15% | [`docs/CERINTA_3_CFG_COMPLEXITATE.md`](docs/CERINTA_3_CFG_COMPLEXITATE.md)<br>Graf Mermaid + 7 căi liniar independente |
| **4** | **MC/DC (Modified Condition/Decision Coverage)** | **Victor Mura** | 15% | [`docs/CERINTA_4_MCDC.md`](docs/CERINTA_4_MCDC.md)<br>Tabel adevăr + Teste: [`tests/test_mcdc.py`](tests/test_mcdc.py) |
| **5** | **Mutant Echivalent de Ordinul 1** | **Natalia Moroz** | 15% | [`docs/CERINTA_5_MUTANT_ECHIVALENT.md`](docs/CERINTA_5_MUTANT_ECHIVALENT.md)<br>Cod: [`mutants/equivalent_mutant.py`](mutants/equivalent_mutant.py)<br>Test: [`tests/test_equivalent_mutant.py`](tests/test_equivalent_mutant.py) |
| **6** | **Mutanți Ne-Echivalenți (Omorât vs. Neomorât)** | **Victor Mura** | 10% | [`docs/CERINTA_6_MUTANTI_MANUALI.md`](docs/CERINTA_6_MUTANTI_MANUALI.md)<br>Cod: [`mutants/manual_mutants.py`](mutants/manual_mutants.py)<br>Test: [`tests/test_manual_mutants.py`](tests/test_manual_mutants.py) |
| **7** | **Mutații Automate (`mutmut` & `cosmic-ray`)** | **Victor Mura** | 10% | [`docs/CERINTA_7_MUTATION_TOOLS.md`](docs/CERINTA_7_MUTATION_TOOLS.md)<br>Analiză comparativă operatori și scoruri |
| **—** | **Declarație Utilizare AI (AI Usage)** | **Echipa** | — | [`AI_USAGE_LAB.md`](AI_USAGE_LAB.md) |

---

## 🚀 Rularea Testelor și Verificarea

### 1. Rularea completă a testelor:
```bash
cd proiect_laborator
pytest -v
```

### 2. Rularea raportului de acoperire de cod (Cerința 2):
```bash
# Setul 1.a (EP)
pytest tests/test_ep.py --cov=src --cov-branch --cov-report=term-missing

# Setul 1.b (BVA)
pytest tests/test_bva.py --cov=src --cov-branch --cov-report=term-missing

# Setul 1.c (CEG)
pytest tests/test_ceg.py --cov=src --cov-branch --cov-report=term-missing
```

### 3. Rularea testelor MC/DC (Cerința 4):
```bash
pytest tests/test_mcdc.py -v
```

### 4. Rularea uneltei de mutații mutmut (Cerința 7):
```bash
mutmut run --paths-to-mutate=src/parking_gate.py
mutmut results
```
