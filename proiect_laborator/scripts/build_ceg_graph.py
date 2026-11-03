"""
Generează graful cauză-efect în trei formate din aceeași specificație geometrică:
  - docs/CEG_Drawio.drawio   (editabil în draw.io / diagrams.net)
  - docs/img/ceg_graph.svg   (vectorial)
  - docs/img/ceg_graph.png   (2x Retina, folosit în prezentare și în raportul PDF)

Notații:
  - cercuri C1..C8 pentru cauze, cercuri 1..3 pentru nodurile intermediare, cercuri Ef1..Ef6 pentru efecte
  - undă (~) transversală pe arcele negate
  - arc de cerc cu simbolul ∧ sau ∨ pe intrările fiecărui nod conjuncție/disjuncție
  - E cu linii punctate între C1 și C2 (exclusivitate)
  - M cu arce punctate între efectele care maschează efecte evaluate ulterior
"""

import html
import math
import os

from PIL import Image, ImageDraw, ImageFont
from lab_data import CAUSES, EFFECTS

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(os.path.dirname(HERE), "docs")
IMG = os.path.join(DOCS, "img")
os.makedirs(IMG, exist_ok=True)

WIDTH, HEIGHT = 1280, 660
CX = 305          # centrul cercurilor C1..C8
EX = 830          # centrul cercurilor Ef1..Ef6
RC = 22           # raza cercurilor C și Ef
RN = 18           # raza nodurilor intermediare 1..3

cause_y = {
    "C1": 55,
    "C2": 130,
    "C3": 205,
    "C4": 275,
    "C5": 340,
    "C6": 410,
    "C7": 495,
    "C8": 585,
}
effect_y = {
    "Ef1": 55,
    "Ef2": 145,
    "Ef3": 250,
    "Ef4": 395,
    "Ef5": 495,
    "Ef6": 595,
}

# Noduri intermediare numerotate 1, 2, 3 (fără prefixul I, care desemnează clasele de ieșire I1..I7):
#   1 = ¬C3 ∨ C6       (fereastră validă pentru încărcare EV)
#   2 = ¬C3 ∨ C8       (fereastră validă pentru overflow)
#   3 = C7 ∧ nodul_2   (condiție overflow aprobat)
nodes = {
    "1": (520, 368, "∨"),
    "2": (510, 565, "∨"),
    "3": (660, 480, "∧"),
}
effect_op = {"Ef2": "∧", "Ef3": "∧", "Ef5": "∧", "Ef6": "∧"}

# (sursă, destinație, negat, poziție_t_pentru_undă)
EDGES = [
    ("C1", "Ef1", False, 0.50),
    ("C2", "Ef2", False, 0.50),
    ("C3", "Ef2", True, 0.55),
    ("C3", "1", True, 0.72),
    ("C6", "1", False, 0.50),
    ("C4", "Ef3", False, 0.50),
    ("C5", "Ef3", False, 0.50),
    ("1", "Ef3", False, 0.50),
    ("C6", "Ef4", False, 0.50),
    ("C3", "2", True, 0.82),
    ("C8", "2", False, 0.50),
    ("C7", "3", False, 0.50),
    ("2", "3", False, 0.50),
    ("C6", "Ef5", True, 0.42),
    ("3", "Ef5", False, 0.50),
    ("C6", "Ef6", True, 0.26),
    ("3", "Ef6", True, 0.55),
]

EFF_COLOR = {
    "Ef1": ("#1F9D57", "#E4F5EA"),
    "Ef2": ("#D64545", "#FBE7E7"),
    "Ef3": ("#1F9D57", "#E4F5EA"),
    "Ef4": ("#1F9D57", "#E4F5EA"),
    "Ef5": ("#D98A0B", "#FDF1DC"),
    "Ef6": ("#D64545", "#FBE7E7"),
}


