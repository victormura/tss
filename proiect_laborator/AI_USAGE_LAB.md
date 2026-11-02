# AI Usage Log & Human Ownership Statement — Laboratory Project

**Course:** Software Systems Testing (TSS) — Laboratory Project  
**Team Members:** Victor Mura & Natalia Moroz  
**Topic:** Smart Corporate Multi-Tenant Parking Gate  

---

## 1. Contribuția Echipei și Asumarea Designului (Human Ownership)

Toate conceptele teoretice, deciziile arhitecturale și validările au fost stabilite și asumate direct de membrii echipei:

- **Selecția Domeniului:** Am ales sistemul de parcare corporate multi-tenant pentru a modela reguli de afaceri realiste cu domenii ierarhizate de acces, cote de chiriași și mobilitate electrică (EV).
- **Calibrarea Matematică & Structurală:**
  - Am calibrat complexitatea ciclomatică la $V(G) = 7$ pentru a permite desenarea manuală și auditarea riguroasă a celor 7 căi liniar independente.
  - Am proiectat special condiția de acces EV ca o expresie booleană compusă cu 4 termeni pentru a oferi o bază solidă criteriului **MC/DC**.
- **Partajarea Efortului (50% - 50%):**
  - **Natalia Moroz (50%):** Proiectarea și implementarea seturilor de teste funcționale (Cerința 1: EP, BVA, CEG), analiza comparativă de acoperire prin cod (Cerința 2: `pytest-cov`), scrierea mutantului de ordin 1 echivalent și demonstrația matematică a echivalenței (Cerința 5).
  - **Victor Mura (50%):** Proiectarea grafului orientat de control și calculul căilor independente (Cerința 3), proiectarea tabelelor decizionale și a setului MC/DC (Cerința 4), scrierea manuală a celor doi mutanți ne-echivalenți omorât vs. neomorât (Cerința 6), configurarea, execuția și analiza comparativă a celor două unelte de mutații `mutmut` și `cosmic-ray` (Cerința 7).

---

## 2. Jurnalul Utilizării Asistenței AI (AI Usage Log)

### Înregistrarea 1: Generarea Ideilor de Proiect și Scheletului Inițial
- **Instrument AI utilizat:** Antigravity (Gemini 3.8 Flash High)
- **Scopul utilizării:** Brainstorming teme de laborator calibrate pe cerințele 1-7 din ghidul TSS și generarea scheletului inițial de cod în Python.
- **Promptul adresat:** *„Ajuta-ne cu o tema, idee de program pentru acest proiect (...) un sistem de parcare pentru o companie cu mai multe grupuri de angajati(companii)? ce parere ai de aceasta idee? hai sa folosim python. explicane motorul”*
- **Rezultatul obținut:** Propunerea motorului de decizie `evaluate_parking_access` cu ierarhie de priorități și maparea pe cerințele 1-7.
- **Modificările efectuate de membrii echipei:**
  - Am adaptat regulile de business astfel încât condițiile booleene să nu fie redundante.
  - Am redenumit deciziile și am adăugat validarea defensivă a frontierelor negative.
- **Modul de verificare și validare:** Verificarea manuală a logicii pe cazuri extreme (limite de oră 0 și 23, cote egale cu locurile ocupate).
