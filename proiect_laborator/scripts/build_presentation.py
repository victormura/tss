"""
Generator prezentare — Proiect de laborator TSS (Smart Parking Gate)
Echipa: Natalia Moroz (50%) & Victor Mura (50%)

Rulare:
    python3 proiect_laborator/scripts/build_presentation.py
Produce:
    proiect_laborator/docs/Prezentare_Laborator_TSS.pptx  (24 slide-uri)
"""

import json
import os
import sys

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_data as D  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT_PPTX = os.path.join(ROOT, "docs", "Prezentare_Laborator_TSS.pptx")
CEG_PNG = os.path.join(ROOT, "docs", "img", "ceg_graph.png")
MUTATION_JSON = os.path.join(ROOT, "mutation_results", "summary.json")


# ---------------------------------------------------------------- design tokens
def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


INK = rgb("0F1B2D")
INK_2 = rgb("3B4A5E")
MUTED = rgb("6B7A8F")
LINE = rgb("DCE2EA")
PANEL = rgb("F3F5F8")
WHITE = rgb("FFFFFF")
NATALIA = rgb("5B4FD6")      # indigo -> Cerințele 1, 2, 5
NATALIA_L = rgb("ECEAFB")
VICTOR = rgb("0E8C7F")       # teal   -> Cerințele 3, 4, 6, 7
VICTOR_L = rgb("E3F4F1")
TEAM = rgb("0F1B2D")
GREEN = rgb("1F9D57")
GREEN_L = rgb("E4F5EA")
RED = rgb("D64545")
RED_L = rgb("FBE7E7")
AMBER = rgb("D98A0B")
AMBER_L = rgb("FDF1DC")
CODE_BG = rgb("111827")
CODE_FG = rgb("E5E7EB")
CODE_DIM = rgb("8B95A5")

COLOR_MAP = {"green": (GREEN, GREEN_L), "red": (RED, RED_L), "amber": (AMBER, AMBER_L)}

FONT = "Helvetica Neue"
MONO = "Menlo"

W, H = 13.333, 7.5
TOTAL = 24

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- primitives
def box(slide, x, y, w, h, fill=None, line=None, line_w=1.0, shape=MSO_SHAPE.RECTANGLE, radius=None, dash=False):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(line_w)
        if dash:
            s.line.dash_style = 4
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def text(slide, x, y, w, h, content, size=14, color=INK, bold=False, font=FONT,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0)
    tf.margin_top = tf.margin_bottom = Inches(0)
    tf.vertical_anchor = anchor
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
        runs = para if isinstance(para, list) else [para]
        for r in runs:
            spec = r if isinstance(r, dict) else {"t": r}
            run = p.add_run()
            run.text = spec["t"]
            f = run.font
            f.name = spec.get("font", font)
            f.size = Pt(spec.get("size", size))
            f.bold = spec.get("bold", bold)
            f.italic = spec.get("italic", italic)
            f.color.rgb = spec.get("color", color)
    return tb


def shape_text(s, content, size=12, color=INK, bold=False, align=PP_ALIGN.CENTER,
               anchor=MSO_ANCHOR.MIDDLE, font=FONT, margin=0.06):
    tf = s.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = anchor
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        runs = para if isinstance(para, list) else [para]
        for r in runs:
            spec = r if isinstance(r, dict) else {"t": r}
            run = p.add_run()
            run.text = spec["t"]
            run.font.name = spec.get("font", font)
            run.font.size = Pt(spec.get("size", size))
            run.font.bold = spec.get("bold", bold)
            run.font.color.rgb = spec.get("color", color)
    return s