def center_and_r(n):
    if n.startswith("C"):
        return CX, cause_y[n], RC
    if n.startswith("Ef"):
        return EX, effect_y[n], RC
    x, y, _ = nodes[n]
    return x, y, RN


def segment(src, dst):
    x1, y1, r1 = center_and_r(src)
    x2, y2, r2 = center_and_r(dst)
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    return (x1 + ux * r1, y1 + uy * r1), (x2 - ux * r2, y2 - uy * r2), (ux, uy)


def gate_angles(dst):
    """Returnează unghiurile (în jurul direcției stânga = π) ale muchiilor care intră în `dst`."""
    cx, cy, r = center_and_r(dst)
    inc = [s for s, d, _, _ in EDGES if d == dst]
    offs = []
    for s in inc:
        sx, sy, _ = center_and_r(s)
        # unghi față de semiaxa stângă (-X): 0 = direct din stânga, >0 = de sus, <0 = de jos
        offs.append(math.atan2(cy - sy, cx - sx))
    return cx, cy, r, min(offs), max(offs)


def wave_points(x1, y1, x2, y2, ux, uy, t=0.55, n=28):
    mx, my = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
    px, py = -uy, ux
    pts = []
    span, amp = 11.0, 6.5
    for i in range(n + 1):
        u = (i / n) * 2 - 1  # -1 .. +1
        along = u * span
        perp = math.sin(u * math.pi) * amp
        pts.append((mx + ux * along + px * perp, my + uy * along + py * perp))
    return pts


