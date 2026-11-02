"""
Generator prezentare — Proiect de laborator TSS (Smart Parking Gate)
Echipa: Victor Mura (50%) & Natalia Moroz (50%)

Rulare (din directorul TSS/):
    python3 proiect_laborator/scripts/build_presentation.py
Produce: proiect_laborator/docs/Prezentare_Laborator_TSS.pptx
Conversia în PDF se face cu PowerPoint (vezi scripts/export_pdf.sh).
"""

import json
import os

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt
from lxml import etree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_PPTX = os.path.join(ROOT, "docs", "Prezentare_Laborator_TSS.pptx")
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
VICTOR = rgb("0E8C7F")       # teal  -> Cerințele 1, 2, 6
VICTOR_L = rgb("E3F4F1")
NATALIA = rgb("5B4FD6")      # indigo -> Cerințele 3, 4, 5, 7
NATALIA_L = rgb("ECEAFB")
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

FONT = "Helvetica Neue"
MONO = "Menlo"

W, H = 13.333, 7.5
TOTAL = 19

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
            s.line.dash_style = 4  # dash
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    s.text_frame.text = ""
    return s


def text(slide, x, y, w, h, content, size=14, color=INK, bold=False, font=FONT,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, italic=False):
    """content: str | list of paragraphs; paragraph = str | list of runs (str or dict)."""
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
        box(slide, x, y + 0.18, 0.06, h - 0.36, fill=accent)
    return s


def table(slide, x, y, w, rows, col_w, row_h=0.32, head_fill=INK, head_color=WHITE,
          size=10.5, head_size=10.5, zebra=PANEL, fills=None, colors=None, bolds=None,
          aligns=None, font=FONT, fonts=None):
    nrows, ncols = len(rows), len(rows[0])
    gt = slide.shapes.add_table(nrows, ncols, Inches(x), Inches(y), Inches(w), Inches(row_h * nrows))
    tbl = gt.table
    # strip default table style banding
    tblPr = gt._element.graphic.graphicData.tbl.tblPr
    tblPr.set("bandRow", "0")
    tblPr.set("firstRow", "0")
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i in range(nrows):
        tbl.rows[i].height = Inches(row_h)
        for j in range(ncols):
            cell = tbl.cell(i, j)
            cell.margin_left = cell.margin_right = Inches(0.08)
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


def code_block(slide, x, y, w, h, lines, size=10.5, line_h=None):
    """lines: list of (text, style) where style in {None,'dim','add','del','hl'}"""
    card_s = box(slide, x, y, w, h, fill=CODE_BG, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
    pad = 0.18
    lh = line_h or (size * 1.45 / 72)
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
        "victor": ("Victor Mura", VICTOR, VICTOR_L),
        "natalia": ("Natalia Moroz", NATALIA, NATALIA_L),
        "team": ("Echipa", TEAM, PANEL),
    }[owner]


def header(slide, n, section, title, owner, req=None):
    name, color, light = owner_meta(owner)
    box(slide, 0, 0, W, H, fill=WHITE)
    box(slide, 0, 0, W, 0.09, fill=color)
    label = section.upper() if req is None else f"CERINȚA {req}  ·  {section.upper()}"
    text(slide, 0.7, 0.42, 8.5, 0.3, label, size=10.5, color=color, bold=True)
    text(slide, 0.7, 0.7, 10.0, 0.6, title, size=25, color=INK, bold=True)
    pill(slide, W - 0.7 - 2.1, 0.45, 2.1, 0.34, name, fill=light, color=color, size=10.5)
    # footer
    box(slide, 0.7, 7.0, W - 1.4, 0.01, fill=LINE)
    text(slide, 0.7, 7.08, 8, 0.25, "TSS · Proiect de laborator · Smart Parking Gate", size=9, color=MUTED)
    text(slide, W - 1.7, 7.08, 1.0, 0.25, f"{n:02d} / {TOTAL}", size=9, color=MUTED, align=PP_ALIGN.RIGHT)


def new_slide(n, section, title, owner, req=None):
    s = prs.slides.add_slide(BLANK)
    header(s, n, section, title, owner, req)
    return s


def divider(n, part, title, owner, items):
    name, color, light = owner_meta(owner)
    s = prs.slides.add_slide(BLANK)
    box(s, 0, 0, W, H, fill=INK)
    box(s, 0, 0, 0.35, H, fill=color)
    text(s, 1.2, 2.0, 8, 0.4, part.upper(), size=14, color=color if owner != "team" else rgb("9FB3C8"), bold=True)
    text(s, 1.2, 2.45, 10.5, 1.2, title, size=40, color=WHITE, bold=True)
    for i, (req, label, who) in enumerate(items):
        yy = 4.05 + i * 0.55
        _, c, _ = owner_meta(who)
        pill(s, 1.2, yy, 1.35, 0.36, f"Cerința {req}", fill=c, size=10.5)
        text(s, 2.75, yy + 0.04, 8, 0.36, label, size=15, color=rgb("DCE4EB"))
    text(s, W - 1.7, 7.08, 1.0, 0.25, f"{n:02d} / {TOTAL}", size=9, color=rgb("6B7A8F"), align=PP_ALIGN.RIGHT)
    return s


# ---------------------------------------------------------------- data
def load_mutation():
    with open(MUTATION_JSON) as fh:
        return json.load(fh)


MUT = load_mutation()

# ============================================================== 01 · TITLE
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, W, H, fill=INK)
box(s, 0, 0, W, 0.09, fill=VICTOR)
box(s, W / 2, 0, W / 2, 0.09, fill=NATALIA)
text(s, 0.9, 1.0, 9, 0.35, "TESTAREA SISTEMELOR SOFTWARE  ·  PROIECT DE LABORATOR", size=12, color=rgb("9FB3C8"), bold=True)
text(s, 0.9, 1.5, 8.5, 1.0, "Smart Parking Gate", size=54, color=WHITE, bold=True)
text(s, 0.9, 2.55, 7.6, 1.0,
     "Testare funcțională, structurală și prin mutații pentru motorul de decizie al unei parcări corporate multi-tenant",
     size=17, color=rgb("C9D4E0"))

# key numbers (right column)
stats = [("80", "teste automate"), ("V(G) = 7", "complexitate ciclomatică"),
         ("5", "teste MC/DC (N + 1)"), ("2", "unelte de mutație")]
for i, (big, small) in enumerate(stats):
    yy = 1.05 + i * 1.02
    box(s, 9.55, yy, 0.05, 0.78, fill=VICTOR if i % 2 == 0 else NATALIA)
    text(s, 9.8, yy - 0.04, 3, 0.55, big, size=28, color=WHITE, bold=True)
    text(s, 9.8, yy + 0.48, 3, 0.3, small, size=11, color=rgb("9FB3C8"))

