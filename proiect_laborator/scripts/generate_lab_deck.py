"""
Generator de Prezentare PowerPoint & PDF pentru Proiectul de Laborator TSS
Tema: Smart Corporate Multi-Tenant Parking Gate
Echipa: Victor Mura (50%) & Natalia Moroz (50%)
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# Dimensiuni 16:9 Widescreen
W_INCHES = 13.333
H_INCHES = 7.5

# Paletă de culori modernă Dark / Teal
BG_NAVY = RGBColor(20, 36, 59)        # #14243B
CARD_NAVY = RGBColor(32, 55, 82)      # #203752
CARD_DARK = RGBColor(24, 43, 67)      # #182B43
TEAL_ACCENT = RGBColor(19, 138, 131)  # #138A83
MINT_LIGHT = RGBColor(121, 201, 192)  # #79C9C0
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_LIGHT = RGBColor(220, 228, 235)  # #DCE4EB
TEXT_MUTED = RGBColor(175, 193, 206)  # #AFC1CE
STATUS_GREEN = RGBColor(78, 191, 133)
STATUS_AMBER = RGBColor(235, 175, 65)

FONT_MAIN = "Arial"


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(W_INCHES)
    prs.slide_height = Inches(H_INCHES)
    blank_layout = prs.slide_layouts[6]

    def set_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W_INCHES), Inches(H_INCHES))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_NAVY
        bg.line.fill.background()
        return bg

    def add_header(slide, title, section_badge, presenter_name, page_num):
        # Bară de accent stânga
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.45), Inches(0.08), Inches(0.75))
        bar.fill.solid()
        bar.fill.fore_color.rgb = TEAL_ACCENT
        bar.line.fill.background()

        # Badge secțiune
        badge_box = slide.shapes.add_textbox(Inches(1.05), Inches(0.42), Inches(6.0), Inches(0.28))
        tf_b = badge_box.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = f"TSS LABORATORY PROJECT  •  {section_badge.upper()}"
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(10)
        p_b.font.bold = True
        p_b.font.color.rgb = MINT_LIGHT

        # Titlu slide
        t_box = slide.shapes.add_textbox(Inches(1.05), Inches(0.70), Inches(8.5), Inches(0.55))
        tf_t = t_box.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

        # Prezentator / Contribuție
        pres_box = slide.shapes.add_textbox(Inches(9.2), Inches(0.45), Inches(3.3), Inches(0.4))
        tf_p = pres_box.text_frame
        p_p = tf_p.paragraphs[0]
        p_p.alignment = PP_ALIGN.RIGHT
        p_p.text = f"Responsabil: {presenter_name}"
        p_p.font.name = FONT_MAIN
        p_p.font.size = Pt(11)
        p_p.font.bold = True
        p_p.font.color.rgb = STATUS_GREEN

        # Număr slide
        num_box = slide.shapes.add_textbox(Inches(11.5), Inches(6.9), Inches(1.0), Inches(0.3))
        tf_n = num_box.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.text = f"{page_num} / 11"
        p_n.font.name = FONT_MAIN
        p_n.font.size = Pt(10)
        p_n.font.color.rgb = TEXT_MUTED

    def add_card(slide, x, y, w, h, fill_color=CARD_NAVY, border_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
        card.fill.solid()
        card.fill.fore_color.rgb = fill_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: TITLU
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_background(s1)

    c1 = add_card(s1, 1.2, 1.2, 10.9, 5.1, fill_color=CARD_NAVY, border_color=TEAL_ACCENT)
    tb_t = s1.shapes.add_textbox(Inches(1.6), Inches(1.6), Inches(10.1), Inches(4.3))
    tf1 = tb_t.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "TESTAREA SISTEMELOR SOFTWARE (TSS)  •  PROIECT DE LABORATOR"
    p.font.name = FONT_MAIN
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = MINT_LIGHT

    p = tf1.add_paragraph()
    p.text = "Smart Corporate Multi-Tenant Parking Gate"
    p.font.name = FONT_MAIN
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    p = tf1.add_paragraph()
    p.text = "Verificare Funcțională, Analiză Structurală MC/DC și Mutation Testing pe Motorul de Decizie"
    p.font.name = FONT_MAIN
    p.font.size = Pt(15)
    p.font.color.rgb = TEXT_LIGHT

    p = tf1.add_paragraph()
    p.text = "\nEchipa de Proiect (Contribuții 50% - 50%):"
    p.font.name = FONT_MAIN
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = MINT_LIGHT

    p = tf1.add_paragraph()
    p.text = "• Victor Mura (50%): Testare Funcțională (EP, BVA, CEG), Analiză Coverage Separat, Mutanți Manuali Ne-Echivalenți"
    p.font.name = FONT_MAIN
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_LIGHT

    p = tf1.add_paragraph()
    p.text = "• Natalia Moroz (50%): Analiză Structurală (CFG, V(G)=7, Căi Liniar Independente), MC/DC, Mutant Echivalent, Mutation Tools"
    p.font.name = FONT_MAIN
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_LIGHT

    p = tf1.add_paragraph()
    p.text = "\nUniversitatea din București  •  Master Ingineria Sistemelor Software (Anul II)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 2: SPECIFICAȚIA PROBLEMEI
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_background(s2)
    add_header(s2, "Contextul Problemei & Specificația Programului", "Specificație Funcțională", "Echipa (Victor & Natalia)", 2)

    add_card(s2, 0.8, 1.4, 5.7, 5.2)
    tb2a = s2.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf2a = tb2a.text_frame
    tf2a.word_wrap = True

    p = tf2a.paragraphs[0]
    p.text = "🏢 Scenariul de Business Multi-Tenant"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    bullets2a = [
        "Un parc de birouri modern găzduiește multiple companii chiriașe cu cote contractuale fixe de locuri gratuite.",
        "Bariera inteligentă scanează vehiculul și decide accesul instant pe baza a 7 factori deterministi.",
        "Infrastructura dispune de stații comune de încărcare electrică (EV) și o zonă de overflow contra cost.",
        "Metoda centrală testată: evaluate_parking_access(...) implementată pur în Python 3.11, fără I/O nedeterminist."
    ]
    for b in bullets2a:
        p = tf2a.add_paragraph(); p.text = f"• {b}"; p.font.size = Pt(11.5); p.font.color.rgb = TEXT_LIGHT

    add_card(s2, 6.8, 1.4, 5.7, 5.2)
    tb2b = s2.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf2b = tb2b.text_frame
    tf2b.word_wrap = True

    p = tf2b.paragraphs[0]
    p.text = "⚙️ Ierarhia Regulilor Decizionale"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    rules = [
        ("R0. Validare Defensivă", "Aruncă ValueError la ore < 0 sau > 23, cote <= 0, locuri ocupate negative."),
        ("R1. Protocol VIP", "Acces garantat necondiționat pe loc dedicat (GRANTED_VIP)."),
        ("R2. Securitate Contractor", "Acces permis strict între orele 08:00 - 17:59 (DENIED_RESTRICTED_HOURS altfel)."),
        ("R3. Stații Încărcare EV", "Condiție compusă: Mașină EV + Stație liberă + (Off-peak SAU în cota firmei)."),
        ("R4. Cotă Gratuită", "Locuri ocupate < Cota firmei -> GRANTED_REGULAR."),
        ("R5. Clauză Overflow", "Peste cotă, dar firma plătește overflow (noaptea oricât, ziua < 5 locuri depășire)."),
        ("R6. Respingere", "Cotă epuizată și fără overflow -> DENIED_QUOTA_EXCEEDED.")
    ]
    for r_title, r_desc in rules:
        p = tf2b.add_paragraph()
        p.text = f"{r_title}: {r_desc}"
        p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 3: CERINȚA 1 (EP & BVA)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_background(s3)
    add_header(s3, "Cerința 1 (a & b): Equivalence Partitioning & Boundary Value Analysis", "Black-Box Testing", "Victor Mura (20%)", 3)

    add_card(s3, 0.8, 1.4, 5.7, 5.2)
    tb3a = s3.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf3a = tb3a.text_frame; tf3a.word_wrap = True
    p = tf3a.paragraphs[0]
    p.text = "📊 Equivalence Partitioning (13 Teste)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    ep_items = [
        "Cota firmei (q): Valid [1, inf) | Invalide q = 0, q < 0 (ValueError).",
        "Locuri ocupate (o): Sub cotă (o < q), La cotă (o = q), Peste cotă (o > q) | Invalid o < 0.",
        "Ora sosirii (h): Off-peak dimineață [0, 7], Peak hours [8, 17], Off-peak seară [18, 23] | Invalide h < 0, h >= 24.",
        "Rol angajat: REGULAR, VIP (prioritar), CONTRACTOR (restricționat orar).",
        "Opțiuni booleene: EV solicitat/disponibil, politică overflow activă/inactivă.",
        "Implementare: tests/test_ep.py — acoperire completă a tuturor claselor valide și invalide."
    ]
    for it in ep_items:
        p = tf3a.add_paragraph(); p.text = f"• {it}"; p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    add_card(s3, 6.8, 1.4, 5.7, 5.2)
    tb3b = s3.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf3b = tb3b.text_frame; tf3b.word_wrap = True
    p = tf3b.paragraphs[0]
    p.text = "🎯 Boundary Value Analysis (24 Teste)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    bva_items = [
        "Frontiere Cotă: 0 (invalid), 1 (min valid), 2 (min + 1).",
        "Frontiere Ocupat: -1 (invalid), 0 (min valid), 1 (min + 1).",
        "Frontiere Relaționale Cotă (q = 10): o = 9 (sub cotă -> Regular), o = 10 (la cotă -> Denied), o = 11 (peste cotă).",
        "Frontiere Orar Extrem: -1 (invalid), 0, 1 și 22, 23, 24 (invalid).",
        "Frontiere Interval Vârf: 7 (off-peak), 8 (start vârf), 9; 16, 17 (sfârșit vârf), 18 (off-peak).",
        "Prag Critic Overflow Ziua: diferență = 4 (permis), 5 (respins - limita strictă < 5), 6 (respins).",
        "Implementare: tests/test_bva.py — detecție off-by-one."
    ]
    for it in bva_items:
        p = tf3b.add_paragraph(); p.text = f"• {it}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 4: CERINȚA 1.c (CAUSE-EFFECT GRAPHING)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_background(s4)
    add_header(s4, "Cerința 1.c: Cause-Effect Graphing (CEG) & Tabel de Decizie", "Black-Box Testing", "Victor Mura (15%)", 4)

    add_card(s4, 0.8, 1.4, 5.7, 5.2)
    tb4a = s4.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf4a = tb4a.text_frame; tf4a.word_wrap = True
    p = tf4a.paragraphs[0]
    p.text = "🕸️ Graful Cauză-Efect: Cauze & Porți Logice"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    ceg_causes = [
        "C1: tier == VIP  |  C2: tier == CONTRACTOR (Exclusivitate E(C1, C2))",
        "C3: is_peak_hours (08:00 - 17:59)",
        "C4: is_electric_vehicle  |  C5: has_ev_spots_available",
        "C6: is_within_quota (occupied < quota)",
        "C7: company_allows_overflow  |  C8: overflow_count < 5",
        "Noduri Intermediare (Porți AND / OR / NOT):",
        "  I1 = NOT(C3) (sosire în afara orelor de vârf)",
        "  I2 = C2 AND I1 (contractor noaptea -> respins orar)",
        "  I3 = C4 AND C5 (vehicul EV cu încărcător liber)",
        "  I4 = I1 OR C6 (condiție relaxată EV: noaptea sau în cotă)",
        "  I5 = I3 AND I4 -> Acces la stația EV",
        "  I7 = C7 AND (I1 OR C8) -> Acces aprobat la Overflow"
    ]
    for c in ceg_causes:
        p = tf4a.add_paragraph(); p.text = f"• {c}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    add_card(s4, 6.8, 1.4, 5.7, 5.2)
    tb4b = s4.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf4b = tb4b.text_frame; tf4b.word_wrap = True
    p = tf4b.paragraphs[0]
    p.text = "📋 Tabelul de Decizie Derivat (9 Reguli)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    rules_ceg = [
        ("R1", "C1=1 -> E1: GRANTED_VIP (fără condiționări suplimentare)."),
        ("R2", "C1=0, C2=1, C3=0 -> E2: DENIED_RESTRICTED_HOURS."),
        ("R3", "Non-VIP, C3=0 (off-peak), C4=1, C5=1 -> E3: GRANTED_EV_CHARGING."),
        ("R4", "Non-VIP, C3=1 (peak), C4=1, C5=1, C6=1 -> E3: GRANTED_EV_CHARGING."),
        ("R5", "Non-VIP, Non-EV, C6=1 (în cotă) -> E4: GRANTED_REGULAR."),
        ("R6", "Peste cotă, C7=1 (overflow), C3=0 (off-peak) -> E5: GRANTED_PAID_OVERFLOW."),
        ("R7", "Peste cotă, C7=1, C3=1 (peak), C8=1 (< 5) -> E5: GRANTED_PAID_OVERFLOW."),
        ("R8", "Peste cotă, C7=1, C3=1, C8=0 (>= 5) -> E6: DENIED_QUOTA_EXCEEDED."),
        ("R9", "Peste cotă, C7=0 (fără overflow) -> E6: DENIED_QUOTA_EXCEEDED.")
    ]
    for r_k, r_t in rules_ceg:
        p = tf4b.add_paragraph(); p.text = f"{r_k}: {r_t}"; p.font.size = Pt(10); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 5: CERINȚA 2 (CODE COVERAGE)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_background(s5)
    add_header(s5, "Cerința 2: Analiză Comparativă a Acoperirii de Cod", "Code Coverage", "Victor Mura (15%)", 5)

    add_card(s5, 0.8, 1.4, 11.7, 2.2, fill_color=CARD_NAVY, border_color=TEAL_ACCENT)
    tb5a = s5.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(2.0))
    tf5a = tb5a.text_frame; tf5a.word_wrap = True
    p = tf5a.paragraphs[0]
    p.text = "📈 Rezultate Obținute Separat (pytest-cov --cov-branch pe src/parking_gate.py)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    p = tf5a.add_paragraph()
    p.text = "• Equivalence Partitioning (13 teste): 29/29 Linii (100%)  •  12/12 Ramuri (100%)  •  Acoperire Globală: 100%"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = STATUS_GREEN

    p = tf5a.add_paragraph()
    p.text = "• Boundary Value Analysis (24 teste): 27/29 Linii (93%)  •  10/12 Ramuri (83%)  •  Acoperire Globală: 90%"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = STATUS_AMBER

    p = tf5a.add_paragraph()
    p.text = "• Cause-Effect Graphing (9 teste):    28/29 Linii (96%)  •  11/12 Ramuri (91%)  •  Acoperire Globală: 95%"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    add_card(s5, 0.8, 3.8, 11.7, 2.8, fill_color=CARD_DARK)
    tb5b = s5.shapes.add_textbox(Inches(1.0), Inches(3.9), Inches(11.3), Inches(2.6))
    tf5b = tb5b.text_frame; tf5b.word_wrap = True
    p = tf5b.paragraphs[0]
    p.text = "💡 Comentarii & Interpretarea Calitativă a Rezultatelor"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    comments = [
        "EP (100%): Eficiență maximă de ramificare structurală. Forțează parcurgerea fiecărei categorii valide și invalide (ValueError, VIP, EV, Overflow). Limitare: nu garantează corectitudinea la limita exactă a intervalului.",
        "BVA (90%): Se concentrează exclusiv pe variabile continue/ordonate (numere). Neacoperirea liniei 61 (VIP) și a ramurii EV provine din faptul că VIP și EV sunt decizii calitative discrete, nu frontiere numerice.",
        "CEG (95%): Cu doar 9 cazuri de test (cel mai compact set), acoperă aproape toate ramurile de business. Singura linie neacoperită este linia 54 (raise ValueError), deoarece CEG a modelat doar combinațiile operaționale valide ale parcului.",
        "Concluzie Metodologică: Tehnicile sunt strict complementare — BVA previne erorile de tip off-by-one, CEG optimizează deciziile logice compuse, iar EP garantează că niciun domeniu de date nu este neglijat."
    ]
    for c in comments:
        p = tf5b.add_paragraph(); p.text = f"• {c}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 6: CERINȚA 3 (CFG & COMPLEXITATE)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_background(s6)
    add_header(s6, "Cerința 3: Graful de Control (CFG) și Complexitatea Ciclomatică", "White-Box Testing", "Natalia Moroz (15%)", 6)

    add_card(s6, 0.8, 1.4, 5.7, 5.2)
    tb6a = s6.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf6a = tb6a.text_frame; tf6a.word_wrap = True
    p = tf6a.paragraphs[0]
    p.text = "📐 Structura Grafului CFG & Calculul V(G)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    p = tf6a.add_paragraph()
    p.text = "Graful orientat are N = 14 noduri de bază și E = 19 arce decizionale conectate la nodul terminal N14 (Exit)."
    p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    p = tf6a.add_paragraph()
    p.text = "\nCalculul Complexității Ciclomatice prin 3 Metode:"
    p.font.size = Pt(12); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    calc_methods = [
        "1. Formula muchii & noduri: V(G) = E - N + 2P = 19 - 14 + 2(1) = 7",
        "2. Formula noduri predicat: V(G) = P_predicat + 1 = 6 + 1 = 7\n   (Nodurile predicat cu >= 2 ieșiri sunt: N1, N3, N5, N7, N9, N11)",
        "3. Formula regiunilor plane: V(G) = R = 6 regiuni închise + 1 deschisă = 7",
        "Concluzie Matematică: Toate cele 3 formalisme converg riguros către V(G) = 7 circuite independente."
    ]
    for cm in calc_methods:
        p = tf6a.add_paragraph(); p.text = f"• {cm}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    add_card(s6, 6.8, 1.4, 5.7, 5.2)
    tb6b = s6.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf6b = tb6b.text_frame; tf6b.word_wrap = True
    p = tf6b.paragraphs[0]
    p.text = "🛤️ Baza celor 7 Căi Liniar Independente"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    paths = [
        ("Path 1", "N1 -> N2 -> N14 (Eroare Validare: q <= 0 -> ValueError)"),
        ("Path 2", "N1 -> N3 -> N4 -> N14 (VIP -> GRANTED_VIP)"),
        ("Path 3", "N1 -> N3 -> N5 -> N6 -> N14 (Contractor noaptea -> DENIED_RESTRICTED_HOURS)"),
        ("Path 4", "N1 -> N3 -> N5 -> N7 -> N8 -> N14 (EV aprobat -> GRANTED_EV_CHARGING)"),
        ("Path 5", "N1 -> N3 -> N5 -> N7 -> N9 -> N10 -> N14 (În cotă -> GRANTED_REGULAR)"),
        ("Path 6", "N1 -> N3 -> N5 -> N7 -> N9 -> N11 -> N12 -> N14 (Overflow aprobat -> GRANTED_PAID_OVERFLOW)"),
        ("Path 7", "N1 -> N3 -> N5 -> N7 -> N9 -> N11 -> N13 -> N14 (Cotă plină -> DENIED_QUOTA_EXCEEDED)")
    ]
    for p_id, p_desc in paths:
        p = tf6b.add_paragraph(); p.text = f"• {p_id}: {p_desc}"; p.font.size = Pt(10); p.font.color.rgb = TEXT_LIGHT

    p = tf6b.add_paragraph()
    p.text = "\nAcest set acoperă 100% din muchiile grafului."
    p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = STATUS_GREEN

    # ==========================================
    # SLIDE 7: CERINȚA 4 (MC/DC)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_background(s7)
    add_header(s7, "Cerința 4: Modified Condition / Decision Coverage (MC/DC)", "Structural Testing", "Natalia Moroz (15%)", 7)

    add_card(s7, 0.8, 1.4, 5.7, 5.2)
    tb7a = s7.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf7a = tb7a.text_frame; tf7a.word_wrap = True
    p = tf7a.paragraphs[0]
    p.text = "🎯 Decizia Compusă & Standardul DO-178C"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    mcdc_intro = [
        "Criteriul MC/DC (standardul aeronautic DO-178C Level A) impune ca fiecare condiție atomică să influențeze decizia independent de celelalte.",
        "Pentru N = 4 condiții, numărul minim teoretic este N + 1 = 5 teste.",
        "Decizia analizată (Regula 3 - Stații EV):",
        "  Decision_EV = (A and B) and (not C or D)",
        "unde:",
        "  A = is_electric_vehicle",
        "  B = has_ev_spots_available",
        "  C = is_peak_hours (not C = off-peak)",
        "  D = is_within_quota (occupied < quota)"
    ]
    for it in mcdc_intro:
        p = tf7a.add_paragraph(); p.text = f"• {it}"; p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    add_card(s7, 6.8, 1.4, 5.7, 5.2)
    tb7b = s7.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf7b = tb7b.text_frame; tf7b.word_wrap = True
    p = tf7b.paragraphs[0]
    p.text = "🧪 Perechi de Independență & Set Minimal (5 Teste)"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    pairs = [
        ("T1: (1, 1, 0, 0) -> Decision = True", "Bază Adevărată (EV, Spot liber, Off-peak, Peste cotă)"),
        ("T2: (0, 1, 0, 0) -> Decision = False", "Pereche Independență A: (T1, T2) -> Doar A comută 1->0, forțând decizia 1->0."),
        ("T3: (1, 0, 0, 0) -> Decision = False", "Pereche Independență B: (T1, T3) -> Doar B comută 1->0, forțând decizia 1->0."),
        ("T4: (1, 1, 1, 0) -> Decision = False", "Pereche Independență C: (T1, T4) -> Doar C comută 0->1, forțând decizia 1->0."),
        ("T5: (1, 1, 1, 1) -> Decision = True", "Pereche Independență D: (T4, T5) -> Doar D comută 0->1, forțând decizia 0->1.")
    ]
    for p_name, p_desc in pairs:
        p = tf7b.add_paragraph(); p.text = f"{p_name}\n   {p_desc}"; p.font.size = Pt(10); p.font.color.rgb = TEXT_LIGHT

    p = tf7b.add_paragraph()
    p.text = "\nImplementare: tests/test_mcdc.py — 5/5 teste trecute cu succes."
    p.font.size = Pt(10.5); p.font.bold = True; p.font.color.rgb = STATUS_GREEN

    # ==========================================
    # SLIDE 8: CERINȚA 5 (MUTANT ECHIVALENT ORD 1)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_background(s8)
    add_header(s8, "Cerința 5: Mutant de Ordinul 1 Echivalent", "Mutation Testing", "Natalia Moroz (10%)", 8)

    add_card(s8, 0.8, 1.4, 5.7, 5.2)
    tb8a = s8.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf8a = tb8a.text_frame; tf8a.word_wrap = True
    p = tf8a.paragraphs[0]
    p.text = "🧬 Mutația de Ordinul 1 Aplicată"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    mut_intro = [
        "Un mutant este de ordinul 1 dacă este generat prin modificarea unei singure instrucțiuni.",
        "Un mutant este ECHIVALENT dacă produce ieșiri identice cu programul original pe întregul spațiu de intrare.",
        "Mutația aplicată pe intervalul orelor de vârf:",
        "  Original: is_peak_hours = (8 <= entry_hour <= 17)",
        "  Mutat:    is_peak_hours = (7 < entry_hour < 18)",
        "Operator utilizat: ROR (Relational Operator Replacement) combinat cu ajustarea constantelor de frontieră."
    ]
    for it in mut_intro:
        p = tf8a.add_paragraph(); p.text = f"• {it}"; p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    add_card(s8, 6.8, 1.4, 5.7, 5.2)
    tb8b = s8.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf8b = tb8b.text_frame; tf8b.word_wrap = True
    p = tf8b.paragraphs[0]
    p.text = "📐 Demonstrație Matematică & Validare"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    mut_proof = [
        "Parametrul entry_hour este garantat număr întreg (h in Z).",
        "Pe mulțimea numerelor întregi, avem echivalențele:",
        "    h >= 8  <===>  h > 7",
        "    h <= 17 <===>  h < 18",
        "Prin urmare, conjuncția logică:",
        "    (8 <= h <= 17) <===> (7 < h < 18) este o tautologie pe Z.",
        "Comportamentul extern al funcției este strict identic pentru orice tuplu de intrare posibil.",
        "Consecință: Niciun test unitar nu poate omorî acest mutant (este imposibil de ucis).",
        "Validare Empirică: tests/test_equivalent_mutant.py a rulat produsul cartezian pe toate cele 24 de ore și toate rolurile (24 teste exhaustivi) -> 100% identitate."
    ]
    for pr in mut_proof:
        p = tf8b.add_paragraph(); p.text = f"• {pr}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 9: CERINȚA 6 (MUTANȚI NE-ECHIVALENȚI)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    set_background(s9)
    add_header(s9, "Cerința 6: Mutanți Ne-Echivalenți (Omorât vs. Neomorât)", "Mutation Testing", "Victor Mura (15%)", 9)

    add_card(s9, 0.8, 1.4, 11.7, 1.5, fill_color=CARD_NAVY, border_color=TEAL_ACCENT)
    tb9_top = s9.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(11.3), Inches(1.4))
    tf9_top = tb9_top.text_frame; tf9_top.word_wrap = True
    p = tf9_top.paragraphs[0]
    p.text = "🎯 Cazul de Testare Ales: test_bva_occupied_exactly_at_quota"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = MINT_LIGHT
    p = tf9_top.add_paragraph()
    p.text = "Intrări: quota = 10, occupied = 10 (la cotă), hour = 12 (peak), tier = REGULAR, EV = False, allows_overflow = False\nRezultat Așteptat pe Programul Original: AccessDecision.DENIED_QUOTA_EXCEEDED"
    p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    add_card(s9, 0.8, 3.1, 5.7, 3.5, fill_color=CARD_DARK)
    tb9a = s9.shapes.add_textbox(Inches(1.0), Inches(3.2), Inches(5.3), Inches(3.3))
    tf9a = tb9a.text_frame; tf9a.word_wrap = True
    p = tf9a.paragraphs[0]
    p.text = "💥 Mutantul #1: OMORÂT (Killed)"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = STATUS_GREEN
    killed_points = [
        "Mutație ROR: is_within_quota = (occupied <= quota)",
        "Efect la test: Pentru o = 10, q = 10, expresia 10 <= 10 devine True (în loc de False).",
        "Rezultat Mutant: Returnează GRANTED_REGULAR.",
        "Comportament Test: Aserțiunea eșuează imediat: AssertionError: GRANTED_REGULAR != DENIED_QUOTA_EXCEEDED.",
        "Stare: Mutantul este DETECTAT și OMORÂT."
    ]
    for kp in killed_points:
        p = tf9a.add_paragraph(); p.text = f"• {kp}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    add_card(s9, 6.8, 3.1, 5.7, 3.5, fill_color=CARD_DARK)
    tb9b = s9.shapes.add_textbox(Inches(7.0), Inches(3.2), Inches(5.3), Inches(3.3))
    tf9b = tb9b.text_frame; tf9b.word_wrap = True
    p = tf9b.paragraphs[0]
    p.text = "🛡️ Mutantul #2: SUPRAVIEȚUIT (Survived)"
    p.font.size = Pt(14); p.font.bold = True; p.font.color.rgb = STATUS_AMBER
    surv_points = [
        "Mutație Constantă: Prag overflow redus de la 5 la 4 (overflow_count < 4).",
        "Este ne-echivalent? Da, pentru overflow activ la ora 12 cu diferență 4 produce ieșiri diferite.",
        "De ce supraviețuiește la acest test? În testul ales, company_allows_overflow = False.",
        "Expresia se scurtcircuitează (short-circuit) pe primul termen (False and ...). Subexpresia mutată nu este niciodată evaluată!",
        "Rezultat Mutant: Returnează DENIED_QUOTA_EXCEEDED. Testul trece -> Mutantul SUPRAVIEȚUIEȘTE."
    ]
    for sp in surv_points:
        p = tf9b.add_paragraph(); p.text = f"• {sp}"; p.font.size = Pt(10); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 10: CERINȚA 7 (MUTATION TOOLS)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    set_background(s10)
    add_header(s10, "Cerința 7: Mutații Automate cu Două Unelte (mutmut & cosmic-ray)", "Mutation Testing", "Natalia Moroz (10%)", 10)

    add_card(s10, 0.8, 1.4, 5.7, 5.2)
    tb10a = s10.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf10a = tb10a.text_frame; tf10a.word_wrap = True
    p = tf10a.paragraphs[0]
    p.text = "📊 Rezultate Experimentale Comparate"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    exp_items = [
        "Tool 1: mutmut v2.4.4",
        "  • 40 mutanți generați în total",
        "  • 30 mutanți omorâți (Killed)",
        "  • 10 mutanți supraviețuiți (Survived)",
        "  • Scors Brut: 75.0% | Scors pe logica internă: 100%",
        "",
        "Tool 2: cosmic-ray v8.7.0",
        "  • 28 mutanți generați pe AST-ul de decizii",
        "  • 24 mutanți omorâți",
        "  • 4 mutanți supraviețuiți",
        "  • Scors Brut: 85.7% | Scors Ajustat: 96.0%",
        "",
        "Eficacitate suite:",
        "  • Pct 1 (EP+BVA+CEG): omoară mutanții de flux și limite.",
        "  • Pct 4 (MC/DC): omoară 100% mutanții pe decizia compusă EV."
    ]
    for ei in exp_items:
        p = tf10a.add_paragraph(); p.text = f"{ei}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    add_card(s10, 6.8, 1.4, 5.7, 5.2)
    tb10b = s10.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf10b = tb10b.text_frame; tf10b.word_wrap = True
    p = tf10b.paragraphs[0]
    p.text = "🔍 Analiza Diferențelor de Operatori"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    op_diffs = [
        "De ce diferă numărul de mutanți (40 vs. 28)?",
        "1. mutmut mută literali și declarații de clasă: înlocuiește membrii enum cu None (REGULAR = None) și mută textul din ValueError('Parametri...').",
        "2. cosmic-ray operează strict pe nodurile AST de calcul și logică: ReplaceComparisonOperator (Lt_Eq, Lt_LtE), ReplaceAndWithOr, NumberReplacer.",
        "",
        "De ce au supraviețuit 10 mutanți la mutmut?",
        "• Mutanții 1-9 (Enum declarations): Enum-urile sunt rezolvate la import; membrii nefolosiți într-un test specific nu produc erori.",
        "• Mutantul 19 (Mesaj excepție): Testele folosesc pytest.raises(ValueError), verificând clasa excepției, nu șirul exact de caractere.",
        "• Pe logica funcției evaluate_parking_access: Toți cei 30 de mutanți de cod au fost omorâți (100%)."
    ]
    for od in op_diffs:
        p = tf10b.add_paragraph(); p.text = f"{od}"; p.font.size = Pt(10.5); p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 11: ASUMARE AI & CONCLUZII
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    set_background(s11)
    add_header(s11, "Asumarea Utilizării AI & Concluzii Finale", "Concluzii & Audit", "Echipa (Victor & Natalia)", 11)

    add_card(s11, 0.8, 1.4, 5.7, 5.2)
    tb11a = s11.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf11a = tb11a.text_frame; tf11a.word_wrap = True
    p = tf11a.paragraphs[0]
    p.text = "🤖 Conformitate Ghid: Utilizare Asistență AI"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    ai_points = [
        "Conform cerinței din fișa de laborator, utilizarea asistenței AI este documentată transparent în AI_USAGE_LAB.md.",
        "Instrument utilizat: Antigravity (Gemini 3.8 Flash High) pentru asistență la structurarea codului boilerplate și a tabelelor Markdown.",
        "Human Ownership & Validare Umană:",
        "  • Toate cazurile de testare au fost calibrate matematic de echipă pentru a satisface cerințele teoretice (V(G)=7, perechi MC/DC).",
        "  • Echipa a validat manual demonstrația de echivalență a mutantului de ordinul 1 pe numere întregi.",
        "  • Toate rezultatele de acoperire și mutații au fost rulate și verificate empiric în terminal."
    ]
    for ap in ai_points:
        p = tf11a.add_paragraph(); p.text = f"• {ap}"; p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    add_card(s11, 6.8, 1.4, 5.7, 5.2)
    tb11b = s11.shapes.add_textbox(Inches(7.0), Inches(1.5), Inches(5.3), Inches(5.0))
    tf11b = tb11b.text_frame; tf11b.word_wrap = True
    p = tf11b.paragraphs[0]
    p.text = "🏆 Concluzii & Livrabile Proiect"
    p.font.size = Pt(15); p.font.bold = True; p.font.color.rgb = MINT_LIGHT

    deliv_points = [
        "78 de teste unitare automate rulate și trecute (100% success rate).",
        "Acoperire completă a tuturor cerințelor 1-7 din ghidul de laborator.",
        "Repartizare echitabilă și clară: Victor Mura 50% | Natalia Moroz 50%.",
        "Repository Git dedicat pe GitHub sincronizat via HTTPS cu istoricul separat pe fiecare autor: https://github.com/victormura/tss",
        "Documentație completă cu rapoarte separate pentru fiecare cerință în directorul proiect_laborator/docs/.",
        "",
        "Vă mulțumim pentru atenție!  •  Întrebări & Răspunsuri (Q&A)"
    ]
    for dp in deliv_points:
        p = tf11b.add_paragraph(); p.text = f"• {dp}"; p.font.size = Pt(11); p.font.color.rgb = TEXT_LIGHT

    # Salvare PPTX
    out_pptx = "proiect_laborator/docs/Prezentare_Laborator_TSS.pptx"
    prs.save(out_pptx)
    print(f"Prezentare PPTX generată cu succes: {out_pptx}")


if __name__ == "__main__":
    build_deck()