# ------------------------------------------------------------------ SVG
def build_svg():
    o = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Helvetica Neue, Helvetica, Arial, sans-serif">',
        '<defs>'
        '<marker id="arr" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto">'
        '<path d="M0,0 L8,3.5 L0,7 z" fill="#2C3E50"/></marker>'
        '<marker id="marr" markerWidth="8" markerHeight="7" refX="7" refY="3.5" orient="auto">'
        '<path d="M0,0 L8,3.5 L0,7 z" fill="#B45309"/></marker>'
        '</defs>',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    ex, ey = 230, (cause_y["C1"] + cause_y["C2"]) / 2
    for cid in ("C1", "C2"):
        o.append(f'<line x1="{ex}" y1="{ey}" x2="{CX - RC}" y2="{cause_y[cid]}" '
                 f'stroke="#D64545" stroke-width="1.6" stroke-dasharray="5,4"/>')
    o.append(f'<text x="{ex - 12}" y="{ey + 5}" font-size="16" font-weight="700" fill="#D64545" '
             f'text-anchor="middle">E</text>')

    for s, d, neg, t in EDGES:
        (x1, y1), (x2, y2), (ux, uy) = segment(s, d)
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="#2C3E50" stroke-width="1.6" marker-end="url(#arr)"/>')
        if neg:
            pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in wave_points(x1, y1, x2, y2, ux, uy, t))
            o.append(f'<polyline points="{pts}" fill="none" stroke="#D64545" stroke-width="2.2"/>')

    for dst, op in [(k, v[2]) for k, v in nodes.items()] + list(effect_op.items()):
        cx, cy, r, o1, o2 = gate_angles(dst)
        ar = r + 18
        p1x, p1y = cx - ar * math.cos(o1), cy - ar * math.sin(o1)
        p2x, p2y = cx - ar * math.cos(o2), cy - ar * math.sin(o2)
        om = (o1 + o2) / 2
        tx, ty = cx - (ar + 13) * math.cos(om), cy - (ar + 13) * math.sin(om) + 5
        o.append(f'<path d="M {p1x:.1f},{p1y:.1f} A {ar},{ar} 0 0,1 {p2x:.1f},{p2y:.1f}" '
                 f'fill="none" stroke="#1E3A5F" stroke-width="1.6"/>'
                 f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="15" font-weight="700" fill="#1E3A5F" '
                 f'text-anchor="middle">{op}</text>')

    for cid, lbl in CAUSES:
        y = cause_y[cid]
        o.append(f'<circle cx="{CX}" cy="{y}" r="{RC}" fill="#ECEAFB" stroke="#5B4FD6" stroke-width="1.8"/>'
                 f'<text x="{CX}" y="{y + 5}" font-size="14" font-weight="700" fill="#0F1B2D" '
                 f'text-anchor="middle">{cid}</text>'
                 f'<text x="{CX - RC - 14}" y="{y + 5}" font-size="13.5" fill="#0F1B2D" '
                 f'text-anchor="end">{html.escape(lbl)}</text>')

    for nid, (x, y, _) in nodes.items():
        o.append(f'<circle cx="{x}" cy="{y}" r="{RN}" fill="white" stroke="#0F1B2D" stroke-width="1.8"/>'
                 f'<text x="{x}" y="{y + 5}" font-size="14" font-weight="700" fill="#0F1B2D" '
                 f'text-anchor="middle">{nid}</text>')

    for eid, name, _ in EFFECTS:
        y = effect_y[eid]
        fg, bg = EFF_COLOR[eid]
        o.append(f'<circle cx="{EX}" cy="{y}" r="{RC}" fill="{bg}" stroke="{fg}" stroke-width="1.8"/>'
                 f'<text x="{EX}" y="{y + 5}" font-size="13.5" font-weight="700" fill="{fg}" '
                 f'text-anchor="middle">{eid}</text>'
                 f'<rect x="{EX + RC + 12}" y="{y - 16}" width="235" height="32" rx="6" fill="{bg}" stroke="{fg}" stroke-width="1"/>'
                 f'<text x="{EX + RC + 22}" y="{y + 5}" font-size="12.5" font-weight="700" fill="{fg}" '
                 f'font-family="Menlo, monospace">{name}</text>')

    bx = EX + RC + 255
    for src, dst, bulge in [("Ef1", "Ef3", 40), ("Ef2", "Ef3", 22), ("Ef3", "Ef4", 26)]:
        y1, y2 = effect_y[src], effect_y[dst]
        ym = (y1 + y2) / 2
        cx_ = bx + bulge
        o.append(f'<path d="M {bx - 6},{y1} Q {cx_},{ym} {bx - 6},{y2}" fill="none" '
                 f'stroke="#B45309" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#marr)"/>'
                 f'<text x="{cx_ + 4}" y="{ym + 5}" font-size="13" font-weight="700" fill="#B45309">M</text>')
    o.append("</svg>")
    return "\n".join(o)


# ------------------------------------------------------------------ PNG (Pillow, 2x Retina)
def load_font(size, bold=False, mono=False):
    candidates = (
        ["/System/Library/Fonts/Menlo.ttc"] if mono else
        ["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"]
    )
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size, index=(1 if bold and p.endswith(".ttc") else 0))
            except Exception:
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_dashed_line(drw, p1, p2, color, width=3, dash=10, gap=8):
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    if d == 0:
        return
    ux, uy = dx / d, dy / d
    pos = 0.0
    while pos < d:
        end = min(pos + dash, d)
        drw.line([(x1 + ux * pos, y1 + uy * pos), (x1 + ux * end, y1 + uy * end)], fill=color, width=width)
        pos += dash + gap


def draw_arrow_head(drw, tip, ux, uy, color, size=14):
    tx, ty = tip
    px, py = -uy, ux
    bx, by = tx - ux * size, ty - uy * size
    w = size * 0.48
    drw.polygon([(tx, ty), (bx + px * w, by + py * w), (bx - px * w, by - py * w)], fill=color)


