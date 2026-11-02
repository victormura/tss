# AI Usage Statement & Team Contribution

**Course:** Software Systems Testing (TSS) — Project 14  
**Topic:** Foundational Property-Based Testing in Haskell  
**Team Members:** Victor Mura & Natalia Moroz  

---

### 1. Team Contributions (Human Ownership & Design)

The conceptual architecture, mathematical adaptation, and code implementation were driven by the team:

- **Theoretical Formulation:** Adapted the formal framework from the ITP 2015 paper (*Paraskevopoulou et al.*) from Coq/Gallina into pure Haskell, formalizing possibilistic generator semantics (`semGen`), checker semantics (`semChecker`), and the three verification theorems (**Soundness**, **Completeness**, **Fidelity**).
- **Haskell Implementation:**
  - Designed the banking transaction domain (`Transaction`, `Currency`, business preconditions, and round-trip serialization).
  - Implemented the certified testing pipeline in `FoundationalPBT.hs` (deterministic PRNG, monadic combinators, and formal verification phases).
  - Built the comparative 5-experiment demo in `Main.hs` and integrated the real Hackage `Test.QuickCheck` suite in `QuickCheckOfficial.hs`.
- **Presentation & Delivery:** Structured the 20-minute presentation (Natalia: theoretical foundations and formal guarantees; Victor: architecture and live demo), designed the slide deck, and authored the verbal presentation script.
- **Validation:** Checked all formal definitions against the cited research paper, eliminated GHC compiler warnings, and validated end-to-end execution with `cabal run`.

---

### 2. AI Assistance

- **Tools Used:** LLM assistance (Antigravity / ChatGPT).
- **Scope:**
  - Scaffolding initial Cabal project configuration and `python-pptx` generation scripts.
  - Assisting with ANSI terminal formatting and box-drawing layouts.
- **Human Review & Corrections:** All AI suggestions were rigorously reviewed, rewritten, and validated by the team (e.g., replacing partial functions with total pattern matching, implementing genuine possibilistic semantics, and refining experimental scenarios).