# people
for i, (name, reqs, color) in enumerate([
        ("Victor Mura", "Cerințele 1, 2, 5  ·  testare funcțională, acoperire, mutant echivalent", VICTOR),
        ("Natalia Moroz", "Cerințele 3, 4, 6, 7  ·  CFG, MC/DC, mutanți ne-echivalenți, unelte", NATALIA)]):
    xx = 0.9 + i * 4.3
    box(s, xx, 4.7, 4.0, 1.25, fill=rgb("18263B"), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    box(s, xx, 4.7, 0.07, 1.25, fill=color)
    text(s, xx + 0.3, 4.85, 3.5, 0.35, name, size=17, color=WHITE, bold=True)
    text(s, xx + 0.3, 5.25, 3.55, 0.6, reqs, size=11, color=rgb("C9D4E0"))
    pill(s, xx + 2.95, 4.88, 0.85, 0.3, "50%", fill=color, size=10)
text(s, 0.9, 6.75, 11, 0.3,
     "Universitatea din București  ·  FMI  ·  Master Ingineria Sistemelor Software, anul II  ·  2026",
     size=10.5, color=rgb("6B7A8F"))

# ============================================================== 02 · AGENDA
s = new_slide(2, "Structura prezentării", "7 cerințe, două perspective, o singură funcție", "team")
agenda = [
    ("1", "Testare funcțională", "EP · BVA · Graf cauză-efect", "victor"),
    ("2", "Acoperire de cod", "pytest-cov, fiecare set separat", "victor"),
    ("3", "Graf de control", "CFG · V(G) · căi independente", "natalia"),
    ("4", "MC/DC", "decizia compusă EV, 5 teste", "natalia"),
    ("5", "Mutant echivalent", "ordin 1, demonstrație pe ℤ", "victor"),
    ("6", "Mutanți ne-echivalenți", "unul ucis, unul supraviețuitor", "natalia"),
    ("7", "Unelte de mutație", "mutmut vs. cosmic-ray", "natalia"),
]
cw, ch, gx, gy = 2.82, 2.05, 0.21, 0.28
for i, (num, title_, sub, who) in enumerate(agenda):
    row, col = divmod(i, 4)
    xx = 0.7 + col * (cw + gx) + (0 if row == 0 else (cw + gx) / 2)
    yy = 1.65 + row * (ch + gy)
    _, c, light = owner_meta(who)
    card(s, xx, yy, cw, ch, fill=WHITE, line=LINE)
    box(s, xx, yy, cw, 0.08, fill=c)
    text(s, xx + 0.25, yy + 0.3, 1.2, 0.6, f"0{num}", size=30, color=c, bold=True)
    text(s, xx + 0.25, yy + 0.98, cw - 0.4, 0.4, title_, size=15.5, color=INK, bold=True)
    text(s, xx + 0.25, yy + 1.36, cw - 0.4, 0.5, sub, size=11, color=MUTED)
# legend
for i, (who, lbl) in enumerate([("victor", "Victor Mura — 50%"), ("natalia", "Natalia Moroz — 50%")]):
    _, c, _ = owner_meta(who)
    box(s, 0.7 + i * 2.8, 6.55, 0.22, 0.22, fill=c, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    text(s, 1.02 + i * 2.8, 6.55, 2.4, 0.25, lbl, size=11, color=INK_2)
text(s, 6.6, 6.55, 6.0, 0.25, "Culoarea fiecărui slide indică autorul secțiunii.", size=11, color=MUTED, align=PP_ALIGN.RIGHT)

# ============================================================== 03 · SYSTEM UNDER TEST
s = new_slide(3, "Sistemul testat", "Bariera unui campus de birouri cu mai mulți chiriași", "team")
text(s, 0.7, 1.6, 4.6, 0.3, "SCENARIU", size=10.5, color=MUTED, bold=True)
bul = [
    [{"t": "Mai multe companii ", "bold": True}, "împart aceeași parcare; fiecare are o cotă contractuală de locuri gratuite."],
    [{"t": "O singură barieră ", "bold": True}, "decide instant accesul pe baza a 7 parametri."],
    [{"t": "Resurse comune: ", "bold": True}, "stații de încărcare EV și o zonă de overflow plătită de companie."],
    [{"t": "Funcție pură, deterministă ", "bold": True}, "— fără I/O, ideală pentru testare unitară și mutații."],
]
for i, b in enumerate(bul):
    yy = 2.0 + i * 0.95
    box(s, 0.7, yy + 0.08, 0.1, 0.1, fill=INK, shape=MSO_SHAPE.OVAL)
    text(s, 0.98, yy, 4.3, 0.9, [b], size=13.5, color=INK_2)

text(s, 5.9, 1.6, 6.7, 0.3, "IERARHIA DECIZIILOR — evaluate_parking_access()", size=10.5, color=MUTED, bold=True)
pipeline = [
    ("R0", "Parametri valizi?", "nu", "ValueError", RED, RED_L),
    ("R1", "Angajat VIP?", "da", "GRANTED_VIP", GREEN, GREEN_L),
    ("R2", "Contractor în afara 08–17?", "da", "DENIED_RESTRICTED_HOURS", RED, RED_L),
    ("R3", "EV + stație liberă + (noapte ∨ în cotă)?", "da", "GRANTED_EV_CHARGING", GREEN, GREEN_L),
    ("R4", "Ocupate < cotă?", "da", "GRANTED_REGULAR", GREEN, GREEN_L),
    ("R5", "Overflow permis și (noapte ∨ depășire < 5)?", "da", "GRANTED_PAID_OVERFLOW", AMBER, AMBER_L),
    ("R6", "Altfel", "", "DENIED_QUOTA_EXCEEDED", RED, RED_L),
]
for i, (rid, q, edge, out, c, light) in enumerate(pipeline):
    yy = 2.0 + i * 0.68
    b = box(s, 5.9, yy, 3.75, 0.5, fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
    pill(s, 6.0, yy + 0.1, 0.5, 0.3, rid, fill=INK, size=9.5)
    text(s, 6.62, yy + 0.04, 3.0, 0.45, q, size=11, color=INK, anchor=MSO_ANCHOR.MIDDLE)
    if i < len(pipeline) - 1:
        arrow(s, 6.25, yy + 0.5, 6.25, yy + 0.68, color=LINE, width=1.5)
    arrow(s, 9.65, yy + 0.25, 10.05, yy + 0.25, color=c, width=1.5)
    if edge:
        text(s, 9.68, yy - 0.02, 0.4, 0.2, edge, size=8.5, color=c, bold=True)
    ob = box(s, 10.1, yy + 0.05, 2.55, 0.4, fill=light, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    shape_text(ob, out, size=9.5, color=c, bold=True, font=MONO)

# ============================================================== 04 · CODE + INPUTS
s = new_slide(4, "Sistemul testat", "Funcția sub test și domeniile de intrare", "team")
code = [
    ("def evaluate_parking_access(quota, occupied, hour, tier,", None),
    ("        is_ev, has_ev_spots, allows_overflow):", None),
    ("    if quota <= 0 or occupied < 0 or hour < 0 or hour > 23:", None),
    ("        raise ValueError(...)", "dim"),
    ("    is_peak = (8 <= hour <= 17)", None),
    ("    if tier == VIP:", None),
    ("        return GRANTED_VIP", "dim"),
    ("    if tier == CONTRACTOR and not is_peak:", None),
    ("        return DENIED_RESTRICTED_HOURS", "dim"),
    ("    within = occupied < quota", None),
    ("    if is_ev and has_ev_spots and (not is_peak or within):", "hl"),
    ("        return GRANTED_EV_CHARGING", "dim"),
    ("    if within:", None),
    ("        return GRANTED_REGULAR", "dim"),
    ("    overflow = occupied - quota", None),
    ("    if allows_overflow and (not is_peak or overflow < 5):", None),
    ("        return GRANTED_PAID_OVERFLOW", "dim"),
    ("    return DENIED_QUOTA_EXCEEDED", "dim"),
]
code_block(s, 0.7, 1.6, 6.55, 5.15, code, size=10.5, line_h=0.268)
text(s, 0.7, 6.78, 6.5, 0.2, "Simplificat pentru lizibilitate — sursa completă: src/parking_gate.py.  Linia evidențiată = decizia MC/DC.",
     size=9, color=MUTED, italic=True)
rows = [["Parametru", "Tip", "Domeniu valid"],
        ["company_allocated_quota", "int", "≥ 1"],
        ["company_current_occupied", "int", "≥ 0"],
        ["entry_hour", "int", "0 … 23  (vârf: 8 … 17)"],
        ["tier", "Enum", "REGULAR · VIP · CONTRACTOR"],
        ["is_electric_vehicle", "bool", "True / False"],
        ["has_ev_spots_available", "bool", "True / False"],
        ["company_allows_overflow", "bool", "True / False"]]
table(s, 7.6, 1.6, 5.05, rows, [2.45, 0.55, 2.05], row_h=0.42, size=10, fonts={0: MONO})
card(s, 7.6, 5.2, 5.05, 1.55, fill=PANEL)
text(s, 7.85, 5.35, 4.6, 0.3, "6 rezultate posibile", size=13, color=INK, bold=True)
outs = [("VIP", GREEN), ("EV", GREEN), ("REGULAR", GREEN), ("OVERFLOW", AMBER), ("HOURS ✕", RED), ("QUOTA ✕", RED)]
for i, (o, c) in enumerate(outs):
    row, col = divmod(i, 3)
    pill(s, 7.85 + col * 1.58, 5.8 + row * 0.45, 1.45, 0.34, o, fill=c, size=9.5)

# ============================================================== 05 · DIVIDER I
divider(5, "Partea I · Victor Mura", "Testare funcțională", "victor",
        [("1", "Partiționare în clase de echivalență, valori de frontieră, graf cauză-efect", "victor"),
         ("2", "Acoperirea de cod obținută de fiecare set, măsurată separat", "victor")])

# ============================================================== 06 · EP
s = new_slide(6, "Testare funcțională", "Partiționare în clase de echivalență", "victor", req="1a")
rows = [["Parametru", "Clase valide", "Clase invalide"],
        ["quota  (q)", "q ≥ 1", "q = 0  ·  q < 0"],
        ["occupied  (o)", "o < q (sub cotă)  ·  o = q (la cotă)  ·  o > q (peste cotă)", "o < 0"],
        ["entry_hour  (h)", "0–7 (dimineață)  ·  8–17 (vârf)  ·  18–23 (seară)", "h < 0  ·  h ≥ 24"],
        ["tier", "VIP  ·  REGULAR  ·  CONTRACTOR", "— (garantat de Enum)"],
        ["is_ev, has_spots", "(T, T)  ·  (T, F)  ·  (F, –)", "—"],
        ["allows_overflow", "True  ·  False", "—"]]
fills = {(i, 2): RED_L for i in range(1, 4)}
colors = {(i, 2): RED for i in range(1, 4)}
table(s, 0.7, 1.6, 8.3, rows, [1.85, 4.45, 2.0], row_h=0.58, size=11.5, fills=fills, colors=colors,
      bolds={(i, 0): True for i in range(1, 7)})
card(s, 9.35, 1.6, 3.3, 4.06, fill=VICTOR_L)
text(s, 9.6, 1.8, 2.9, 0.8, "13", size=54, color=VICTOR, bold=True)
text(s, 9.6, 2.75, 2.9, 0.3, "cazuri de test", size=13, color=INK, bold=True)
text(s, 9.6, 3.2, 2.85, 2.3,
     ["6 pentru clasele invalide (ValueError).", "7 pentru clasele valide, câte unul pentru fiecare rezultat al funcției.",
      "tests/test_ep.py"], size=11.5, color=INK_2, spacing=6)
text(s, 0.7, 6.0, 12, 0.6,
     [[{"t": "Ideea: ", "bold": True, "color": VICTOR},
       "un reprezentant per clasă; dacă funcționează pentru el, presupunem că funcționează pentru toată clasa. "
       "Limita: nu spune nimic despre marginile clasei — de aceea urmează BVA."]], size=12, color=INK_2)

# ============================================================== 07 · BVA
s = new_slide(7, "Testare funcțională", "Analiza valorilor de frontieră", "victor", req="1b")


def number_line(slide, x, y, w, lo, hi, marks, bands, title_, unit_label=None):
    text(slide, x, y - 0.65, w, 0.3, title_, size=12.5, color=INK, bold=True)
    span = hi - lo
    sx = lambda v: x + (v - lo) / span * w
    for (a, b, fill, lbl) in bands:
        box(slide, sx(a), y - 0.09, sx(b) - sx(a), 0.18, fill=fill)
        if lbl:
            text(slide, sx(a), y - 0.32, sx(b) - sx(a), 0.22, lbl, size=8.5, color=MUTED, align=PP_ALIGN.CENTER)
    box(slide, x, y - 0.01, w, 0.02, fill=INK_2)
    for v, kind in marks:
        c = {"bad": RED, "ok": VICTOR, "edge": INK}[kind]
        d = 0.2
        box(slide, sx(v) - d / 2, y - d / 2, d, d, fill=c, shape=MSO_SHAPE.OVAL, line=WHITE, line_w=1.5)
        text(slide, sx(v) - 0.3, y + 0.16, 0.6, 0.25, str(v), size=10, color=c, bold=True, align=PP_ALIGN.CENTER)


number_line(s, 1.0, 2.35, 11.3, -2, 25,
            [(-1, "bad"), (0, "ok"), (1, "ok"), (7, "ok"), (8, "edge"), (9, "ok"), (16, "ok"), (17, "edge"),
             (18, "ok"), (22, "ok"), (23, "ok"), (24, "bad")],
            [(-2, -0.5, RED_L, "invalid"), (-0.5, 7.5, PANEL, "off-peak"), (7.5, 17.5, VICTOR_L, "ore de vârf"),
             (17.5, 23.5, PANEL, "off-peak"), (23.5, 25, RED_L, "invalid")],
            "entry_hour — limitele zilei și ale intervalului de vârf")
number_line(s, 1.0, 4.15, 5.2, 7, 13,
            [(9, "ok"), (10, "edge"), (11, "ok")],
            [(7, 9.5, VICTOR_L, "sub cotă"), (9.5, 13, PANEL, "cotă atinsă")],
            "occupied față de quota = 10")
number_line(s, 7.1, 4.15, 5.2, 2, 8,
            [(4, "ok"), (5, "edge"), (6, "ok")],
            [(2, 4.5, AMBER_L, "overflow permis"), (4.5, 8, RED_L, "refuzat")],
            "depășire la ore de vârf  (occupied − quota)")
rows = [["Frontieră", "Valori testate", "Ce prinde"],
        ["quota ≥ 1", "0 · 1 · 2", "cote zero sau negative"],
        ["occupied ≥ 0", "−1 · 0 · 1", "contoare negative"],
        ["occupied < quota", "9 · 10 · 11", "< scris greșit ca ≤"],
        ["overflow < 5", "4 · 5 · 6", "pragul strict de overflow"]]
table(s, 1.0, 4.95, 7.6, rows, [2.1, 2.0, 3.5], row_h=0.36, size=10.5, fonts={1: MONO})
card(s, 9.0, 4.95, 3.3, 1.8, fill=VICTOR_L)
text(s, 9.25, 5.05, 2.9, 0.8, "24", size=44, color=VICTOR, bold=True)
text(s, 9.25, 5.82, 2.9, 0.8, ["cazuri de test", "tests/test_bva.py"], size=11.5, color=INK_2)

# ============================================================== 08 · CEG GRAPH
s = new_slide(8, "Testare funcțională", "Graful cauză-efect", "victor", req="1c")
causes = ["C1  tier = VIP", "C2  tier = CONTRACTOR", "C3  ore de vârf", "C4  vehicul electric",
          "C5  stație EV liberă", "C6  ocupate < cotă", "C7  overflow permis", "C8  depășire < 5"]
cy = {}
for i, c in enumerate(causes):
    yy = 1.55 + i * 0.62
    b = box(s, 0.7, yy, 2.55, 0.44, fill=VICTOR_L, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    shape_text(b, c, size=10.5, color=INK, align=PP_ALIGN.LEFT, margin=0.12)
    cy[i + 1] = yy + 0.22
CX = 3.25  # right edge of causes

effects = [(1, "E1  GRANTED_VIP", GREEN_L, GREEN), (2, "E2  DENIED_HOURS", RED_L, RED),
           (3, "E3  GRANTED_EV", GREEN_L, GREEN), (4, "E4  GRANTED_REGULAR", GREEN_L, GREEN),
           (5, "E5  PAID_OVERFLOW", AMBER_L, AMBER), (6, "E6  DENIED_QUOTA", RED_L, RED)]
ey = {1: cy[1], 2: 2.62, 3: 3.95, 4: cy[6], 5: 5.6, 6: 6.35}
EX = 8.35
for k, lbl, fill, c in effects:
    b = box(s, EX, ey[k] - 0.22, 2.5, 0.44, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    shape_text(b, lbl, size=10, color=c, bold=True, font=MONO, align=PP_ALIGN.LEFT, margin=0.12)

R = 0.25


def gate(slide, cx_, cy_, label):
    g = box(slide, cx_ - R, cy_ - R, 2 * R, 2 * R, fill=WHITE, line=INK, line_w=1.25, shape=MSO_SHAPE.OVAL)
    shape_text(g, label, size=7.5, color=INK, bold=True, margin=0)
    return (cx_, cy_)


I1 = gate(s, 4.15, cy[3], "NOT")
I3 = gate(s, 4.15, (cy[4] + cy[5]) / 2, "AND")
I2 = gate(s, 5.45, 2.62, "AND")
I4 = gate(s, 5.45, 4.5, "OR")
I6 = gate(s, 5.45, 5.75, "OR")
I5 = gate(s, 6.85, 3.95, "AND")
I7 = gate(s, 6.85, 5.6, "AND")


def link(a, b, color=MUTED, dash=False):
    (x1, y1), (x2, y2) = a, b
    import math
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    arrow(s, x1 + dx / d * R, y1 + dy / d * R, x2 - dx / d * R, y2 - dy / d * R, color=color, dash=dash)


def from_cause(i, g):
    gx_, gy_ = g
    import math
    dx, dy = gx_ - CX, gy_ - cy[i]
    d = math.hypot(dx, dy)
    arrow(s, CX, cy[i], gx_ - dx / d * R, gy_ - dy / d * R, color=MUTED)


def to_effect(g, k, color):
    arrow(s, g[0] + R, g[1], EX, ey[k], color=color, width=1.5)


arrow(s, CX, cy[1], EX, ey[1], color=GREEN, width=1.5)        # C1 -> E1
from_cause(3, I1)
from_cause(2, I2); link(I1, I2)
to_effect(I2, 2, RED)
from_cause(4, I3); from_cause(5, I3)
link(I1, I4); from_cause(6, I4)
link(I3, I5); link(I4, I5)
to_effect(I5, 3, GREEN)
arrow(s, CX, cy[6], EX, ey[4], color=GREEN, width=1.5)        # C6 -> E4
link(I1, I6); from_cause(8, I6)
from_cause(7, I7); link(I6, I7)
to_effect(I7, 5, AMBER)
text(s, 7.0, 6.22, 1.3, 0.3, "altfel →", size=10, color=MUTED, italic=True, align=PP_ALIGN.RIGHT)

# legend / constraints
card(s, 11.15, 1.55, 1.5, 4.95, fill=PANEL)
text(s, 11.3, 1.7, 1.25, 4.7,
     [[{"t": "Constrângere", "bold": True}], "E(C1, C2): un angajat nu poate fi VIP și contractor.", "",
      [{"t": "Porți", "bold": True}], "NOT = ore off-peak", "AND/OR = condiții compuse", "",
      [{"t": "Prioritate", "bold": True}], "E1 > E2 > E3 > E4 > E5 > E6"],
     size=9.5, color=INK_2, spacing=2)

# ============================================================== 09 · CEG TABLE
s = new_slide(9, "Testare funcțională", "Din graf în tabel de decizie: 9 reguli → 9 teste", "victor", req="1c")
D = "–"
rules = [
    ("R1", "1", "0", D, D, D, D, D, D, "E1 VIP"),
    ("R2", "0", "1", "0", D, D, D, D, D, "E2 HOURS ✕"),
    ("R3", "0", "0", "0", "1", "1", D, D, D, "E3 EV"),
    ("R4", "0", "0", "1", "1", "1", "1", D, D, "E3 EV"),
    ("R5", "0", "0", D, "0", D, "1", D, D, "E4 REGULAR"),
    ("R6", "0", "0", "0", "0", D, "0", "1", D, "E5 OVERFLOW"),
    ("R7", "0", "0", "1", "0", D, "0", "1", "1", "E5 OVERFLOW"),
    ("R8", "0", "0", "1", "0", D, "0", "1", "0", "E6 QUOTA ✕"),
    ("R9", "0", "0", D, "0", D, "0", "0", D, "E6 QUOTA ✕"),
]
rows = [["Regulă", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "Efect"]] + [list(r) for r in rules]
fills, colors = {}, {}
for i, r in enumerate(rules, start=1):
    for j in range(1, 9):
        if r[j] == "1":
            fills[(i, j)] = VICTOR_L
            colors[(i, j)] = VICTOR
        elif r[j] == D:
            colors[(i, j)] = rgb("B4BECB")
    eff = r[9]
    c = GREEN if eff.startswith(("E1", "E3", "E4")) else AMBER if eff.startswith("E5") else RED
    colors[(i, 9)] = c
center = {j: PP_ALIGN.CENTER for j in range(0, 9)}
table(s, 0.7, 1.6, 8.6, rows, [0.95] + [0.68] * 8 + [2.21], row_h=0.44, size=11.5, fills=fills,
      colors=colors, aligns=center, bolds={(i, j): True for i in range(1, 10) for j in (0, 9)}, zebra=None)
card(s, 9.65, 1.6, 3.0, 4.4, fill=PANEL)
text(s, 9.9, 1.8, 2.6, 4.0,
     [[{"t": "Cum citim tabelul", "bold": True, "size": 13}],
      [{"t": "1", "bold": True, "color": VICTOR}, " = cauza trebuie să fie adevărată"],
      [{"t": "0", "bold": True}, " = cauza trebuie să fie falsă"],
      [{"t": "–", "bold": True, "color": rgb("B4BECB")}, " = nu contează"], "",
      "Fiecare regulă devine exact un caz de test în tests/test_ceg.py.", "",
      "Cel mai mic set funcțional (9 teste), dar acoperă toate combinațiile logice ale specificației."],
     size=11, color=INK_2, spacing=4)
text(s, 0.7, 6.25, 8.6, 0.5,
     "C1 VIP · C2 contractor · C3 vârf · C4 EV · C5 stație liberă · C6 în cotă · C7 overflow permis · C8 depășire < 5",
     size=10, color=MUTED)

# ============================================================== 10 · COVERAGE
s = new_slide(10, "Acoperire de cod", "Același cod, trei seturi de teste, trei rezultate", "victor", req="2")
cd = CategoryChartData()
cd.categories = ["EP (13 teste)", "BVA (24 teste)", "CEG (9 teste)"]
cd.add_series("Instrucțiuni %", (100.0, 93.1, 96.6))
cd.add_series("Ramuri %", (100.0, 83.3, 91.7))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.5), Inches(6.6), Inches(5.2), cd)
ch = gf.chart
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.TOP
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(11)
ch.legend.font.name = FONT
va = ch.value_axis
va.maximum_scale = 100
va.minimum_scale = 0
va.major_unit = 25
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = LINE
va.tick_labels.font.size = Pt(10)
va.tick_labels.font.color.rgb = MUTED
va.format.line.fill.background()
ca = ch.category_axis
ca.tick_labels.font.size = Pt(11)
ca.tick_labels.font.name = FONT
ca.format.line.color.rgb = LINE
plot = ch.plots[0]
plot.gap_width = 70
plot.overlap = -10
plot.has_data_labels = True
dl = plot.data_labels
dl.number_format = '0"%"'
dl.number_format_is_linked = False
dl.position = XL_LABEL_POSITION.OUTSIDE_END
dl.font.size = Pt(10.5)
dl.font.bold = True
for ser, c in zip(plot.series, (VICTOR, rgb("8FD3C9"))):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = c

insights = [
    ("EP", "100%", "29/29 instrucțiuni, 12/12 ramuri", "O clasă per rezultat ⇒ fiecare ramură e atinsă cel puțin o dată.", GREEN),
    ("BVA", "90%", "lipsesc liniile 61 și 70", "VIP și EV sunt decizii calitative — nu au „frontieră” numerică de testat.", AMBER),
    ("CEG", "95%", "lipsește linia 54", "Graful modelează doar intrări valide; ValueError nu e o cauză de business.", AMBER),
]
for i, (k, pct, detail, why, c) in enumerate(insights):
    yy = 1.6 + i * 1.62
    card(s, 7.55, yy, 5.1, 1.42, fill=WHITE, line=LINE, accent=c)
    text(s, 7.85, yy + 0.18, 1.2, 0.4, k, size=15, color=INK, bold=True)
    text(s, 11.2, yy + 0.12, 1.25, 0.45, pct, size=22, color=c, bold=True, align=PP_ALIGN.RIGHT)
    text(s, 7.85, yy + 0.55, 4.6, 0.3, detail, size=10.5, color=MUTED, font=MONO)
    text(s, 7.85, yy + 0.85, 4.6, 0.55, why, size=11, color=INK_2)
text(s, 0.7, 6.75, 6.4, 0.25, "pytest --cov=src --cov-branch, rulat separat pe fiecare set · src/parking_gate.py",
     size=9, color=MUTED, italic=True)

# ============================================================== 11 · DIVIDER II
divider(11, "Partea II · Natalia Moroz", "Testare structurală", "natalia",
        [("3", "Graful de control, complexitatea ciclomatică, căile independente", "natalia"),
         ("4", "Modified Condition / Decision Coverage pe decizia compusă EV", "natalia")])

# ============================================================== 12 · CFG
s = new_slide(12, "Testare structurală", "Graful de flux de control", "natalia", req="3")
preds = [("N1", "date invalide?"), ("N3", "VIP?"), ("N5", "contractor ∧ ¬vârf?"),
         ("N7", "condiția EV"), ("N9", "în cotă?"), ("N11", "overflow?")]
rets = [("N2", "ValueError", RED), ("N4", "GRANTED_VIP", GREEN), ("N6", "DENIED_HOURS", RED),
        ("N8", "GRANTED_EV", GREEN), ("N10", "GRANTED_REGULAR", GREEN), ("N12", "PAID_OVERFLOW", AMBER)]
PX, PW, PH = 0.9, 2.2, 0.62
RX, RW = 3.75, 2.15
BUS = 6.35
y0, dy = 1.55, 0.76
for i, ((pid, pq), (rid, rl, rc)) in enumerate(zip(preds, rets)):
    yy = y0 + i * dy
    d = box(s, PX, yy, PW, PH, fill=NATALIA_L, line=NATALIA, line_w=1.25, shape=MSO_SHAPE.DIAMOND)
    shape_text(d, [[{"t": pid + "  ", "bold": True, "color": NATALIA}, {"t": pq}]], size=9, color=INK, margin=0.1)
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
ex = box(s, BUS - 0.4, n13y + 0.45, 0.8, 0.5, fill=INK, shape=MSO_SHAPE.OVAL)
arrow(s, BUS, n13y + 0.25, BUS, n13y + 0.45, color=INK, width=1.25)
shape_text(ex, "N14", size=9, color=WHITE, bold=True)

# metrics
text(s, 7.2, 1.55, 5.4, 0.3, "COMPLEXITATE CICLOMATICĂ", size=10.5, color=MUTED, bold=True)
card(s, 7.2, 1.9, 5.45, 1.25, fill=NATALIA)
text(s, 7.5, 2.0, 3, 1.0, "V(G) = 7", size=38, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
text(s, 10.3, 2.08, 2.2, 0.9, ["14 noduri", "19 arce", "6 noduri predicat"], size=11.5, color=rgb("E2DFFB"))
methods = [("Arce și noduri", "E − N + 2P", "19 − 14 + 2 = 7"),
           ("Noduri predicat", "P + 1", "6 + 1 = 7"),
           ("Regiuni", "R", "6 închise + 1 exterioară = 7")]
for i, (m, f, v) in enumerate(methods):
    yy = 3.35 + i * 0.95
    card(s, 7.2, yy, 5.45, 0.8, fill=WHITE, line=LINE)
    text(s, 7.45, yy + 0.12, 2.2, 0.3, m, size=12, color=INK, bold=True)
    text(s, 7.45, yy + 0.43, 2.2, 0.3, f, size=11, color=NATALIA, font=MONO)
    text(s, 9.6, yy + 0.22, 2.9, 0.4, v, size=13, color=INK_2, align=PP_ALIGN.RIGHT, font=MONO)
text(s, 7.2, 6.25, 5.45, 0.5, "Trei metode, același rezultat ⇒ 7 căi liniar independente de acoperit.",
     size=11.5, color=INK_2, italic=True)

# ============================================================== 13 · PATHS
s = new_slide(13, "Testare structurală", "7 căi liniar independente, fiecare cu testul ei", "natalia", req="3")
paths = [
    ("P1", "N1 → N2", "quota = 0", "ValueError", RED),
    ("P2", "N1 → N3 → N4", "tier = VIP", "GRANTED_VIP", GREEN),
    ("P3", "N1 → N3 → N5 → N6", "CONTRACTOR, ora 21", "DENIED_RESTRICTED_HOURS", RED),
    ("P4", "… → N5 → N7 → N8", "EV, stație liberă, ora 6", "GRANTED_EV_CHARGING", GREEN),
    ("P5", "… → N7 → N9 → N10", "occupied 5 / quota 10", "GRANTED_REGULAR", GREEN),
    ("P6", "… → N9 → N11 → N12", "12 / 10, overflow, ora 10", "GRANTED_PAID_OVERFLOW", AMBER),
    ("P7", "… → N9 → N11 → N13", "10 / 10, fără overflow", "DENIED_QUOTA_EXCEEDED", RED),
]
rows = [["Cale", "Secvență de noduri", "Date de test", "Rezultat"]] + [[p[0], p[1], p[2], p[3]] for p in paths]
colors = {(i, 3): p[4] for i, p in enumerate(paths, start=1)}
colors.update({(i, 0): NATALIA for i in range(1, 8)})
table(s, 0.7, 1.6, 11.95, rows, [0.9, 3.6, 3.65, 3.8], row_h=0.5, size=12, colors=colors,
      bolds={(i, j): True for i in range(1, 8) for j in (0, 3)}, fonts={1: MONO, 3: MONO})
card(s, 0.7, 5.75, 11.95, 0.95, fill=NATALIA_L)
text(s, 1.0, 5.9, 11.4, 0.7,
     [[{"t": "De ce 7?  ", "bold": True, "color": NATALIA},
       "Fiecare cale adaugă cel puțin un arc nou. Împreună acoperă toate cele 19 arce ale grafului, "
       "iar orice altă cale prin program se poate scrie ca o combinație a acestora."]], size=12, color=INK_2)

# ============================================================== 14 · MC/DC
s = new_slide(14, "Testare structurală", "MC/DC pe decizia de acces la stația EV", "natalia", req="4")
card(s, 0.7, 1.5, 11.95, 0.85, fill=PANEL)
text(s, 0.95, 1.6, 7.0, 0.65,
     [[{"t": "D = (", "font": MONO}, {"t": "A", "font": MONO, "bold": True, "color": VICTOR},
       {"t": " ∧ ", "font": MONO}, {"t": "B", "font": MONO, "bold": True, "color": NATALIA},
       {"t": ") ∧ (¬", "font": MONO}, {"t": "C", "font": MONO, "bold": True, "color": AMBER},
       {"t": " ∨ ", "font": MONO}, {"t": "D", "font": MONO, "bold": True, "color": RED},
       {"t": ")", "font": MONO}]], size=22, color=INK, anchor=MSO_ANCHOR.MIDDLE)
text(s, 7.4, 1.62, 5.1, 0.65,
     [[{"t": "A", "bold": True, "color": VICTOR}, " vehicul electric   ", {"t": "B", "bold": True, "color": NATALIA},
       " stație liberă"],
      [{"t": "C", "bold": True, "color": AMBER}, " ore de vârf   ", {"t": "D", "bold": True, "color": RED},
       " ocupate < cotă"]], size=11.5, color=INK_2)

mcdc_tests = [
    ("T1", "1", "1", "0", "0", "1", "Bază comună (acces EV aprobat)"),
    ("T2", "0", "1", "0", "0", "0", "A este 0  ⇒  acces refuzat"),
    ("T3", "1", "0", "0", "0", "0", "B este 0  ⇒  fără stație liberă"),
    ("T4", "1", "1", "1", "0", "0", "C este 1  ⇒  vârf, ¬C este 0"),
    ("T5", "1", "1", "1", "1", "1", "D este 1  ⇒  sub cotă, resuscitează OR"),
]
rows = [["Test", "A", "B", "C", "D", "Dec.", "Justificare independență"]]
fills, colors, bolds = {}, {}, {}
for idx, (t, a, b, c, d, dec, desc) in enumerate(mcdc_tests, start=1):
    rows.append([t, a, b, c, d, dec, desc])
    fills[(idx, None)] = NATALIA_L if idx % 2 == 1 else WHITE
    colors[(idx, 0)] = NATALIA
    bolds[(idx, 0)] = True
    bolds[(idx, 5)] = True
    colors[(idx, 5)] = GREEN if dec == "1" else RED
    colors[(idx, 6)] = INK_2

table(s, 0.7, 2.55, 4.75, rows, [0.65, 0.42, 0.42, 0.42, 0.42, 0.55, 1.87], row_h=0.46, size=9.5, head_size=9.5,
      fills=fills, colors=colors, bolds=bolds, aligns={0: PP_ALIGN.CENTER, 1: PP_ALIGN.CENTER, 2: PP_ALIGN.CENTER,
                                                        3: PP_ALIGN.CENTER, 4: PP_ALIGN.CENTER, 5: PP_ALIGN.CENTER,
                                                        6: PP_ALIGN.LEFT}, zebra=None)

card(s, 0.7, 5.25, 4.75, 1.6, fill=PANEL)
text(s, 0.9, 5.4, 4.35, 0.3, "De la 16 combinații la 5 teste", size=12, color=INK, bold=True)
text(s, 0.9, 5.75, 4.35, 1.0,
     "Tabelul exhaustiv are 2⁴ = 16 combinații (prezentate în raport). "
     "MC/DC demonstrează independența fiecărei variabile atomice cu doar N + 1 = 5 teste "
     "selectate riguros, reducând efortul de testare cu 69% și garantând decizia fără redundanță.",
     size=10, color=MUTED)

text(s, 5.75, 2.55, 6.8, 0.3, "PERECHI DE INDEPENDENȚĂ — se schimbă o singură condiție, se schimbă decizia",
     size=10.5, color=MUTED, bold=True)
pairs = [("A", VICTOR, "T1", "1 1 0 0", "T2", "0 1 0 0"),
         ("B", NATALIA, "T1", "1 1 0 0", "T3", "1 0 0 0"),
         ("C", AMBER, "T1", "1 1 0 0", "T4", "1 1 1 0"),
         ("D", RED, "T5", "1 1 1 1", "T4", "1 1 1 0")]
for i, (cond, c, t1, v1, t2, v2) in enumerate(pairs):
    yy = 2.95 + i * 0.86
    card(s, 5.75, yy, 6.9, 0.72, fill=WHITE, line=LINE)
    pill(s, 5.95, yy + 0.18, 0.5, 0.36, cond, fill=c, size=12)
    text(s, 6.7, yy + 0.2, 2.3, 0.35, [[{"t": t1 + "  ", "bold": True}, {"t": v1, "font": MONO}, "  → 1"]],
         size=12, color=INK)
    arrow(s, 9.0, yy + 0.36, 9.45, yy + 0.36, color=c, width=1.5)
    text(s, 9.6, yy + 0.2, 2.9, 0.35, [[{"t": t2 + "  ", "bold": True}, {"t": v2, "font": MONO}, "  → 0"]],
         size=12, color=INK)
card(s, 5.75, 6.4, 6.9, 0.45, fill=NATALIA)
text(s, 5.95, 6.45, 6.6, 0.35, "N = 4 condiții  ⇒  N + 1 = 5 teste  ·  tests/test_mcdc.py  ·  5/5 trec",
     size=12, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================== 15 · DIVIDER III
divider(15, "Partea III · Echipa", "Testare prin mutații", "team",
        [("5", "Un mutant de ordin 1 echivalent — și de ce nu poate fi ucis", "victor"),
         ("6", "Doi mutanți ne-echivalenți: unul ucis, unul supraviețuitor", "natalia"),
         ("7", "Generare automată cu mutmut și cosmic-ray", "natalia")])

# ============================================================== 16 · EQUIVALENT MUTANT
s = new_slide(16, "Testare prin mutații", "Mutant de ordin 1 echivalent", "victor", req="5")
code_block(s, 0.7, 1.6, 6.3, 1.3, [
    ("# src/parking_gate.py, linia 57", "dim"),
    ("- is_peak_hours = (8 <= entry_hour <= 17)", "del"),
    ("+ is_peak_hours = (7 < entry_hour < 18)", "add"),
], size=12, line_h=0.32)
text(s, 0.7, 3.1, 6.3, 0.3, "DEMONSTRAȚIE", size=10.5, color=MUTED, bold=True)
steps = [("1", "entry_hour este de tip int, deci h ∈ ℤ."),
         ("2", "Pe ℤ:  h ≥ 8 ⇔ h > 7   și   h ≤ 17 ⇔ h < 18."),
         ("3", "Deci is_peak_hours are aceeași valoare pentru orice h, iar restul codului e identic."),
         ("∴", "M(x) = P(x) pentru orice intrare x — niciun test nu poate ucide mutantul.")]
for i, (k, t) in enumerate(steps):
    yy = 3.5 + i * 0.78
    last = k == "∴"
    pill(s, 0.7, yy + 0.06, 0.45, 0.45, k, fill=VICTOR if not last else INK, size=13)
    text(s, 1.35, yy + 0.08, 5.6, 0.6, t, size=13, color=INK if last else INK_2, bold=last)

card(s, 7.45, 1.6, 5.2, 2.6, fill=VICTOR_L)
text(s, 7.75, 1.8, 4.7, 0.3, "VERIFICARE EXHAUSTIVĂ", size=10.5, color=VICTOR, bold=True)
text(s, 7.75, 2.15, 4.7, 0.9, "1 152", size=48, color=VICTOR, bold=True)
text(s, 7.75, 3.05, 4.7, 1.0, "comparații original vs. mutant, toate identice\n24 ore × 3 roluri × 2³ combinații bool × 2 niveluri de ocupare",
     size=11, color=INK_2)
card(s, 7.45, 4.45, 5.2, 2.3, fill=WHITE, line=LINE)
text(s, 7.75, 4.65, 4.7, 2.0,
     [[{"t": "De ce contează", "bold": True, "size": 13}],
      "Un mutant echivalent rămâne „viu” oricât de bune ar fi testele.",
      "Scorul de mutație brut îl numără totuși ca eșec — de aceea mutanții echivalenți se exclud din numitor."],
     size=11.5, color=INK_2, spacing=6)

# ============================================================== 17 · KILLED VS SURVIVED
s = new_slide(17, "Testare prin mutații", "Același test, doi mutanți, două destine", "natalia", req="6")
card(s, 0.7, 1.55, 11.95, 1.0, fill=PANEL)
text(s, 0.95, 1.65, 3.0, 0.3, "TESTUL ALES (din BVA)", size=10, color=MUTED, bold=True)
text(s, 0.95, 1.95, 6.0, 0.4, "test_bva_occupied_exactly_at_quota", size=13, color=INK, bold=True, font=MONO)
text(s, 7.0, 1.68, 5.5, 0.8,
     ["quota = 10 · occupied = 10 · ora 12 · REGULAR", "fără EV · allows_overflow = False"],
     size=11.5, color=INK_2, font=MONO)
text(s, 10.0, 2.02, 2.5, 0.4, "", size=1)

for col, spec in enumerate([
    dict(title="Mutant #1 — UCIS", color=GREEN, light=GREEN_L, op="ROR: < devine ≤",
         code=[("- within = occupied < quota", "del"), ("+ within = occupied <= quota", "add")],
         trace=["10 <= 10 este True", "funcția returnează GRANTED_REGULAR",
                "testul așteaptă DENIED_QUOTA_EXCEEDED", "aserțiunea pică ⇒ mutant detectat"]),
    dict(title="Mutant #2 — SUPRAVIEȚUIEȘTE", color=AMBER, light=AMBER_L, op="constantă: 5 devine 4",
         code=[("- ... (not is_peak or overflow < 5)", "del"), ("+ ... (not is_peak or overflow < 4)", "add")],
         trace=["allows_overflow = False", "`False and …` se scurtcircuitează",
                "pragul mutat nu este evaluat niciodată", "rezultat identic ⇒ testul nu vede mutația"]),
]):
    xx = 0.7 + col * 6.1
    card(s, xx, 2.8, 5.85, 3.95, fill=WHITE, line=LINE)
    box(s, xx, 2.8, 5.85, 0.08, fill=spec["color"])
    text(s, xx + 0.25, 3.02, 4.0, 0.4, spec["title"], size=16, color=spec["color"], bold=True)
    pill(s, xx + 3.75, 3.04, 1.9, 0.32, spec["op"], fill=spec["light"], color=spec["color"], size=9.5)
    code_block(s, xx + 0.25, 3.55, 5.35, 0.9, spec["code"], size=10.5, line_h=0.3)
    for k, t in enumerate(spec["trace"]):
        yy = 4.65 + k * 0.48
        box(s, xx + 0.32, yy + 0.08, 0.16, 0.16, fill=spec["color"], shape=MSO_SHAPE.OVAL)
        if k < 3:
            arrow(s, xx + 0.4, yy + 0.24, xx + 0.4, yy + 0.56, color=LINE, width=1.25, head=False)
        text(s, xx + 0.65, yy + 0.02, 5.0, 0.35, t, size=12, color=INK_2 if k < 3 else INK, bold=(k == 3))

# ============================================================== 18 · TOOLS
s = new_slide(18, "Testare prin mutații", "mutmut vs. cosmic-ray pe trei seturi de teste", "natalia", req="7")
suites = [("functional", "Cerința 1"), ("mcdc", "Cerința 4"), ("combined", "1 + 4")]
cd = CategoryChartData()
cd.categories = [lbl for _, lbl in suites]
cd.add_series("mutmut", [MUT["mutmut"][k]["score"] for k, _ in suites])
cd.add_series("cosmic-ray", [MUT["cosmic_ray"][k]["score"] for k, _ in suites])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.5), Inches(6.0), Inches(3.55), cd)
ch = gf.chart
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.TOP
ch.legend.include_in_layout = False
ch.legend.font.size = Pt(11)
va = ch.value_axis
va.maximum_scale = 100
va.minimum_scale = 0
va.major_unit = 25
va.major_gridlines.format.line.color.rgb = LINE
va.tick_labels.font.size = Pt(10)
va.tick_labels.font.color.rgb = MUTED
va.format.line.fill.background()
ch.category_axis.tick_labels.font.size = Pt(11)
ch.category_axis.format.line.color.rgb = LINE
plot = ch.plots[0]
plot.gap_width = 70
plot.overlap = -10
plot.has_data_labels = True
plot.data_labels.number_format = '0"%"'
plot.data_labels.number_format_is_linked = False
plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
plot.data_labels.font.size = Pt(10.5)
plot.data_labels.font.bold = True
for ser, c in zip(plot.series, (NATALIA, rgb("A9A2EE"))):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = c

rows = [["Set de teste", "mutmut  ucis / total", "cosmic-ray  ucis / total"]]
for k, lbl in suites:
    m, c = MUT["mutmut"][k], MUT["cosmic_ray"][k]
    rows.append([lbl, f"{m['killed']} / {m['total']}", f"{c['killed']} / {c['total']}"])
table(s, 0.7, 5.25, 5.9, rows, [1.7, 2.1, 2.1], row_h=0.36, size=11,
      aligns={1: PP_ALIGN.CENTER, 2: PP_ALIGN.CENTER}, fonts={1: MONO, 2: MONO})

notes = MUT["notes"]
for i, (ttl, body, c) in enumerate([
    ("Operatori diferiți", notes["operators"], NATALIA),
    ("Ce supraviețuiește", notes["survivors"], AMBER),
    ("Cerința 1 vs. Cerința 4", notes["suites"], VICTOR),
]):
    yy = 1.55 + i * 1.75
    card(s, 7.0, yy, 5.65, 1.6, fill=WHITE, line=LINE, accent=c)
    text(s, 7.3, yy + 0.15, 5.2, 0.3, ttl, size=13.5, color=INK, bold=True)
    text(s, 7.3, yy + 0.5, 5.2, 1.05, body, size=10.5, color=INK_2)

# ============================================================== 19 · CONCLUSIONS
s = new_slide(19, "Concluzii", "Ce am obținut și ce am învățat", "team")
kpis = [("80", "teste, toate trec"), ("100%", "ramuri acoperite (EP)"), ("7", "căi independente"),
        (f"{MUT['mutmut']['combined']['score']:.0f}%", "scor mutmut, set combinat")]
for i, (big, small) in enumerate(kpis):
    xx = 0.7 + i * 3.04
    card(s, xx, 1.55, 2.84, 1.35, fill=PANEL)
    text(s, xx + 0.25, 1.65, 2.4, 0.7, big, size=32, color=INK, bold=True)
    text(s, xx + 0.25, 2.38, 2.4, 0.4, small, size=11.5, color=MUTED)
lessons = [
    ("Tehnicile se completează", "BVA prinde erorile off-by-one, CEG combinațiile logice, EP domeniile uitate.", VICTOR),
    ("Acoperirea nu e suficientă", "100% ramuri nu garantează că un < nu a devenit ≤ — mutațiile o arată.", NATALIA),
    ("Scurtcircuitarea ascunde defecte", "O condiție evaluată leneș poate face un test „orb” la o mutație.", AMBER),
]
for i, (t, b, c) in enumerate(lessons):
    yy = 3.15 + i * 0.95
    card(s, 0.7, yy, 7.4, 0.8, fill=WHITE, line=LINE, accent=c)
    text(s, 1.0, yy + 0.1, 7.0, 0.3, t, size=13, color=INK, bold=True)
    text(s, 1.0, yy + 0.42, 7.0, 0.35, b, size=11, color=INK_2)
card(s, 8.4, 3.15, 4.25, 2.7, fill=INK)
text(s, 8.7, 3.32, 3.8, 2.4,
     [[{"t": "Utilizare AI", "bold": True, "size": 13, "color": WHITE}],
      "Asistentul Antigravity a fost folosit pentru schelet de cod, teste și documentație.",
      "Prompturile, rezultatele și verificările sunt documentate în AI_USAGE_LAB.md, conform cerinței."],
     size=11, color=rgb("C9D4E0"), spacing=6)
text(s, 0.7, 6.2, 11.95, 0.4,
     [[{"t": "Cod, teste, documentație: ", "bold": True}, {"t": "github.com/victormura/tss", "font": MONO},
       "   ·   ", {"t": "Întrebări?", "bold": True, "color": NATALIA}]], size=13, color=INK_2)

prs.save(OUT_PPTX)
print("saved", OUT_PPTX, "slides:", len(prs.slides))