def build_png(out_path, scale=2):
    S = lambda v: v * scale
    img = Image.new("RGB", (S(WIDTH), S(HEIGHT)), "white")
    drw = ImageDraw.Draw(img)

    f_lbl = load_font(S(14), bold=False)
    f_node = load_font(S(14), bold=True)
    f_op = load_font(S(16), bold=True)
    f_mono = load_font(S(12), bold=True, mono=True)
    f_note = load_font(S(12), bold=False)

    # 1. E(C1, C2)
    ex, ey = 230, (cause_y["C1"] + cause_y["C2"]) / 2
    for cid in ("C1", "C2"):
        draw_dashed_line(drw, (S(ex), S(ey)), (S(CX - RC), S(cause_y[cid])), "#D64545", width=S(2))
    drw.text((S(ex - 14), S(ey)), "E", fill="#D64545", font=f_op, anchor="mm")

    # 2. Muchii + săgeți + undă negație
    for s, d, neg, t in EDGES:
        (x1, y1), (x2, y2), (ux, uy) = segment(s, d)
        drw.line([(S(x1), S(y1)), (S(x2 - ux * 5), S(y2 - uy * 5))], fill="#2C3E50", width=S(2))
        draw_arrow_head(drw, (S(x2), S(y2)), ux, uy, "#2C3E50", size=S(11))
        if neg:
            pts = [(S(px), S(py)) for px, py in wave_points(x1, y1, x2, y2, ux, uy, t)]
            drw.line(pts, fill="#D64545", width=S(3))

    # 3. Arcele ∧ / ∨ în stânga nodurilor
    for dst, op in [(k, v[2]) for k, v in nodes.items()] + list(effect_op.items()):
        cx, cy, r, o1, o2 = gate_angles(dst)
        ar = r + 18
        arc_pts = []
        steps = 24
        for i in range(steps + 1):
            ang = o1 + (o2 - o1) * (i / steps)
            arc_pts.append((S(cx - ar * math.cos(ang)), S(cy - ar * math.sin(ang))))
        drw.line(arc_pts, fill="#1E3A5F", width=S(2))
        om = (o1 + o2) / 2
        tx, ty = cx - (ar + 14) * math.cos(om), cy - (ar + 14) * math.sin(om)
        dx_op, dy_op = 5.0, 5.5
        if op == "∧":
            drw.line([(S(tx - dx_op), S(ty + dy_op)), (S(tx), S(ty - dy_op)), (S(tx + dx_op), S(ty + dy_op))],
                     fill="#1E3A5F", width=S(2))
        else:
            drw.line([(S(tx - dx_op), S(ty - dy_op)), (S(tx), S(ty + dy_op)), (S(tx + dx_op), S(ty - dy_op))],
                     fill="#1E3A5F", width=S(2))

    # 4. Cauze C1..C8
    for cid, lbl in CAUSES:
        y = cause_y[cid]
        drw.ellipse([S(CX - RC), S(y - RC), S(CX + RC), S(y + RC)], fill="#ECEAFB", outline="#5B4FD6", width=S(2))
        drw.text((S(CX), S(y)), cid, fill="#0F1B2D", font=f_node, anchor="mm")
        drw.text((S(CX - RC - 12), S(y)), lbl, fill="#0F1B2D", font=f_lbl, anchor="rm")

    # 5. Noduri intermediare 1..3
    for nid, (x, y, _) in nodes.items():
        drw.ellipse([S(x - RN), S(y - RN), S(x + RN), S(y + RN)], fill="white", outline="#0F1B2D", width=S(2))
        drw.text((S(x), S(y)), nid, fill="#0F1B2D", font=f_node, anchor="mm")

    # 6. Efecte Ef1..Ef6
    for eid, name, _ in EFFECTS:
        y = effect_y[eid]
        fg, bg = EFF_COLOR[eid]
        drw.ellipse([S(EX - RC), S(y - RC), S(EX + RC), S(y + RC)], fill=bg, outline=fg, width=S(2))
        drw.text((S(EX), S(y)), eid, fill=fg, font=f_node, anchor="mm")
        rx1, ry1, rx2, ry2 = EX + RC + 12, y - 16, EX + RC + 252, y + 16
        drw.rounded_rectangle([S(rx1), S(ry1), S(rx2), S(ry2)], radius=S(6), fill=bg, outline=fg, width=S(2))
        drw.text((S(rx1 + 10), S(y)), name, fill=fg, font=f_mono, anchor="lm")

    # 7. Constrângeri de mascare M între efecte
    bx = EX + RC + 258
    for src, dst, bulge in [("Ef1", "Ef3", 46), ("Ef2", "Ef3", 24), ("Ef3", "Ef4", 28)]:
        y1, y2 = effect_y[src], effect_y[dst]
        ym = (y1 + y2) / 2
        cx_ = bx + bulge
        pts = []
        for i in range(25):
            u = i / 24
            px = (1 - u) ** 2 * bx + 2 * (1 - u) * u * cx_ + u ** 2 * bx
            py = (1 - u) ** 2 * y1 + 2 * (1 - u) * u * ym + u ** 2 * y2
            pts.append((px, py))
        for i in range(0, len(pts) - 1, 2):
            drw.line([(S(pts[i][0]), S(pts[i][1])), (S(pts[i + 1][0]), S(pts[i + 1][1]))], fill="#B45309", width=S(2))
        ux, uy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        d = math.hypot(ux, uy)
        draw_arrow_head(drw, (S(bx), S(y2)), ux / d, uy / d, "#B45309", size=S(10))
        drw.text((S((bx + cx_) / 2 + 8), S(ym)), "M", fill="#B45309", font=f_node, anchor="lm")

    drw.text((S(bx + 6), S(effect_y["Ef5"] - 6)), "M(Ef1, Ef3..Ef6)", fill="#6B7A8F", font=f_note, anchor="lm")
    drw.text((S(bx + 6), S(effect_y["Ef5"] + 14)), "M(Ef2, Ef3..Ef6)", fill="#6B7A8F", font=f_note, anchor="lm")
    drw.text((S(bx + 6), S(effect_y["Ef5"] + 34)), "M(Ef3, Ef4..Ef6)", fill="#6B7A8F", font=f_note, anchor="lm")

    img.save(out_path, "PNG")