def arrow(slide, x1, y1, x2, y2, color=MUTED, width=1.25, head=True, dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    if dash:
        c.line.dash_style = 4
    if head:
        ln = c.line._get_or_add_ln()
        tail = etree.SubElement(ln, qn("a:tailEnd"))
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
    return c


def pill(slide, x, y, w, h, label, fill, color=WHITE, size=10, bold=True):
    s = box(slide, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    shape_text(s, label, size=size, color=color, bold=bold, margin=0.04)
    return s


def card(slide, x, y, w, h, fill=PANEL, line=None, accent=None):
    s = box(slide, x, y, w, h, fill=fill, line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    if accent is not None:
        box(slide, x, y + 0.14, 0.06, h - 0.28, fill=accent)
    return s


def table(slide, x, y, w, rows, col_w, row_h=0.32, head_fill=INK, head_color=WHITE,
          size=10.0, head_size=10.0, zebra=PANEL, fills=None, colors=None, bolds=None,
          aligns=None, font=FONT, fonts=None):
    nrows, ncols = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nrows, ncols, Inches(x), Inches(y), Inches(w), Inches(row_h * nrows))
    tbl = gt.table
    tblPr = gt._element.graphic.graphicData.tbl.tblPr
    tblPr.set("bandRow", "0")
    tblPr.set("firstRow", "0")
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i in range(nrows):
        tbl.rows[i].height = Inches(row_h)
        for j in range(ncols):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if i == 0:
                fill = head_fill
            elif fills and fills.get((i, j)) is not None:
                fill = fills[(i, j)]
            elif fills and fills.get((i, None)) is not None:
                fill = fills[(i, None)]
            else:
                fill = zebra if (i % 2 == 0 and zebra is not None) else WHITE
            cell.fill.solid()
            cell.fill.fore_color.rgb = fill
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = ""
            run = p.add_run()
            run.text = str(rows[i][j])
            run.font.name = (fonts or {}).get(j, font) if i > 0 else FONT
            run.font.size = Pt(head_size if i == 0 else size)
            run.font.bold = True if i == 0 else bool(bolds and bolds.get((i, j)))
            if i == 0:
                run.font.color.rgb = head_color
            elif colors and colors.get((i, j)) is not None:
                run.font.color.rgb = colors[(i, j)]
            else:
                run.font.color.rgb = INK
            if aligns and j in aligns:
                p.alignment = aligns[j]
    return tbl


def code_block(slide, x, y, w, h, lines, size=10.0, line_h=None):
    card_s = box(slide, x, y, w, h, fill=CODE_BG, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
    pad = 0.16
    lh = line_h or (size * 1.42 / 72)
    for i, (ln, style) in enumerate(lines):
        ly = y + pad + i * lh
        color = CODE_FG
        if style == "dim":
            color = CODE_DIM
        if style in ("add", "del", "hl"):
            band = {"add": rgb("12442E"), "del": rgb("4A1D24"), "hl": rgb("23314A")}[style]
            box(slide, x + 0.06, ly - 0.01, w - 0.12, lh, fill=band)
            color = {"add": rgb("7EE2A8"), "del": rgb("FF9AA2"), "hl": rgb("FFFFFF")}[style]
        text(slide, x + pad, ly, w - 2 * pad, lh, ln, size=size, color=color, font=MONO)
    return card_s


# ---------------------------------------------------------------- slide chrome
def owner_meta(owner):
    return {
        "natalia": ("Natalia Moroz", NATALIA, NATALIA_L),
        "victor": ("Victor Mura", VICTOR, VICTOR_L),
        "team": ("Echipa", TEAM, PANEL),
    }[owner]


def header(slide, n, section, title, owner, req=None):
    name, color, light = owner_meta(owner)
    box(slide, 0, 0, W, H, fill=WHITE)
    box(slide, 0, 0, W, 0.09, fill=color)
    label = section.upper() if req is None else f"CERINȚA {req}  ·  {section.upper()}"
    text(slide, 0.7, 0.38, 8.8, 0.28, label, size=10, color=color, bold=True)
    text(slide, 0.7, 0.64, 10.2, 0.55, title, size=23, color=INK, bold=True)
    pill(slide, W - 0.7 - 2.1, 0.42, 2.1, 0.34, name, fill=light, color=color, size=10.5)
    box(slide, 0.7, 7.02, W - 1.4, 0.01, fill=LINE)
    text(slide, 0.7, 7.09, 8, 0.25, "TSS · Proiect de laborator · Smart Parking Gate", size=9, color=MUTED)
    text(slide, W - 1.7, 7.09, 1.0, 0.25, f"{n:02d} / {TOTAL}", size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def new_slide(n, section, title, owner, req=None):
    s = prs.slides.add_slide(BLANK)
    header(s, n, section, title, owner, req)
    return s


def divider(n, part, title, owner, items):
    _, color, _ = owner_meta(owner)
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, W, H, fill=INK)
    box(s, 0, 0, 0.35, H, fill=color)
    text(s, 1.2, 1.95, 8, 0.4, part.upper(), size=14, color=color if owner != "team" else rgb("9FB3C8"), bold=True)
    text(s, 1.2, 2.4, 10.5, 1.1, title, size=38, color=WHITE, bold=True)
    for i, (req, label, who) in enumerate(items):
        yy = 3.95 + i * 0.56
        _, c, _ = owner_meta(who)
        pill(s, 1.2, yy, 1.35, 0.36, f"Cerința {req}", fill=c, size=10.5)
        text(s, 2.75, yy + 0.04, 8.8, 0.36, label, size=14.5, color=rgb("DCE4EB"))
    text(s, W - 1.7, 7.09, 1.0, 0.25, f"{n:02d} / {TOTAL}", size=9, color=rgb("6B7A8F"), align=PP_ALIGN.RIGHT)
    return s


with open(MUTATION_JSON) as fh:
    MUT = json.load(fh)

# ============================================================== 01 · TITLE
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, W, H, fill=INK)
box(s, 0, 0, W, 0.09, fill=NATALIA)
box(s, W / 2, 0, W / 2, 0.09, fill=VICTOR)
text(s, 0.9, 1.0, 9, 0.35, "TESTAREA SISTEMELOR SOFTWARE  ·  PROIECT DE LABORATOR", size=12, color=rgb("9FB3C8"), bold=True)
text(s, 0.9, 1.5, 8.5, 1.0, "Smart Parking Gate", size=54, color=WHITE, bold=True)
text(s, 0.9, 2.55, 7.6, 1.0,
     "Testare funcțională, structurală și prin mutații pentru motorul de decizie al unei parcări corporate multi-tenant",
     size=17, color=rgb("C9D4E0"))

stats = [("81", "teste unitare rulate automat"), ("V(G) = 7", "complexitate ciclomatică"),
         ("5", "teste MC/DC (N + 1)"), ("100%", "scor de mutație ajustat")]
for i, (big, small) in enumerate(stats):
    yy = 1.05 + i * 1.02
    box(s, 9.55, yy, 0.05, 0.78, fill=NATALIA if i % 2 == 0 else VICTOR)
    text(s, 9.8, yy - 0.04, 3, 0.55, big, size=28, color=WHITE, bold=True)
    text(s, 9.8, yy + 0.48, 3, 0.3, small, size=11, color=rgb("9FB3C8"))

for i, (name, reqs, color) in enumerate([
        ("Natalia Moroz", "Cerințele 1, 2, 5  ·  EP, BVA, Graf cauză-efect, acoperire de cod, mutant echivalent", NATALIA),
        ("Victor Mura", "Cerințele 3, 4, 6, 7  ·  CFG, căi independente, MC/DC, mutanți ne-echivalenți, mutmut & cosmic-ray", VICTOR)]):
    xx = 0.9 + i * 4.35
    box(s, xx, 4.7, 4.15, 1.28, fill=rgb("18263B"), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    box(s, xx, 4.7, 0.07, 1.28, fill=color)
    text(s, xx + 0.28, 4.84, 3.6, 0.35, name, size=17, color=WHITE, bold=True)
    text(s, xx + 0.28, 5.24, 3.7, 0.65, reqs, size=10.5, color=rgb("C9D4E0"))
    pill(s, xx + 3.1, 4.86, 0.85, 0.3, "50%", fill=color, size=10)
text(s, 0.9, 6.75, 11, 0.3,
     "Universitatea din București  ·  FMI  ·  Master Ingineria Sistemelor Software, anul II  ·  2026",
     size=10.5, color=rgb("6B7A8F"))

# ============================================================== 02 · AGENDA
s = new_slide(2, "Structura proiectului", "Cele 7 cerințe și împărțirea responsabilităților", "team")
agenda = [
    ("1", "Testare funcțională", "EP (15 teste) · BVA (25) · CEG (9)", "natalia"),
    ("2", "Acoperire de cod", "Instrucțiuni vs. ramuri pe fiecare set", "natalia"),
    ("3", "Graf de control", "CFG · V(G) = 7 · 7 căi independente", "victor"),
    ("4", "Criteriul MC/DC", "Decizia compusă EV · 5 teste", "victor"),
    ("5", "Mutant echivalent", "Ordin 1 · demonstrație pe ℤ", "natalia"),
    ("6", "Mutanți ne-echivalenți", "Unul omorât, unul supraviețuitor", "victor"),
    ("7", "Unelte de mutație", "mutmut (40) vs. cosmic-ray (101)", "victor"),
]
cw, ch, gx, gy = 2.82, 2.02, 0.21, 0.26
for i, (num, title_, sub, who) in enumerate(agenda):
    row, col = divmod(i, 4)
    xx = 0.7 + col * (cw + gx) + (0 if row == 0 else (cw + gx) / 2)
    yy = 1.55 + row * (ch + gy)
    _, c, _ = owner_meta(who)
    card(s, xx, yy, cw, ch, fill=WHITE, line=LINE)
    box(s, xx, yy, cw, 0.08, fill=c)
    text(s, xx + 0.25, yy + 0.28, 1.2, 0.6, f"0{num}", size=30, color=c, bold=True)
    text(s, xx + 0.25, yy + 0.96, cw - 0.4, 0.38, title_, size=15, color=INK, bold=True)
    text(s, xx + 0.25, yy + 1.34, cw - 0.4, 0.5, sub, size=11, color=MUTED)
for i, (who, lbl) in enumerate([("natalia", "Natalia Moroz — 50% (Cerințele 1, 2, 5)"),
                                 ("victor", "Victor Mura — 50% (Cerințele 3, 4, 6, 7)")]):
    _, c, _ = owner_meta(who)
    box(s, 0.7 + i * 4.2, 6.48, 0.22, 0.22, fill=c, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    text(s, 1.02 + i * 4.2, 6.48, 3.8, 0.25, lbl, size=11, color=INK_2, bold=True)

# ============================================================== 03 · SYSTEM UNDER TEST
s = new_slide(3, "Sistemul testat", "Bariera unui campus de birouri cu mai mulți chiriași", "team")
text(s, 0.7, 1.5, 4.6, 0.3, "SPECIFICAȚIA PROBLEMEI", size=10.5, color=MUTED, bold=True)
bul = [
    [{"t": "Parcare partajată multi-tenant: ", "bold": True},
     "fiecare companie chiriașă are o cotă alocată q ≥ 1 de locuri gratuite și un număr curent o ≥ 0 de locuri ocupate."],
    [{"t": "Programul de vârf: ", "bold": True},
     "intervalul orar 08:00–17:59 (8 ≤ h ≤ 17); în afara lui (0..7 și 18..23) parcarea este în regim off-peak."],
    [{"t": "Trei roluri (tier): ", "bold": True},
     "VIP (acces garantat oricând), CONTRACTOR (interzis în afara orelor 8..17), REGULAR (acces conform cotei)."],
    [{"t": "Stații EV și overflow: ", "bold": True},
     "vehiculele electrice primesc stație dacă există loc liber și (e off-peak sau firma e sub cotă); peste cotă, "
     "accesul cu plată e permis dacă firma are overflow activ și (e off-peak sau depășirea o − q < 5)."],
]
for i, b in enumerate(bul):
    yy = 1.9 + i * 1.15
    box(s, 0.7, yy + 0.08, 0.1, 0.1, fill=INK, shape=MSO_SHAPE.OVAL)
    text(s, 0.95, yy, 4.5, 1.05, [b], size=12, color=INK_2)

text(s, 5.85, 1.5, 6.8, 0.3, "IERARHIA DECIZIILOR — evaluate_parking_access()", size=10.5, color=MUTED, bold=True)
pipeline = [
    ("Pas 0", "q ≤ 0 ∨ o < 0 ∨ h < 0 ∨ h > 23 ?", "I7: ValueError", RED, RED_L),
    ("Pas 1", "tier == VIP ?", "I1: GRANTED_VIP", GREEN, GREEN_L),
    ("Pas 2", "tier == CONTRACTOR ∧ ¬(8 ≤ h ≤ 17) ?", "I2: DENIED_RESTRICTED_HOURS", RED, RED_L),
    ("Pas 3", "is_ev ∧ has_spot ∧ (¬peak ∨ o < q) ?", "I3: GRANTED_EV_CHARGING", GREEN, GREEN_L),
    ("Pas 4", "o < q ?", "I4: GRANTED_REGULAR", GREEN, GREEN_L),
    ("Pas 5", "allows_overflow ∧ (¬peak ∨ o − q < 5) ?", "I5: GRANTED_PAID_OVERFLOW", AMBER, AMBER_L),
    ("Pas 6", "Altfel", "I6: DENIED_QUOTA_EXCEEDED", RED, RED_L),
]
for i, (rid, q, out, c, light) in enumerate(pipeline):
    yy = 1.9 + i * 0.68
    box(s, 5.85, yy, 3.85, 0.5, fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
    pill(s, 5.95, yy + 0.1, 0.65, 0.3, rid, fill=INK, size=9)
    text(s, 6.7, yy + 0.04, 2.95, 0.42, q, size=10.2, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    if i < len(pipeline) - 1:
        arrow(s, 6.27, yy + 0.5, 6.27, yy + 0.68, color=LINE, width=1.5)
    arrow(s, 9.7, yy + 0.25, 10.02, yy + 0.25, color=c, width=1.5)
    ob = box(s, 10.05, yy + 0.05, 2.6, 0.4, fill=light, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    shape_text(ob, out, size=9, color=c, bold=True, font=MONO)

# ============================================================== 04 · CODE + INPUTS
s = new_slide(4, "Sistemul testat", "Funcția sub test, parametrii de intrare și ieșirile I1…I7", "team")
code = [
    ("def evaluate_parking_access(company_allocated_quota, company_current_occupied,", None),
    ("        entry_hour, tier, is_electric_vehicle, has_ev_spots_available, company_allows_overflow):", None),
    ("    if (company_allocated_quota <= 0 or company_current_occupied < 0", None),
    ("            or entry_hour < 0 or entry_hour > 23):", None),
    ("        raise ValueError('Parametri de intrare în afara domeniilor valide admise.')", "dim"),
    ("    is_peak_hours = (8 <= entry_hour <= 17)", None),
    ("    if tier == EmployeeTier.VIP:", None),
    ("        return AccessDecision.GRANTED_VIP", "dim"),
    ("    if tier == EmployeeTier.CONTRACTOR and not is_peak_hours:", None),
    ("        return AccessDecision.DENIED_RESTRICTED_HOURS", "dim"),
    ("    is_within_quota = company_current_occupied < company_allocated_quota", None),
    ("    if is_electric_vehicle and has_ev_spots_available and (not is_peak_hours or is_within_quota):", "hl"),
    ("        return AccessDecision.GRANTED_EV_CHARGING", "dim"),
    ("    if is_within_quota:", None),
    ("        return AccessDecision.GRANTED_REGULAR", "dim"),
    ("    overflow_count = company_current_occupied - company_allocated_quota", None),
    ("    if company_allows_overflow and (not is_peak_hours or overflow_count < 5):", None),
    ("        return AccessDecision.GRANTED_PAID_OVERFLOW", "dim"),
    ("    return AccessDecision.DENIED_QUOTA_EXCEEDED", "dim"),
]
code_block(s, 0.7, 1.48, 6.95, 5.3, code, size=9.2, line_h=0.26)
rows = [["Parametru", "Tip", "Domeniu valid"],
        ["company_allocated_quota (q)", "int", "q ≥ 1"],
        ["company_current_occupied (o)", "int", "o ≥ 0"],
        ["entry_hour (h)", "int", "0 ≤ h ≤ 23  (vârf: 8..17)"],
        ["tier (t)", "Enum", "VIP · REGULAR · CONTRACTOR"],
        ["is_electric_vehicle (ev)", "bool", "True / False"],
        ["has_ev_spots_available (spot)", "bool", "True / False"],
        ["company_allows_overflow (ovf)", "bool", "True / False"]]
table(s, 7.85, 1.48, 4.8, rows, [2.45, 0.55, 1.8], row_h=0.38, size=9.5, fonts={0: MONO})
card(s, 7.85, 4.72, 4.8, 2.06, fill=PANEL)
text(s, 8.05, 4.82, 4.4, 0.28, "CLASELE DE IEȘIRE (I1 … I7)", size=10.5, color=MUTED, bold=True)
for idx, (oid, name, cname) in enumerate(D.OUTPUTS):
    fg, bg = COLOR_MAP[cname]
    r, c = divmod(idx, 2)
    xx = 8.05 + c * 2.25
    yy = 5.15 + r * 0.39
    pill(s, xx, yy, 2.15, 0.32, f"{oid}: {name}", fill=bg, color=fg, size=8.0, bold=True)

# ============================================================== 05 · DIVIDER I
divider(5, "Partea I · Natalia Moroz", "Testare funcțională și acoperire de cod", "natalia",
        [("1a", "Partiționarea în clase de echivalență: clase de intrare, ieșire și clase finale", "natalia"),
         ("1b", "Analiza valorilor de frontieră: toate cele 25 de cazuri testate", "natalia"),
         ("1c", "Graful cauză-efect și construcția pas cu pas a tabelului de decizie", "natalia"),
         ("2", "Acoperirea la nivel de instrucțiune și de ramură pe fiecare set", "natalia")])

# ============================================================== 06 · EP (1/2)
s = new_slide(6, "Testare funcțională · EP (1/2)", "Partiționarea în clase de echivalență: intrări și ieșiri", "natalia", req="1a")
text(s, 0.7, 1.42, 7.8, 0.28, "CLASELE DE INTRARE (VALIDE ȘI INVALIDE)", size=10.5, color=MUTED, bold=True)
rows = [["Parametru de intrare", "Clase valide", "Clase invalide"]]
for param, val_c, inv_c in D.INPUT_CLASSES:
    v_str = "   ·   ".join(f"{k}: {cond}" for k, cond in val_c)
    i_str = "   ·   ".join(f"{k}: {cond}" for k, cond in inv_c) if inv_c else "—"
    rows.append([param, v_str, i_str])
fills = {(i, 2): RED_L for i in range(1, 4)}
colors = {(i, 2): RED for i in range(1, 4)}
table(s, 0.7, 1.72, 7.95, rows, [2.05, 3.85, 2.05], row_h=0.58, size=10.5,
      fills=fills, colors=colors, bolds={(i, 0): True for i in range(1, 7)}, fonts={0: MONO})

text(s, 8.9, 1.42, 3.75, 0.28, "CLASELE DE IEȘIRE (I1 … I7)", size=10.5, color=MUTED, bold=True)
out_rows = [["Clasă", "Valoare returnată / excepție"]]
out_colors, out_fills, out_bolds = {}, {}, {}
for idx, (oid, name, cname) in enumerate(D.OUTPUTS, start=1):
    fg, bg = COLOR_MAP[cname]
    out_rows.append([oid, name])
    out_colors[(idx, 0)] = fg
    out_colors[(idx, 1)] = fg
    out_fills[(idx, 0)] = bg
    out_bolds[(idx, 0)] = True
    out_bolds[(idx, 1)] = True
table(s, 8.9, 1.72, 3.75, out_rows, [0.75, 3.0], row_h=0.44, size=9.5,
      fills=out_fills, colors=out_colors, bolds=out_bolds, fonts={1: MONO},
      aligns={0: PP_ALIGN.CENTER})

card(s, 8.9, 5.4, 3.75, 1.38, fill=NATALIA_L)
text(s, 9.1, 5.5, 3.4, 1.2,
     [[{"t": "Cum se obțin clasele finale:", "bold": True, "size": 11, "color": NATALIA}],
      "Fiecare clasă de echivalență finală ECk asociază o combinație de clase de intrare cu o clasă de ieșire Ik.",
      "Pentru clasele invalide se modifică câte un singur parametru odată, restul fiind fixați pe valori valide."],
     size=9.8, color=INK_2, spacing=3)

text(s, 0.7, 6.02, 7.95, 0.75,
     [[{"t": "Observație pentru perechea (is_ev, has_spot): ", "bold": True, "color": NATALIA},
       "când is_ev = False, valoarea lui has_spot nu poate schimba ramura parcursă (conjuncția is_ev and has_spot "
       "este deja False), deci (False, True) și (False, False) formează o singură clasă V3 = (F, –)."]],
     size=10.5, color=INK_2)

# ============================================================== 07 · EP (2/2) FINAL CLASSES + TEST VALUES
s = new_slide(7, "Testare funcțională · EP (2/2)",
              "Clasele de echivalență finale și valorile testate (tests/test_ep.py)", "natalia", req="1a")
rows = [["Clasă finală", "Combinație clase de intrare", "Clasă ieșire",
         "Valoare testată (q, o, h, tier, ev, spot, ovf)", "Rezultat obținut"]]
fills, colors, bolds = {}, {}, {}
r_i = 0
for ec_id, in_cls, cases in D.EP_FINAL:
    for case in cases:
        r_i += 1
        res = D.run(case)
        oid = D.OUT_ID[res]
        fg, bg = COLOR_MAP[D.OUT_COLOR[oid]]
        in_desc = f"{in_cls}  (restul valide)" if len(in_cls) <= 2 else in_cls.replace(" ", ", ")
        rows.append([ec_id, in_desc, oid, D.fmt_case(case), res])
        bolds[(r_i, 0)] = True
        bolds[(r_i, 2)] = True
        bolds[(r_i, 4)] = True
        colors[(r_i, 0)] = NATALIA
        colors[(r_i, 2)] = fg
        colors[(r_i, 4)] = fg
        fills[(r_i, 2)] = bg

table(s, 0.7, 1.42, 11.95, rows, [1.05, 2.75, 0.95, 4.45, 2.75], row_h=0.34, size=9.2, head_size=9.5,
      fills=fills, colors=colors, bolds=bolds, fonts={3: MONO, 4: MONO},
      aligns={0: PP_ALIGN.CENTER, 2: PP_ALIGN.CENTER})
text(s, 0.7, 6.68, 11.95, 0.28,
     "Total: 13 clase finale (EC1..EC5 invalide → I7; EC6..EC13 valide → I1..I6), 14 apeluri de test + 1 test de integritate Enum = 15 teste în tests/test_ep.py.",
     size=9.5, color=MUTED, italic=True)

# ============================================================== 08 · BVA (1/2) NUMBER LINES
s = new_slide(8, "Testare funcțională · BVA (1/2)",
              "Analiza valorilor de frontieră: limitele domeniilor numerice", "natalia", req="1b")


def number_line(slide, x, y, w, lo, hi, marks, bands, title_):
    text(slide, x, y - 0.62, w, 0.28, title_, size=12, color=INK, bold=True)
    span = hi - lo
    sx = lambda v: x + (v - lo) / span * w
    for (a, b, fill, lbl) in bands:
        box(slide, sx(a), y - 0.09, sx(b) - sx(a), 0.18, fill=fill)
        if lbl:
            text(slide, sx(a), y - 0.32, sx(b) - sx(a), 0.22, lbl, size=8.5, color=MUTED, align=PP_ALIGN.CENTER)
    box(slide, x, y - 0.01, w, 0.02, fill=INK_2)
    for v, kind in marks:
        c = {"bad": RED, "ok": NATALIA, "edge": INK}[kind]
        d = 0.2
        box(slide, sx(v) - d / 2, y - d / 2, d, d, fill=c, shape=MSO_SHAPE.OVAL, line=WHITE, line_w=1.5)
        text(slide, sx(v) - 0.3, y + 0.15, 0.6, 0.24, str(v), size=9.5, color=c, bold=True, align=PP_ALIGN.CENTER)


number_line(s, 0.9, 2.25, 11.5, -2, 25,
            [(-1, "bad"), (0, "edge"), (1, "ok"), (7, "ok"), (8, "edge"), (9, "ok"),
             (16, "ok"), (17, "edge"), (18, "ok"), (22, "ok"), (23, "edge"), (24, "bad")],
            [(-2, -0.5, RED_L, "invalid (h < 0)"), (-0.5, 7.5, PANEL, "off-peak (0..7)"),
             (7.5, 17.5, NATALIA_L, "ore de vârf (8..17)"),
             (17.5, 23.5, PANEL, "off-peak (18..23)"), (23.5, 25, RED_L, "invalid (h > 23)")],
            "1. entry_hour (h) — frontierele [0, 23] (testate cu REGULAR) și [8, 17] (testate cu CONTRACTOR)")

number_line(s, 0.9, 3.95, 5.4, -1, 4,
            [(0, "bad"), (1, "edge"), (2, "ok")],
            [(-1, 0.5, RED_L, "invalid (q ≤ 0)"), (0.5, 4, NATALIA_L, "valid (q ≥ 1)")],
            "2. company_allocated_quota (q ≥ 1) — frontiera q = 1")

number_line(s, 6.9, 3.95, 5.5, -2, 3,
            [(-1, "bad"), (0, "edge"), (1, "ok")],
            [(-2, -0.5, RED_L, "invalid (o < 0)"), (-0.5, 3, NATALIA_L, "valid (o ≥ 0)")],
            "3. company_current_occupied (o ≥ 0) — frontiera o = 0")

number_line(s, 0.9, 5.65, 5.4, 7, 13,
            [(9, "ok"), (10, "edge"), (11, "ok")],
            [(7, 9.5, GREEN_L, "în cotă (o < q)"), (9.5, 13, RED_L, "cotă atinsă (o ≥ q)")],
            "4. occupied raportat la quota = 10 — frontiera o = q")

number_line(s, 6.9, 5.65, 5.5, 12, 18,
            [(14, "ok"), (15, "edge"), (16, "ok")],
            [(12, 14.5, AMBER_L, "overflow < 5 (o = 14)"), (14.5, 18, RED_L, "overflow ≥ 5 (o = 15, 16)")],
            "5. depășirea cotei la vârf (o − q < 5, pentru q = 10) — frontiera o = 15")

text(s, 0.9, 6.45, 11.5, 0.4,
     "Pentru fiecare frontieră se testează tripletele (frontieră − 1, frontieră, frontieră + 1); toate cele 25 de cazuri sunt listate pe slide-ul următor.",
     size=10.5, color=MUTED, italic=True)

# ============================================================== 09 · BVA (2/2) ALL 25 TEST CASES
s = new_slide(9, "Testare funcțională · BVA (2/2)",
              "Toate cele 25 de cazuri BVA testate (tests/test_bva.py)", "natalia", req="1b")

all_bva = []
for grp_name, var_sym, cases in D.BVA_GROUPS:
    for case in cases:
        all_bva.append((grp_name, case, D.run(case)))

left_bva = all_bva[:12]   # primele 4 frontiere (12 teste)
right_bva = all_bva[12:]  # următoarele 5 grupuri (13 teste)


def bva_table(slide, x, y, w, items, start_idx):
    rows = [["#", "Frontieră", "Intrare (q, o, h, tier, ev, sp, ovf)", "Ieșire"]]
    colors, bolds, fills = {}, {}, {}
    for i, (grp, case, res) in enumerate(items, start=1):
        oid = D.OUT_ID[res]
        fg, bg = COLOR_MAP[D.OUT_COLOR[oid]]
        t_num = f"B{start_idx + i - 1:02d}"
        rows.append([t_num, grp, D.fmt_case(case), f"{oid}: {res}"])
        bolds[(i, 0)] = True
        bolds[(i, 3)] = True
        colors[(i, 0)] = NATALIA
        colors[(i, 3)] = fg
        fills[(i, 3)] = bg
    table(slide, x, y, w, rows, [0.48, 1.35, 2.35, 1.67], row_h=0.36, size=8.3, head_size=8.8,
          fills=fills, colors=colors, bolds=bolds, fonts={2: MONO, 3: MONO},
          aligns={0: PP_ALIGN.CENTER})


bva_table(s, 0.7, 1.42, 5.85, left_bva, 1)
bva_table(s, 6.78, 1.42, 5.85, right_bva, 13)
text(s, 0.7, 6.68, 11.95, 0.28,
     "B01..B24 acoperă cele 8 frontiere × 3 valori; B25 (q=4, o=11) este un caz special cu cotă diferită de 10 pentru a verifica formula o − q < 5.",
     size=9.5, color=MUTED, italic=True)

# ============================================================== 10 · CEG GRAPH
s = new_slide(10, "Testare funcțională · CEG (1/4)",
              "Graful cauză-efect (docs/CEG_Drawio.drawio)", "natalia", req="1c")
s.shapes.add_picture(CEG_PNG, Inches(0.55), Inches(1.38), width=Inches(9.15))

card(s, 9.8, 1.42, 2.88, 5.4, fill=PANEL)
text(s, 9.98, 1.54, 2.55, 5.15,
     [[{"t": "Elementele grafului", "bold": True, "size": 11.5, "color": INK}],
      "",
      [{"t": "Noduri intermediare:", "bold": True, "size": 9.8, "color": NATALIA}],
      "• Nodul 1 = ¬C3 ∨ C6",
      "  (off-peak sau în cotă)",
      "• Nodul 2 = ¬C3 ∨ C8",
      "  (off-peak sau depășire < 5)",
      "• Nodul 3 = C7 ∧ nodul 2",
      "  (overflow aprobat)",
      "",
      [{"t": "Constrângere pe cauze:", "bold": True, "size": 9.8, "color": RED}],
      "• E(C1, C2): cel mult una din",
      "  C1 (VIP) și C2 (CONTRACTOR)",
      "  poate fi 1 simultan.",
      "",
      [{"t": "Relații de mascare M:", "bold": True, "size": 9.8, "color": AMBER}],
      "• M(Ef1, Ef3..Ef6): dacă Ef1=1,",
      "  efectele Ef3..Ef6 sunt mascate.",
      "• M(Ef2, Ef3..Ef6): dacă Ef2=1,",
      "  efectele Ef3..Ef6 sunt mascate.",
      "• M(Ef3, Ef4..Ef6): dacă Ef3=1,",
      "  efectele Ef4..Ef6 sunt mascate.",
      "• Ef4, Ef5, Ef6 sunt disjuncte",
      "  prin C6 vs. ¬C6 și nodul 3 vs. ¬3."],
     size=9.0, color=INK_2, spacing=1.5)

# ============================================================== 11 · CEG STEP-BY-STEP (1/2)
s = new_slide(11, "Testare funcțională · CEG (2/4)",
              "Construcția tabelului de decizie pas cu pas: efectele Ef1, Ef2, Ef3", "natalia", req="1c")


def mini_dt(slide, x, y, upto_idx):
    """Afișează tabelul de decizie parțial după adăugarea primelor `upto_idx` reguli."""
    rules = D.CEG_RULES[:upto_idx]
    head = [""] + [r[0] for r in rules]
    rows = [head]
    fills, colors, bolds = {}, {}, {}
    for r_i, (cid, _) in enumerate(D.CAUSES, start=1):
        row = [cid]
        bolds[(r_i, 0)] = True
        for c_i, (_, _, case) in enumerate(rules, start=1):
            v = str(D.causes_of(case)[cid])
            row.append(v)
            if v == "1":
                fills[(r_i, c_i)] = NATALIA_L
                colors[(r_i, c_i)] = NATALIA
                bolds[(r_i, c_i)] = True
        rows.append(row)
    for e_i, (eid, _, _) in enumerate(D.EFFECTS, start=9):
        row = [eid]
        bolds[(e_i, 0)] = True
        colors[(e_i, 0)] = GREEN if eid in ("Ef1", "Ef3", "Ef4") else AMBER if eid == "Ef5" else RED
        for c_i, (_, active_eff, _) in enumerate(rules, start=1):
            v = "1" if active_eff == eid else "0"
            row.append(v)
            if v == "1":
                fills[(e_i, c_i)] = GREEN_L if eid in ("Ef1", "Ef3", "Ef4") else AMBER_L if eid == "Ef5" else RED_L
                colors[(e_i, c_i)] = colors[(e_i, 0)]
                bolds[(e_i, c_i)] = True
            else:
                colors[(e_i, c_i)] = MUTED
        rows.append(row)
    cw = [0.48] + [0.38] * len(rules)
    table(slide, x, y, sum(cw), rows, cw, row_h=0.22, size=8.0, head_size=8.2,
          fills=fills, colors=colors, bolds=bolds,
          aligns={j: PP_ALIGN.CENTER for j in range(len(cw))}, zebra=None)


steps_1 = [
    ("Pasul 1 — Efectul Ef1 = 1 (GRANTED_VIP)", GREEN, 1,
     ["Expresie din graf:  Ef1 = C1 = 1  ⇒  C1 = 1.",
      "Constrângerea E(C1, C2) impune C2 = 0.",
      "Pentru restul cauzelor alegem C3=1, C4=1, C5=1, C6=0, C7=0, C8=1.",
      "Deși condițiile pentru Ef6 (¬C6 ∧ ¬nod3) sunt 1, M(Ef1, Ef6) setează Ef6 = 0.",
      "Se adaugă coloana R1  (nr_coloane = 1)."]),
    ("Pasul 2 — Efectul Ef2 = 1 (DENIED_RESTRICTED_HOURS)", RED, 2,
     ["Expresie:  Ef2 = C2 ∧ ¬C3 = 1  ⇒  C2 = 1 și C3 = 0.",
      "Din E(C1, C2) rezultă C1 = 0. Fixăm C4 = 0, C5 = 0, C6 = 1, C7 = 0, C8 = 1.",
      "Deși C6 = 1 ar activa Ef4, masca M(Ef2, Ef4) setează Ef4 = 0.",
      "Se adaugă coloana R2  (nr_coloane = 2)."]),
    ("Pasul 3 — Efectul Ef3 = 1 (GRANTED_EV_CHARGING)", GREEN, 4,
     ["Expresie:  Ef3 = C4 ∧ C5 ∧ nodul_1 = C4 ∧ C5 ∧ (¬C3 ∨ C6) = 1.",
      "Pentru a nu fi mascat de Ef1 sau Ef2, trebuie C1 = 0 și ¬(C2 ∧ ¬C3)  ⇒  luăm C1 = C2 = 0.",
      "Disjuncția (¬C3 ∨ C6) = 1 oferă două combinații:",
      "  • R3: C3 = 0, C6 = 0 (off-peak, cota plină)  — M(Ef3, Ef6) maschează Ef6",
      "  • R4: C3 = 1, C6 = 1 (vârf, în cotă)         — M(Ef3, Ef4) maschează Ef4",
      "Se adaugă coloanele R3 și R4  (nr_coloane = 4)."]),
]
for idx, (ttl, col, upto, lines_) in enumerate(steps_1):
    xx = 0.65 + idx * 4.08
    card(s, xx, 1.42, 3.92, 5.42, fill=WHITE, line=LINE, accent=col)
    text(s, xx + 0.18, 1.52, 3.6, 0.32, ttl, size=10.5, color=col, bold=True)
    text(s, xx + 0.18, 1.86, 3.6, 1.55, lines_, size=8.6, color=INK_2, spacing=2)
    mini_dt(s, xx + 0.85, 3.42, upto)

# ============================================================== 12 · CEG STEP-BY-STEP (2/2)
s = new_slide(12, "Testare funcțională · CEG (3/4)",
              "Construcția tabelului de decizie pas cu pas: efectele Ef4, Ef5, Ef6", "natalia", req="1c")

steps_2 = [
    ("Pasul 4 — Efectul Ef4 = 1 (GRANTED_REGULAR)", GREEN, [5],
     ["Expresie:  Ef4 = C6 = 1, cu condiția ca Ef1 = Ef2 = Ef3 = 0 (nemascat).",
      "Alegem C1 = 0, C2 = 0, C3 = 1 (ore de vârf), C4 = 0, C5 = 0 (fără EV),",
      "C6 = 1 (în cotă), C7 = 0, C8 = 1.",
      "Rezultă o singură coloană nouă: R5  (nr_coloane = 5)."]),
    ("Pasul 5 — Efectul Ef5 = 1 (GRANTED_PAID_OVERFLOW)", AMBER, [6, 7],
     ["Expresie:  Ef5 = ¬C6 ∧ nodul_3 = ¬C6 ∧ C7 ∧ (¬C3 ∨ C8) = 1, cu Ef1=Ef2=Ef3=0.",
      "Deci C1 = C2 = C4 = C5 = 0, C6 = 0 (cotă epuizată), C7 = 1 (overflow permis).",
      "Nodul 2 = (¬C3 ∨ C8) = 1 produce două coloane:",
      "  • R6: C3 = 0, C8 = 0  (noaptea, chiar și cu depășire ≥ 5 locuri)",
      "  • R7: C3 = 1, C8 = 1  (ore de vârf, depășire < 5 locuri)",
      "Se adaugă coloanele R6 și R7  (nr_coloane = 7)."]),
    ("Pasul 6 — Efectul Ef6 = 1 (DENIED_QUOTA_EXCEEDED)", RED, [8, 9],
     ["Expresie:  Ef6 = ¬C6 ∧ ¬nodul_3 = ¬C6 ∧ ¬(C7 ∧ (¬C3 ∨ C8)) = 1, cu Ef1..Ef3 = 0.",
      "Deci C6 = 0, iar nodul 3 = 0 se obține în două moduri:",
      "  • R8: C7 = 1, C3 = 1, C8 = 0  (overflow permis, dar la vârf cu depășire ≥ 5)",
      "  • R9: C7 = 0, C3 = 1, C8 = 1  (politica de overflow dezactivată)",
      "Se adaugă coloanele R8 și R9  ⇒  tabelul complet are M = 9 coloane."]),
]
for idx, (ttl, col, cols_added, lines_) in enumerate(steps_2):
    yy = 1.42 + idx * 1.8
    card(s, 0.7, yy, 7.35, 1.66, fill=WHITE, line=LINE, accent=col)
    text(s, 0.95, yy + 0.1, 7.0, 0.3, ttl, size=11.5, color=col, bold=True)
    text(s, 0.95, yy + 0.42, 7.0, 1.18, lines_, size=9.5, color=INK_2, spacing=2.5)

text(s, 8.3, 1.42, 4.35, 0.28, "TABELUL ACUMULAT (R1 … R9)", size=10, color=MUTED, bold=True)
mini_dt(s, 8.3, 1.72, 9)
text(s, 8.3, 5.25, 4.35, 1.5,
     [[{"t": "Bilanț:", "bold": True, "size": 10.5, "color": NATALIA}],
      "p = 8 cauze + q = 6 efecte  ⇒  N = 14 linii.",
      "M = 1 + 1 + 2 + 1 + 2 + 2 = 9 coloane (reguli).",
      "Pe slide-ul următor sunt adăugate valorile",
      "concrete de Input și Output pentru fiecare regulă."],
     size=9.5, color=INK_2, spacing=2)

# ============================================================== 13 · CEG FINAL TABLE WITH INPUT/OUTPUT
s = new_slide(13, "Testare funcțională · CEG (4/4)",
              "Tabelul de decizie final și cazurile de test asociate (tests/test_ceg.py)", "natalia", req="1c")

cols = ["Cauză / Efect"] + [r[0] for r in D.CEG_RULES]
t_rows = [cols]
fills, colors, bolds = {}, {}, {}

for r_i, (cid, lbl) in enumerate(D.CAUSES, start=1):
    row = [f"{cid}  {lbl}"]
    bolds[(r_i, 0)] = True
    for c_i, (_, _, case) in enumerate(D.CEG_RULES, start=1):
        v = str(D.causes_of(case)[cid])
        row.append(v)
        if v == "1":
            fills[(r_i, c_i)] = NATALIA_L
            colors[(r_i, c_i)] = NATALIA
            bolds[(r_i, c_i)] = True
    t_rows.append(row)

for e_offset, (eid, name, _) in enumerate(D.EFFECTS):
    r_i = 9 + e_offset
    row = [f"{eid}  {name}"]
    ec = GREEN if eid in ("Ef1", "Ef3", "Ef4") else AMBER if eid == "Ef5" else RED
    el = GREEN_L if eid in ("Ef1", "Ef3", "Ef4") else AMBER_L if eid == "Ef5" else RED_L
    colors[(r_i, 0)] = ec
    bolds[(r_i, 0)] = True
    for c_i, (_, active_eff, _) in enumerate(D.CEG_RULES, start=1):
        v = "1" if active_eff == eid else "0"
        row.append(v)
        if v == "1":
            fills[(r_i, c_i)] = el
            colors[(r_i, c_i)] = ec
            bolds[(r_i, c_i)] = True
        else:
            colors[(r_i, c_i)] = rgb("CBD5E1")
    t_rows.append(row)

# Input row + Output row (exact ca în exercițiile de laborator)
in_row = ["Input (q, o, h, tier, ev, sp, ovf)"]
out_row = ["Output (decizie barieră)"]
bolds[(15, 0)] = True
bolds[(16, 0)] = True
for c_i, (_, active_eff, case) in enumerate(D.CEG_RULES, start=1):
    q, o, h, tier, ev, sp, ovf = case
    b = lambda x: "T" if x else "F"
    in_row.append(f"({q},{o},{h},{tier.name[:3]},{b(ev)},{b(sp)},{b(ovf)})")
    res = D.run(case)
    oid = D.OUT_ID[res]
    fg, bg = COLOR_MAP[D.OUT_COLOR[oid]]
    out_row.append(f"{oid}: {res.replace('GRANTED_', '').replace('DENIED_', '')}")
    fills[(15, c_i)] = PANEL
    fills[(16, c_i)] = bg
    colors[(16, c_i)] = fg
    bolds[(16, c_i)] = True
t_rows.append(in_row)
t_rows.append(out_row)

aligns = {j: PP_ALIGN.CENTER for j in range(1, 10)}
aligns[0] = PP_ALIGN.LEFT
table(s, 0.65, 1.38, 12.03, t_rows, [2.43] + [1.066] * 9, row_h=0.31, size=8.2, head_size=9.0,
      fills=fills, colors=colors, bolds=bolds, aligns=aligns, zebra=None)

# ============================================================== 14 · CODE COVERAGE
s = new_slide(14, "Acoperire de cod", "Acoperirea la nivel de instrucțiune vs. acoperirea la nivel de ramură",
              "natalia", req="2")

# Top explanation cards: Statement vs Branch coverage
card(s, 0.7, 1.4, 5.85, 1.35, fill=NATALIA_L, accent=NATALIA)
text(s, 0.92, 1.48, 5.5, 0.28, "Acoperire la nivel de instrucțiune (Statement / Line Coverage)",
     size=11, color=NATALIA, bold=True)
text(s, 0.92, 1.76, 5.5, 0.92,
     "Măsoară câte din cele 29 de linii executabile din src/parking_gate.py au fost rulate cel puțin o dată. "
     "O instrucțiune `if cond:` este considerată acoperită chiar dacă condiția a fost evaluată doar pe True sau doar pe False.",
     size=9.5, color=INK_2)

card(s, 6.8, 1.4, 5.85, 1.35, fill=VICTOR_L, accent=VICTOR)
text(s, 7.02, 1.48, 5.5, 0.28, "Acoperire la nivel de ramură / decizie (Branch Coverage)",
     size=11, color=VICTOR, bold=True)
text(s, 7.02, 1.76, 5.5, 0.92,
     "Măsoară câte din cele 12 ramuri decizionale (6 instrucțiuni `if` × 2 ieșiri: True și False) au fost parcurse. "
     "Este mai strictă decât acoperirea la nivel de instrucțiune: un `if` al cărui corp nu se execută lasă 1 linie "
     "neacoperită (din 29 ≈ −3.4%), dar 1 ramură din 12 neacoperită (−8.3%).",
     size=9.5, color=INK_2)

# Chart on bottom-left
cd = CategoryChartData()
cd.categories = ["EP (15 teste)", "BVA (25 teste)", "CEG (9 teste)"]
cd.add_series("Instrucțiuni (din 29)", (100.0, 93.1, 96.6))
cd.add_series("Ramuri (din 12)", (100.0, 83.3, 91.7))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.65), Inches(2.9), Inches(5.6), Inches(3.85), cd)
ch = gf.chart
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.TOP
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(10)
ch.legend.font.name = FONT
va = ch.value_axis
va.maximum_scale = 100
va.minimum_scale = 0
va.major_unit = 25
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = LINE
va.tick_labels.font.size = Pt(9.5)
va.tick_labels.font.color.rgb = MUTED
va.format.line.fill.background()
ca = ch.category_axis
ca.tick_labels.font.size = Pt(10)
ca.tick_labels.font.name = FONT
ca.format.line.color.rgb = LINE
plot = ch.plots[0]
plot.gap_width = 75
plot.overlap = -10
plot.has_data_labels = True
dl = plot.data_labels
dl.number_format = '0.0"%"'
dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size = Pt(9.5)
dl.font.bold = True
for ser, c in zip(plot.series, (NATALIA, VICTOR)):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = c

# Table + explanation on bottom-right
cov_rows = [
    ["Set de teste", "Instrucțiuni", "Ramuri", "Total (pytest-cov)", "Linii neacoperite & motiv"],
    ["EP (15 teste)", "29 / 29 (100%)", "12 / 12 (100%)", "100%",
     "Nicio linie lipsă — clasele finale EC1..EC13 acoperă toate ieșirile I1..I7."],
    ["BVA (25 teste)", "27 / 29 (93.1%)", "10 / 12 (83.3%)", "90%",
     "Liniile 61 (GRANTED_VIP) și 70 (GRANTED_EV_CHARGING): decizii calitative fără frontieră numerică."],
    ["CEG (9 teste)", "28 / 29 (96.6%)", "11 / 12 (91.7%)", "95%",
     "Linia 54 (raise ValueError): graful cauză-efect modelează regulile pe intrări valide."],
]
table(s, 6.45, 2.98, 6.2, cov_rows, [1.15, 1.05, 1.05, 0.8, 2.15], row_h=0.82, size=8.8, head_size=8.8,
      bolds={(i, 0): True for i in range(1, 4)}, aligns={1: PP_ALIGN.CENTER, 2: PP_ALIGN.CENTER, 3: PP_ALIGN.CENTER})
text(s, 0.7, 6.76, 11.9, 0.22,
     "Comandă rulată independent pe fiecare fișier:  pytest tests/test_<set>.py --cov=src --cov-branch --cov-report=term-missing",
     size=9, color=MUTED, font=MONO)

# ============================================================== 15 · DIVIDER II
divider(15, "Partea a II-a · Victor Mura", "Testare structurală", "victor",
        [("3", "Graful orientat de flux de control (CFG), complexitatea ciclomatică V(G) și căile independente", "victor"),
         ("4", "Setul minimal de teste pentru criteriul MC/DC pe decizia compusă EV", "victor")])

# ============================================================== 16 · CFG
s = new_slide(16, "Testare structurală · CFG (1/2)",
              "Graful de flux de control și complexitatea ciclomatică (docs/CFG_Drawio.drawio)", "victor", req="3")
preds = [("N1", "date invalide?"), ("N3", "tier == VIP?"), ("N5", "contractor ∧ ¬vârf?"),
         ("N7", "condiția EV?"), ("N9", "o < q?"), ("N11", "overflow permis?")]
rets = [("N2", "ValueError", RED), ("N4", "GRANTED_VIP", GREEN), ("N6", "DENIED_HOURS", RED),
        ("N8", "GRANTED_EV", GREEN), ("N10", "GRANTED_REGULAR", GREEN), ("N12", "PAID_OVERFLOW", AMBER)]
PX, PW, PH = 0.9, 2.2, 0.62
RX, RW = 3.75, 2.15
BUS = 6.35
y0, dy = 1.5, 0.76
for i, ((pid, pq), (rid, rl, rc)) in enumerate(zip(preds, rets)):
    yy = y0 + i * dy
    d = box(s, PX, yy, PW, PH, fill=VICTOR_L, line=VICTOR, line_w=1.25, shape=MSO_SHAPE.DIAMOND)
    shape_text(d, [[{"t": pid + "  ", "bold": True, "color": VICTOR}, {"t": pq}]], size=9, color=INK, margin=0.08)
    r = box(s, RX, yy + 0.11, RW, 0.4, fill=WHITE, line=rc, line_w=1.25, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    shape_text(r, [[{"t": rid + "  ", "bold": True, "color": rc}, {"t": rl, "font": MONO}]], size=9, color=INK)
    arrow(s, PX + PW, yy + PH / 2, RX, yy + PH / 2, color=GREEN, width=1.25)
    text(s, PX + PW + 0.08, yy + 0.05, 0.6, 0.2, "T", size=8.5, color=GREEN, bold=True)
    arrow(s, RX + RW, yy + PH / 2, BUS, yy + PH / 2, color=LINE, width=1.25, head=False)
    if i < len(preds) - 1:
        arrow(s, PX + PW / 2, yy + PH, PX + PW / 2, yy + dy, color=RED, width=1.25)
        text(s, PX + PW / 2 + 0.08, yy + PH - 0.02, 0.4, 0.2, "F", size=8.5, color=RED, bold=True)
yl = y0 + 5 * dy
n13y = yl + dy
arrow(s, PX + PW / 2, yl + PH, PX + PW / 2, n13y + 0.05, color=RED, width=1.25)
text(s, PX + PW / 2 + 0.08, yl + PH - 0.02, 0.4, 0.2, "F", size=8.5, color=RED, bold=True)
n13 = box(s, PX + 0.05, n13y + 0.05, PW - 0.1, 0.4, fill=WHITE, line=RED, line_w=1.25,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
shape_text(n13, [[{"t": "N13  ", "bold": True, "color": RED}, {"t": "DENIED_QUOTA", "font": MONO}]], size=9, color=INK)
arrow(s, PX + PW - 0.05, n13y + 0.25, BUS, n13y + 0.25, color=LINE, width=1.25, head=False)
arrow(s, BUS, y0 + PH / 2, BUS, n13y + 0.25, color=LINE, width=1.25, head=False)
ex = box(s, BUS - 0.4, n13y + 0.45, 0.8, 0.48, fill=INK, shape=MSO_SHAPE.OVAL)
arrow(s, BUS, n13y + 0.25, BUS, n13y + 0.45, color=INK, width=1.25)
shape_text(ex, "N14", size=9, color=WHITE, bold=True)

text(s, 7.2, 1.5, 5.4, 0.3, "COMPLEXITATEA CICLOMATICĂ McCABE", size=10.5, color=MUTED, bold=True)
card(s, 7.2, 1.85, 5.45, 1.25, fill=VICTOR)
text(s, 7.45, 1.95, 2.7, 1.0, "V(G) = 7", size=38, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 10.2, 2.02, 2.3, 0.9, ["n = 14 noduri", "e = 19 arce", "P = 6 noduri predicat"], size=11.5, color=rgb("D1F2EB"))
methods = [
    ("1. Arce și noduri", "V(G) = e − n + 2", "19 − 14 + 2 = 7   (20 − 14 + 1 = 7 cu arc N14→N1)"),
    ("2. Noduri predicat", "V(G) = P + 1", "6 noduri de decizie + 1 = 7"),
    ("3. Regiuni plane", "V(G) = R", "6 regiuni închise + 1 exterioară = 7"),
]
for i, (m, f, v) in enumerate(methods):
    yy = 3.26 + i * 0.96
    card(s, 7.2, yy, 5.45, 0.84, fill=WHITE, line=LINE)
    text(s, 7.42, yy + 0.1, 2.1, 0.28, m, size=11, color=INK, bold=True)
    text(s, 7.42, yy + 0.42, 2.1, 0.28, f, size=10.5, color=VICTOR, font=MONO)
    text(s, 9.3, yy + 0.16, 3.2, 0.5, v, size=9.0, color=INK_2, align=PP_ALIGN.RIGHT, font=MONO)
text(s, 7.2, 6.24, 5.45, 0.5,
     "Numărul de circuite / căi liniar independente din setul de bază este V(G) = 7.",
     size=11, color=INK_2, italic=True)

# ============================================================== 17 · INDEPENDENT PATHS
s = new_slide(17, "Testare structurală · CFG (2/2)",
              "Cele 7 căi liniar independente și testele asociate", "victor", req="3")
paths = [
    ("P1", "N1 → N2 → N14", "(0, 0, 10, REGULAR, F, F, F)", "I7: ValueError", RED),
    ("P2", "N1 → N3 → N4 → N14", "(10, 10, 22, VIP, F, F, F)", "I1: GRANTED_VIP", GREEN),
    ("P3", "N1 → N3 → N5 → N6 → N14", "(10, 2, 19, CONTRACTOR, F, F, F)", "I2: DENIED_RESTRICTED_HOURS", RED),
    ("P4", "N1 → N3 → N5 → N7 → N8 → N14", "(10, 10, 6, REGULAR, T, T, F)", "I3: GRANTED_EV_CHARGING", GREEN),
    ("P5", "N1 → N3 → N5 → N7 → N9 → N10 → N14", "(10, 5, 11, REGULAR, F, F, F)", "I4: GRANTED_REGULAR", GREEN),
    ("P6", "N1 → N3 → N5 → N7 → N9 → N11 → N12 → N14", "(10, 12, 11, REGULAR, F, F, T)", "I5: GRANTED_PAID_OVERFLOW", AMBER),
    ("P7", "N1 → N3 → N5 → N7 → N9 → N11 → N13 → N14", "(10, 10, 11, REGULAR, F, F, F)", "I6: DENIED_QUOTA_EXCEEDED", RED),
]
rows = [["Cale", "Secvența de noduri parcursă", "Intrare (q, o, h, tier, ev, sp, ovf)", "Ieșire"]] + [
    [p[0], p[1], p[2], p[3]] for p in paths
]
colors = {(i, 3): p[4] for i, p in enumerate(paths, start=1)}
colors.update({(i, 0): VICTOR for i in range(1, 8)})
table(s, 0.7, 1.5, 11.95, rows, [0.75, 4.35, 3.7, 3.15], row_h=0.5, size=10.2, colors=colors,
      bolds={(i, j): True for i in range(1, 8) for j in (0, 3)}, fonts={1: MONO, 2: MONO, 3: MONO},
      aligns={0: PP_ALIGN.CENTER})
card(s, 0.7, 5.72, 11.95, 0.95, fill=VICTOR_L)
text(s, 0.95, 5.86, 11.45, 0.7,
     [[{"t": "Independența liniară: ", "bold": True, "color": VICTOR},
       "fiecare cale Pk introduce cel puțin o muchie nouă față de P1..Pk−1 (de exemplu ramura True a deciziei curente "
       "și în final N11 → N13). Împreună, P1..P7 parcurg toate cele 14 noduri și toate cele 19 arce ale grafului."]],
     size=11, color=INK_2)

# ============================================================== 18 · MC/DC
s = new_slide(18, "Testare structurală · MC/DC",
              "Acoperirea MC/DC pe decizia compusă de acces la stația EV", "victor", req="4")
card(s, 0.7, 1.45, 11.95, 0.82, fill=PANEL)
text(s, 0.95, 1.55, 6.8, 0.62,
     [[{"t": "D = (", "font": MONO}, {"t": "A", "font": MONO, "bold": True, "color": VICTOR},
       {"t": " ∧ ", "font": MONO}, {"t": "B", "font": MONO, "bold": True, "color": NATALIA},
       {"t": ") ∧ (¬", "font": MONO}, {"t": "C", "font": MONO, "bold": True, "color": AMBER},
       {"t": " ∨ ", "font": MONO}, {"t": "Dq", "font": MONO, "bold": True, "color": RED},
       {"t": ")", "font": MONO}]], size=21, color=INK, anchor=MSO_ANCHOR.MIDDLE)
text(s, 7.1, 1.54, 5.4, 0.62,
     [[{"t": "A", "bold": True, "color": VICTOR}, " = is_electric_vehicle     ",
       {"t": "B", "bold": True, "color": NATALIA}, " = has_ev_spots_available"],
      [{"t": "C", "bold": True, "color": AMBER}, " = is_peak_hours (8..17)   ",
       {"t": "Dq", "bold": True, "color": RED}, " = is_within_quota (o < q)"]],
     size=11, color=INK_2)

mcdc_tests = [
    ("T1", "1", "1", "0", "0", "1", "(10, 10, 6, REG, T, T, F)", "GRANTED_EV_CHARGING"),
    ("T2", "0", "1", "0", "0", "0", "(10, 10, 6, REG, F, T, F)", "DENIED_QUOTA_EXCEEDED"),
    ("T3", "1", "0", "0", "0", "0", "(10, 10, 6, REG, T, F, F)", "DENIED_QUOTA_EXCEEDED"),
    ("T4", "1", "1", "1", "0", "0", "(10, 10, 10, REG, T, T, F)", "DENIED_QUOTA_EXCEEDED"),
    ("T5", "1", "1", "1", "1", "1", "(10, 7, 10, REG, T, T, F)", "GRANTED_EV_CHARGING"),
]
rows = [["Test", "A", "B", "C", "Dq", "D", "Valori de intrare", "Rezultat"]]
fills, colors, bolds = {}, {}, {}
for idx, (t, a, b, c, d, dec, inp, res) in enumerate(mcdc_tests, start=1):
    rows.append([t, a, b, c, d, dec, inp, res])
    fills[(idx, None)] = VICTOR_L if idx % 2 == 1 else WHITE
    colors[(idx, 0)] = VICTOR
    bolds[(idx, 0)] = True
    bolds[(idx, 5)] = True
    colors[(idx, 5)] = GREEN if dec == "1" else RED
    colors[(idx, 7)] = GREEN if dec == "1" else RED

table(s, 0.7, 2.45, 6.75, rows, [0.55, 0.36, 0.36, 0.36, 0.42, 0.42, 2.25, 2.03], row_h=0.44, size=8.6, head_size=8.8,
      fills=fills, colors=colors, bolds=bolds, fonts={6: MONO, 7: MONO},
      aligns={j: PP_ALIGN.CENTER for j in range(6)}, zebra=None)

card(s, 0.7, 5.28, 6.75, 1.5, fill=PANEL)
text(s, 0.9, 5.38, 6.35, 0.26, "Verificarea condițiilor MC/DC", size=11, color=INK, bold=True)
text(s, 0.9, 5.66, 6.35, 1.05,
     "• Fiecare condiție atomică A, B, C, Dq ia atât valoarea 1 (True) cât și valoarea 0 (False).\n"
     "• Decizia D ia atât valoarea 1 (în T1, T5) cât și valoarea 0 (în T2, T3, T4).\n"
     "• Pentru fiecare condiție există o pereche de teste în care doar acea condiție se modifică, iar D își schimbă valoarea.",
     size=9.5, color=INK_2)

text(s, 7.7, 2.45, 4.95, 0.28, "PERECHILE DE INDEPENDENȚĂ (N + 1 = 5 TESTE)", size=10, color=MUTED, bold=True)
pairs = [
    ("A", VICTOR, "T1 (1,1,0,0) → D=1", "T2 (0,1,0,0) → D=0", "B=1, C=0, Dq=0 fixe"),
    ("B", NATALIA, "T1 (1,1,0,0) → D=1", "T3 (1,0,0,0) → D=0", "A=1, C=0, Dq=0 fixe"),
    ("C", AMBER, "T1 (1,1,0,0) → D=1", "T4 (1,1,1,0) → D=0", "A=1, B=1, Dq=0 fixe"),
    ("Dq", RED, "T4 (1,1,1,0) → D=0", "T5 (1,1,1,1) → D=1", "A=1, B=1, C=1 fixe"),
]
for i, (cond, c, p1, p2, fixed) in enumerate(pairs):
    yy = 2.8 + i * 0.98
    card(s, 7.7, yy, 4.95, 0.84, fill=WHITE, line=LINE)
    pill(s, 7.88, yy + 0.22, 0.52, 0.38, cond, fill=c, size=11)
    text(s, 8.52, yy + 0.12, 4.0, 0.3, f"{p1}   ↔   {p2}", size=10, color=INK, bold=True, font=MONO)
    text(s, 8.52, yy + 0.46, 4.0, 0.28, fixed, size=9.2, color=MUTED)

# ============================================================== 19 · DIVIDER III
divider(19, "Partea a III-a · Natalia Moroz & Victor Mura", "Testare bazată pe mutații", "team",
        [("5", "Mutant de ordinul 1 echivalent — demonstrație și verificare exhaustivă", "natalia"),
         ("6", "Doi mutanți ne-echivalenți: unul omorât și unul neomorât de același test", "victor"),
         ("7", "Evaluarea automată a mutațiilor cu mutmut și cosmic-ray", "victor")])

# ============================================================== 20 · EQUIVALENT MUTANT
s = new_slide(20, "Testare prin mutații · Mutant echivalent",
              "Mutant de ordinul 1 echivalent (mutants/equivalent_mutant.py)", "natalia", req="5")
code_block(s, 0.7, 1.5, 6.3, 1.35, [
    ("# src/parking_gate.py, linia 57 — definirea intervalului de vârf", "dim"),
    ("- is_peak_hours = (8 <= entry_hour <= 17)", "del"),
    ("+ is_peak_hours = (7 < entry_hour < 18)", "add"),
], size=11.5, line_h=0.32)
text(s, 0.7, 3.05, 6.3, 0.3, "DEMONSTRAȚIA ECHIVALENȚEI SEMANTICE", size=10.5, color=MUTED, bold=True)
steps = [
    ("1", "Parametrul entry_hour este un întreg (h ∈ ℤ), validat în [0, 23] la linia 48."),
    ("2", "În inelul numerelor întregi (ℤ, ≤):  h ≥ 8 ⇔ h ≥ 7 + 1 ⇔ h > 7  și  h ≤ 17 ⇔ h < 18."),
    ("3", "Prin urmare, valoarea booleană a variabilei is_peak_hours este identică în P și în M pentru orice h ∈ ℤ."),
    ("∴", "P(x) = M(x) pentru orice tuplu de intrare x — niciun test posibil nu poate distinge mutantul de original."),
]
for i, (k, t) in enumerate(steps):
    yy = 3.45 + i * 0.78
    last = k == "∴"
    pill(s, 0.7, yy + 0.06, 0.45, 0.45, k, fill=NATALIA if not last else INK, size=13)
    text(s, 1.35, yy + 0.06, 5.65, 0.65, t, size=11.8, color=INK if last else INK_2, bold=last)

card(s, 7.45, 1.5, 5.2, 2.55, fill=NATALIA_L)
text(s, 7.75, 1.68, 4.7, 0.3, "VERIFICARE AUTOMATĂ EXHAUSTIVĂ", size=10.5, color=NATALIA, bold=True)
text(s, 7.75, 2.02, 4.7, 0.85, "1 152", size=46, color=NATALIA, bold=True)
text(s, 7.75, 2.9, 4.7, 1.0,
     "combinații testate în tests/test_equivalent_mutant.py:\n"
     "24 ore (0..23) × 3 roluri × 2³ flag-uri booleene × 2 stări de cotă = 1 152 intrări valide + 4 intrări invalide.",
     size=10.2, color=INK_2)
card(s, 7.45, 4.3, 5.2, 2.35, fill=WHITE, line=LINE)
text(s, 7.75, 4.48, 4.7, 2.05,
     [[{"t": "Efectul asupra scorului de mutație", "bold": True, "size": 12, "color": INK}],
      "Mutanții echivalenți nu reprezintă defecte reale, ci rescrieri sintactice cu aceeași semantică.",
      "Pentru că niciun caz de test nu îi poate omorî, ei se scad din numărul total de mutanți M atunci când se "
      "calculează scorul de mutație:  MS = D / (M − E)."],
     size=10.5, color=INK_2, spacing=5)

# ============================================================== 21 · MANUAL MUTANT #1 (KILLED)
s = new_slide(21, "Testare prin mutații · Mutanți ne-echivalenți (1/2)",
              "Mutantul #1 (ne-echivalent, omorât de testul BVA pentru o = q)", "victor", req="6")

card(s, 0.7, 1.45, 11.95, 0.9, fill=PANEL)
text(s, 0.95, 1.54, 4.5, 0.25, "CAZUL DE TEST FOLOSIT (DIN CERINȚA 1 — BVA, B08)", size=9.5, color=MUTED, bold=True)
text(s, 0.95, 1.82, 5.2, 0.35, "test_bva_occupied_exactly_at_quota", size=13, color=INK, bold=True, font=MONO)
text(s, 6.2, 1.56, 6.2, 0.65,
     ["Intrare:  q = 10, o = 10, h = 12, tier = REGULAR, ev = False, spot = False, ovf = False",
      "Aserțiune în test:  assert res == AccessDecision.DENIED_QUOTA_EXCEEDED"],
     size=10.2, color=INK_2, font=MONO)

code_m1 = [
    ("# src/parking_gate.py — liniile 68–79", "dim"),
    ("    is_within_quota = company_current_occupied < company_allocated_quota", "del"),
    ("    is_within_quota = company_current_occupied <= company_allocated_quota  # MUTAȚIE: < înlocuit cu <=", "add"),
    ("    if is_electric_vehicle and has_ev_spots_available and (not is_peak_hours or is_within_quota):", None),
    ("        return AccessDecision.GRANTED_EV_CHARGING", "dim"),
    ("    if is_within_quota:", "hl"),
    ("        return AccessDecision.GRANTED_REGULAR", "hl"),
    ("    overflow_count = company_current_occupied - company_allocated_quota", None),
    ("    if company_allows_overflow and (not is_peak_hours or overflow_count < 5):", None),
    ("        return AccessDecision.GRANTED_PAID_OVERFLOW", "dim"),
    ("    return AccessDecision.DENIED_QUOTA_EXCEEDED", None),
]
code_block(s, 0.7, 2.52, 7.35, 4.25, code_m1, size=9.3, line_h=0.34)

card(s, 8.25, 2.52, 4.4, 4.25, fill=WHITE, line=LINE, accent=GREEN)
pill(s, 8.5, 2.7, 2.3, 0.34, "MUTANT OMORÂT (KILLED)", fill=GREEN, size=10)
text(s, 8.5, 3.18, 3.95, 3.4,
     [[{"t": "Urmărirea execuției pe (q=10, o=10):", "bold": True, "size": 11, "color": INK}],
      "",
      [{"t": "1. În programul original P:", "bold": True, "color": INK}],
      "   is_within_quota = (10 < 10) = False",
      "   Linia 73 (`if is_within_quota:`) este False.",
      "   Linia 77 (`if company_allows_overflow ...`) este False.",
      "   Returnează DENIED_QUOTA_EXCEEDED.",
      "",
      [{"t": "2. În mutantul M1:", "bold": True, "color": GREEN}],
      "   is_within_quota = (10 <= 10) = True",
      "   Linia 73 devine True și funcția returnează",
      "   imediat GRANTED_REGULAR.",
      "",
      [{"t": "3. Rezultat:", "bold": True, "color": RED}],
      "   GRANTED_REGULAR ≠ DENIED_QUOTA_EXCEEDED",
      "   ⇒ aserțiunea eșuează ⇒ mutantul este omorât."],
     size=9.5, color=INK_2, spacing=1.5)

# ============================================================== 22 · MANUAL MUTANT #2 (SURVIVED)
s = new_slide(22, "Testare prin mutații · Mutanți ne-echivalenți (2/2)",
              "Mutantul #2 (ne-echivalent, supraviețuiește aceluiași test datorită scurtcircuitării)", "victor", req="6")

card(s, 0.7, 1.45, 11.95, 0.9, fill=PANEL)
text(s, 0.95, 1.54, 4.5, 0.25, "ACELAȘI CAZ DE TEST (DIN CERINȚA 1 — BVA, B08)", size=9.5, color=MUTED, bold=True)
text(s, 0.95, 1.82, 5.2, 0.35, "test_bva_occupied_exactly_at_quota", size=13, color=INK, bold=True, font=MONO)
text(s, 6.2, 1.56, 6.2, 0.65,
     ["Intrare:  q = 10, o = 10, h = 12, tier = REGULAR, ev = False, spot = False, company_allows_overflow = False",
      "Aserțiune în test:  assert res == AccessDecision.DENIED_QUOTA_EXCEEDED"],
     size=10.0, color=INK_2, font=MONO)

code_m2 = [
    ("# src/parking_gate.py — liniile 72–82 (codul complet al ramurilor 4, 5 și 6)", "dim"),
    ("    if is_within_quota:                                  # (10 < 10) este False -> nu intră", None),
    ("        return AccessDecision.GRANTED_REGULAR", "dim"),
    ("    overflow_count = company_current_occupied - company_allocated_quota   # 10 - 10 = 0", None),
    ("-   if company_allows_overflow and (not is_peak_hours or overflow_count < 5):", "del"),
    ("+   if company_allows_overflow and (not is_peak_hours or overflow_count < 4):  # MUTAȚIE: 5 -> 4", "add"),
    ("        return AccessDecision.GRANTED_PAID_OVERFLOW", "dim"),
    ("    return AccessDecision.DENIED_QUOTA_EXCEEDED          # se execută atât în P cât și în M2", "hl"),
]
code_block(s, 0.7, 2.52, 7.55, 3.1, code_m2, size=9.0, line_h=0.34)

card(s, 0.7, 5.75, 7.55, 1.05, fill=GREEN_L, accent=GREEN)
text(s, 0.95, 5.84, 7.15, 0.88,
     [[{"t": "De ce M2 NU este echivalent (ce test îl omoară): ", "bold": True, "color": GREEN},
       "pentru intrarea (q=10, o=14, h=10, REGULAR, ev=F, spot=F, company_allows_overflow=True) — adică testul BVA "
       "B22 (overflow_count = 4, la ore de vârf) — programul original evaluează 4 < 5 (True → GRANTED_PAID_OVERFLOW), "
       "pe când M2 evaluează 4 < 4 (False → DENIED_QUOTA_EXCEEDED)."]],
     size=9.5, color=INK_2)

card(s, 8.42, 2.52, 4.23, 4.28, fill=WHITE, line=LINE, accent=AMBER)
pill(s, 8.65, 2.7, 2.9, 0.34, "MUTANT SUPRAVIEȚUITOR (ALIVE)", fill=AMBER, size=9.5)
text(s, 8.65, 3.16, 3.85, 3.5,
     [[{"t": "De ce partea mutată nu se execută în acest test:", "bold": True, "size": 10.5, "color": INK}],
      "",
      "1. La linia 76 se calculează overflow_count = 10 − 10 = 0.",
      "",
      "2. La linia 77 se evaluează condiția:",
      "   company_allows_overflow and (...)",
      "",
      "3. În acest test, company_allows_overflow este False.",
      "",
      "4. Operatorul `and` din Python evaluează cu scurtcircuitare (short-circuit): deoarece operandul stâng este "
      "deja False, paranteza din dreapta `(not is_peak_hours or overflow_count < 4)` NU mai este evaluată.",
      "",
      "5. Ambele variante (P și M2) sar peste `if` și returnează DENIED_QUOTA_EXCEEDED la linia 82 — testul trece "
      "fără să observe mutația."],
     size=9.3, color=INK_2, spacing=1.2)

# ============================================================== 23 · MUTATION TOOLS
s = new_slide(23, "Testare prin mutații · mutmut vs. cosmic-ray",
              "Evaluarea automată a mutațiilor pe cele trei suite de teste", "victor", req="7")

# Explicit legend of what the 3 suites mean
suite_cards = [
    ("Suita Cerinței 1 — Teste funcționale", "49 teste (EP: 15 + BVA: 25 + CEG: 9)",
     "Acoperă toate ramurile și frontierele funcției.", NATALIA, NATALIA_L),
    ("Suita Cerinței 4 — Teste MC/DC", "5 teste (T1 .. T5 din test_mcdc.py)",
     "Vizează exclusiv decizia compusă EV (linia 69).", VICTOR, VICTOR_L),
    ("Suita Combinată — Cerința 1 + Cerința 4", "54 teste (EP + BVA + CEG + MC/DC)",
     "Reunește testele funcționale și testele structurale MC/DC.", INK, PANEL),
]
for i, (st, cnt, desc, col, bg) in enumerate(suite_cards):
    xx = 0.7 + i * 4.05
    card(s, xx, 1.4, 3.85, 1.05, fill=bg, accent=col)
    text(s, xx + 0.2, 1.48, 3.55, 0.26, st, size=10.2, color=col, bold=True)
    text(s, xx + 0.2, 1.74, 3.55, 0.24, cnt, size=9.5, color=INK, bold=True, font=MONO)
    text(s, xx + 0.2, 1.98, 3.55, 0.4, desc, size=8.8, color=INK_2)

suites = [("functional", "Suita Cerinței 1 (EP+BVA+CEG)"),
          ("mcdc", "Suita Cerinței 4 (MC/DC)"),
          ("combined", "Combinat (Cerința 1 + 4)")]
cd = CategoryChartData()
cd.categories = ["Cerința 1 (49 teste)", "Cerința 4 (5 teste)", "Combinat 1+4 (54)"]
cd.add_series("mutmut (40 mutanți)", [MUT["mutmut"][k]["score"] for k, _ in suites])
cd.add_series("cosmic-ray (101 mutanți)", [MUT["cosmic_ray"][k]["score"] for k, _ in suites])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.65), Inches(2.6), Inches(5.75), Inches(2.7), cd)
ch = gf.chart
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.TOP
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(9.5)
va = ch.value_axis
va.maximum_scale = 100
va.minimum_scale = 0
va.major_unit = 25
va.major_gridlines.format.line.color.rgb = LINE
va.tick_labels.font.size = Pt(9)
va.tick_labels.font.color.rgb = MUTED
va.format.line.fill.background()
ch.category_axis.tick_labels.font.size = Pt(9.5)
ch.category_axis.format.line.color.rgb = LINE
plot = ch.plots[0]
plot.gap_width = 70
plot.overlap = -10
plot.has_data_labels = True
plot.data_labels.number_format = '0.0"%"'
plot.data_labels.number_format_is_linked = False
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
plot.data_labels.font.size = Pt(9)
plot.data_labels.font.bold = True
for ser, c in zip(plot.series, (VICTOR, rgb("8FD3C9"))):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = c

rows = [["Suită de teste", "mutmut (uciși / total)", "cosmic-ray (uciși / total)"]]
for k, lbl in suites:
    m, c = MUT["mutmut"][k], MUT["cosmic_ray"][k]
    rows.append([lbl, f"{m['killed']} / {m['total']}  ({m['score']}%)", f"{c['killed']} / {c['total']}  ({c['score']}%)"])
table(s, 0.7, 5.4, 5.7, rows, [2.3, 1.7, 1.7], row_h=0.35, size=9.2, head_size=9.2,
      aligns={1: PP_ALIGN.CENTER, 2: PP_ALIGN.CENTER}, fonts={1: MONO, 2: MONO})

notes = MUT["notes"]
cards_spec = [
    ("Formula scorului de mutație",
     "MS(T) = D / (M − E) × 100%, unde D = mutanți uciși, M = total mutanți generați, E = mutanți echivalenți.",
     INK),
    ("Diferențe între operatorii uneltelor", notes["operators"], VICTOR),
    ("Analiza mutanților supraviețuitori", notes["survivors"], AMBER),
    ("Complementaritatea Cerința 1 vs. Cerința 4", notes["suites"], NATALIA),
]
for i, (ttl, body, c) in enumerate(cards_spec):
    yy = 2.6 + i * 1.06
    card(s, 6.65, yy, 6.0, 0.96, fill=WHITE, line=LINE, accent=c)
    text(s, 6.88, yy + 0.08, 5.65, 0.24, ttl, size=10.2, color=INK, bold=True)
    text(s, 6.88, yy + 0.34, 5.65, 0.58, body, size=8.8, color=INK_2)

# ============================================================== 24 · CONCLUSIONS & TEAM CONTRIBUTION
s = new_slide(24, "Concluzii", "Rezultate obținute și contribuția echipei", "team")
kpis = [
    ("81", "teste unitare (100% trec)"),
    ("100%", "acoperire instrucțiuni & ramuri (EP)"),
    ("V(G) = 7", "căi independente acoperite"),
    ("100%", "scor de mutație ajustat (1 + 4)"),
]
for i, (big, small) in enumerate(kpis):
    xx = 0.7 + i * 3.04
    card(s, xx, 1.45, 2.84, 1.2, fill=PANEL)
    text(s, xx + 0.22, 1.52, 2.4, 0.62, big, size=28, color=INK, bold=True)
    text(s, xx + 0.22, 2.15, 2.4, 0.4, small, size=10.5, color=MUTED)

# Team contribution in the foreground
card(s, 0.7, 2.82, 5.85, 3.05, fill=WHITE, line=LINE, accent=NATALIA)
text(s, 0.95, 2.95, 5.4, 0.3, "Natalia Moroz (50% contribuție)", size=13, color=NATALIA, bold=True)
text(s, 0.95, 3.3, 5.4, 2.4,
     ["• Cerința 1: Definirea claselor de intrare/ieșire și a celor 13 clase finale EP (15 teste), "
      "identificarea tuturor celor 25 de cazuri BVA pe cele 8 frontiere + caz special, proiectarea grafului "
      "cauză-efect (8 cauze, 6 efecte, măști M) și derivarea pas cu pas a tabelului de decizie (9 reguli).",
      "• Cerința 2: Măsurarea acoperirii la nivel de instrucțiune și ramură pe EP, BVA și CEG și identificarea "
      "liniilor neacoperite (61, 70 la BVA; 54 la CEG).",
      "• Cerința 5: Formularea mutantului echivalent de ordin 1 pe intervalul [8, 17], demonstrația pe ℤ și "
      "verificarea exhaustivă pe 1 152 intrări."],
     size=9.5, color=INK_2, spacing=4)

card(s, 6.8, 2.82, 5.85, 3.05, fill=WHITE, line=LINE, accent=VICTOR)
text(s, 7.05, 2.95, 5.4, 0.3, "Victor Mura (50% contribuție)", size=13, color=VICTOR, bold=True)
text(s, 7.05, 3.3, 5.4, 2.4,
     ["• Cerința 3: Construcția grafului de flux de control (14 noduri, 19 arce), calculul complexității "
      "ciclomatice V(G) = 7 prin 3 metode și extragerea celor 7 căi independente.",
      "• Cerința 4: Analiza deciziei compuse EV D = (A ∧ B) ∧ (¬C ∨ Dq), selecția celor 4 perechi de "
      "independență și implementarea setului minimal de N + 1 = 5 teste MC/DC.",
      "• Cerințele 6 & 7: Construcția celor doi mutanți ne-echivalenți (unul omorât, unul mascat prin "
      "scurtcircuitare) și rularea comparativă mutmut vs. cosmic-ray pe cele 3 suite."],
     size=9.5, color=INK_2, spacing=4)

card(s, 0.7, 6.02, 11.95, 0.82, fill=PANEL)
text(s, 0.95, 6.12, 11.45, 0.65,
     [[{"t": "Notă privind instrumentele utilizate: ", "bold": True, "color": INK},
       "modelarea matematică, partiționarea domeniilor, diagramele Draw.io, tabelele de decizie, perechile MC/DC "
       "și analiza mutanților au fost realizate de autori; asistența AI ( documentată în AI_USAGE_LAB.md ) a fost "
       "folosită ca suport de redactare și automatizare a scripturilor de raportare."]],
     size=9.8, color=INK_2)

prs.save(OUT_PPTX)
print("saved", OUT_PPTX, "slides:", len(prs.slides))
