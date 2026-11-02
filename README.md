# Software Systems Testing (TSS) — Master IS, Year II

**University of Bucharest — Faculty of Mathematics and Computer Science**  
**Course:** Testarea Sistemelor Software (TSS)  
**Authors:** Victor Mura & Natalia Moroz  

---

## 📂 Repository Structure

This repository contains both academic projects developed for the TSS course:

### 1. Course Project: Foundational Property-Based Testing in Haskell
- **Location:** [`demo/`](demo/), [`presentation/`](presentation/)
- **Topic:** Certified & Foundational Property-Based Testing (adapted from the ITP 2015 research paper by Paraskevopoulou et al.).
- **Stack:** Haskell, Cabal, QuickCheck, Monadic Possibilistic Generators.
- **Deliverables:** Complete runnable demo with 5 comparison experiments, research adaptation, verbal script, and slide deck.
- **Statement:** [`AI-USAGE.md`](AI-USAGE.md)

### 2. Laboratory Project: Smart Corporate Multi-Tenant Parking Gate
- **Location:** [`proiect_laborator/`](proiect_laborator/)
- **Topic:** Systematic Black-Box, White-Box, and Mutation Testing on a deterministic corporate gate access decision engine.
- **Stack:** Python 3.11, `pytest`, `coverage.py` / `pytest-cov`, `mutmut`, `cosmic-ray`.
- **All 7 Requirements Covered:**
  - **Requirement 1 (Victor Mura):** Equivalence Partitioning (EP), Boundary Value Analysis (BVA), Cause-Effect Graphing (CEG)
  - **Requirement 2 (Victor Mura):** Isolated Code Coverage Analysis via `pytest-cov`
  - **Requirement 3 (Natalia Moroz):** Control Flow Graph (CFG), Cyclomatic Complexity $V(G) = 7$, 7 Linearly Independent Paths
  - **Requirement 4 (Natalia Moroz):** Modified Condition / Decision Coverage (MC/DC) with 5 minimal test cases
  - **Requirement 5 (Natalia Moroz):** Order-1 Equivalent Mutant with formal equivalence proof
  - **Requirement 6 (Victor Mura):** Non-equivalent Mutants (Killed vs. Survived) under a specific test case
  - **Requirement 7 (Natalia Moroz):** Comparative Mutation Testing with `mutmut` and `cosmic-ray`
- **Documentation:** [`proiect_laborator/README.md`](proiect_laborator/README.md)
- **AI Usage Log:** [`proiect_laborator/AI_USAGE_LAB.md`](proiect_laborator/AI_USAGE_LAB.md)