# ------------------------------------------------------------------ draw.io
def build_drawio():
    cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>']

    def v(cid, value, x, y, w, h, style):
        cells.append(f'<mxCell id="{cid}" value="{html.escape(value)}" style="{style}" vertex="1" parent="1">'
                     f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    def e(eid, src, dst, value="", style=""):
        cells.append(f'<mxCell id="{eid}" value="{html.escape(value)}" style="endArrow=block;html=1;'
                     f'strokeColor=#2C3E50;fontColor=#D64545;fontStyle=1;fontSize=15;{style}" edge="1" '
                     f'parent="1" source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry"/></mxCell>')

    for cid, lbl in CAUSES:
        y = cause_y[cid]
        v(f"lbl_{cid}", lbl, 15, y - 15, CX - RC - 25, 30,
          "text;html=1;align=right;verticalAlign=middle;fontSize=13;fontColor=#0F1B2D;")
        v(cid, cid, CX - RC, y - RC, 2 * RC, 2 * RC,
          "ellipse;whiteSpace=wrap;html=1;fillColor=#ECEAFB;strokeColor=#5B4FD6;fontStyle=1;fontSize=13;")
    for eid, name, _ in EFFECTS:
        y = effect_y[eid]
        fg, bg = EFF_COLOR[eid]
        v(eid, eid, EX - RC, y - RC, 2 * RC, 2 * RC,
          f"ellipse;whiteSpace=wrap;html=1;fillColor={bg};strokeColor={fg};fontColor={fg};fontStyle=1;fontSize=13;")
        v(f"lbl_{eid}", name, EX + RC + 12, y - 16, 235, 32,
          f"rounded=1;whiteSpace=wrap;html=1;fillColor={bg};strokeColor={fg};fontColor={fg};fontFamily=Menlo;"
          "align=left;spacingLeft=8;fontStyle=1;fontSize=12;")
        if eid in effect_op:
            v(f"op_{eid}", effect_op[eid], EX - RC - 28, y - 24, 22, 20,
              "text;html=1;fontSize=15;fontStyle=1;fontColor=#1E3A5F;align=center;")
    for nid, (x, y, op) in nodes.items():
        v(f"N{nid}", nid, x - RN, y - RN, 2 * RN, 2 * RN,
          "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0F1B2D;fontStyle=1;fontSize=13;")
        v(f"op_N{nid}", op, x - RN - 26, y - 22, 22, 20,
          "text;html=1;fontSize=15;fontStyle=1;fontColor=#1E3A5F;align=center;")
    ids = lambda n: n if not n.isdigit() else f"N{n}"
    for i, (s, d, neg, _) in enumerate(EDGES):
        e(f"e{i}", ids(s), ids(d), "~" if neg else "")
    v("E", "E", 205, (cause_y["C1"] + cause_y["C2"]) / 2 - 12, 24, 24,
      "text;html=1;fontSize=15;fontStyle=1;fontColor=#D64545;align=center;")
    for c in ("C1", "C2"):
        e(f"eE{c}", "E", c, "", "dashed=1;endArrow=none;strokeColor=#D64545;")
    for idx, (src, dst) in enumerate([("Ef1", "Ef3"), ("Ef2", "Ef3"), ("Ef3", "Ef4")]):
        e(f"eM{idx}", f"lbl_{src}", f"lbl_{dst}", "M",
          "dashed=1;curved=1;strokeColor=#B45309;fontColor=#B45309;exitX=1;exitY=0.5;entryX=1;entryY=0.5;")
    return ('<mxfile host="app.diagrams.net"><diagram id="ceg" name="Graf cauza-efect">'
            f'<mxGraphModel dx="1300" dy="700" grid="1" gridSize="10" page="1" pageWidth="{WIDTH}" '
            f'pageHeight="{HEIGHT}"><root>' + "".join(cells) + "</root></mxGraphModel></diagram></mxfile>")


def build_cfg_png(out_path, scale=2):
    """Generează imaginea PNG a grafului orientat de control (CFG) cu 14 noduri și 19 arce."""
    S = lambda v: v * scale
    W_C, H_C = 920, 620
    img = Image.new("RGB", (S(W_C), S(H_C)), "white")
    drw = ImageDraw.Draw(img)
    f_b = load_font(S(12), bold=True)
    f_r = load_font(S(11), bold=False)
    f_m = load_font(S(11), bold=True, mono=True)

    preds = [
        ("N1", "q ≤ 0 or o < 0 or h < 0 or h > 23"),
        ("N3", "tier == VIP"),
        ("N5", "tier == CONTRACTOR and not peak"),
        ("N7", "is_ev and has_spot and (not peak or within)"),
        ("N9", "within  (o < q)"),
        ("N11", "allows_ovf and (not peak or ovf < 5)"),
    ]
    rets = [
        ("N2", "raise ValueError", "#D64545", "#FBE7E7"),
        ("N4", "return GRANTED_VIP", "#1F9D57", "#E4F5EA"),
        ("N6", "return DENIED_RESTRICTED_HOURS", "#D64545", "#FBE7E7"),
        ("N8", "return GRANTED_EV_CHARGING", "#1F9D57", "#E4F5EA"),
        ("N10", "return GRANTED_REGULAR", "#1F9D57", "#E4F5EA"),
        ("N12", "return GRANTED_PAID_OVERFLOW", "#D98A0B", "#FDF1DC"),
    ]
    px, pw, ph = 180, 290, 54
    rx, rw, rh = 545, 275, 36
    bus_x = 865
    y0, dy = 24, 82

    drw.line([(S(bus_x), S(y0 + ph / 2)), (S(bus_x), S(y0 + 6 * dy + 22))], fill="#94A3B8", width=S(2))
    for i, ((pid, pq), (rid, rl, fg, bg)) in enumerate(zip(preds, rets)):
        yy = y0 + i * dy
        cx, cy = px, yy + ph / 2
        pts = [(S(cx - pw / 2), S(cy)), (S(cx), S(yy)), (S(cx + pw / 2), S(cy)), (S(cx), S(yy + ph))]
        drw.polygon(pts, fill="#E3F4F1", outline="#0E8C7F", width=S(2))
        drw.text((S(cx), S(cy - 8)), pid, fill="#0E8C7F", font=f_b, anchor="mm")
        drw.text((S(cx), S(cy + 8)), pq, fill="#0F1B2D", font=f_r, anchor="mm")

        # T -> return node
        drw.line([(S(cx + pw / 2), S(cy)), (S(rx - 6), S(cy))], fill="#1F9D57", width=S(2))
        draw_arrow_head(drw, (S(rx), S(cy)), 1, 0, "#1F9D57", size=S(10))
        drw.text((S(cx + pw / 2 + 16), S(cy - 10)), "T", fill="#1F9D57", font=f_b, anchor="mm")

        drw.rounded_rectangle([S(rx), S(cy - rh / 2), S(rx + rw), S(cy + rh / 2)],
                              radius=S(8), fill=bg, outline=fg, width=S(2))
        drw.text((S(rx + 10), S(cy)), f"{rid}  {rl}", fill=fg, font=f_m, anchor="lm")
        drw.line([(S(rx + rw), S(cy)), (S(bus_x), S(cy))], fill="#94A3B8", width=S(2))

        # F -> next
        ny = y0 + (i + 1) * dy
        drw.line([(S(cx), S(yy + ph)), (S(cx), S(ny - 4))], fill="#D64545", width=S(2))
        draw_arrow_head(drw, (S(cx), S(ny)), 0, 1, "#D64545", size=S(10))
        drw.text((S(cx + 14), S(yy + ph + 12)), "F", fill="#D64545", font=f_b, anchor="mm")

    # N13
    y13 = y0 + 6 * dy
    drw.rounded_rectangle([S(px - 135), S(y13), S(px + 135), S(y13 + 38)],
                          radius=S(8), fill="#FBE7E7", outline="#D64545", width=S(2))
    drw.text((S(px), S(y13 + 19)), "N13  return DENIED_QUOTA_EXCEEDED", fill="#D64545", font=f_m, anchor="mm")
    drw.line([(S(px + 135), S(y13 + 19)), (S(bus_x), S(y13 + 19))], fill="#94A3B8", width=S(2))

    # N14
    y14 = y13 + 56
    drw.line([(S(bus_x), S(y13 + 19)), (S(bus_x), S(y14 - 22))], fill="#0F1B2D", width=S(2))
    draw_arrow_head(drw, (S(bus_x), S(y14 - 18)), 0, 1, "#0F1B2D", size=S(10))
    drw.ellipse([S(bus_x - 36), S(y14 - 18), S(bus_x + 36), S(y14 + 22)], fill="#0F1B2D")
    drw.text((S(bus_x), S(y14 + 2)), "N14 EXIT", fill="white", font=f_b, anchor="mm")
    img.save(out_path, "PNG")


if __name__ == "__main__":
    with open(os.path.join(IMG, "ceg_graph.svg"), "w") as fh:
        fh.write(build_svg())
    with open(os.path.join(DOCS, "CEG_Drawio.drawio"), "w") as fh:
        fh.write(build_drawio())
    build_png(os.path.join(IMG, "ceg_graph.png"))
    build_cfg_png(os.path.join(IMG, "cfg_graph.png"))
    print("saved CEG_Drawio.drawio, ceg_graph.svg, ceg_graph.png, cfg_graph.png")
