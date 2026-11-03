#!/usr/bin/env python3
"""
Generator document de laborator (A4 Portrait PDF) — Proiect de laborator TSS (Smart Parking Gate)
Echipa: Natalia Moroz (50%) & Victor Mura (50%)

Produce:
  - proiect_laborator/docs/Prezentare_Laborator_TSS.pdf
  - proiect_laborator/docs/Raport_Proiect_Laborator_TSS.pdf
"""

import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lab_data as D  # noqa: E402

BASE = os.path.dirname(HERE)
HTML_PATH = os.path.join(BASE, "docs", "Raport_Proiect_Laborator_TSS.html")
PDF_MAIN = os.path.join(BASE, "docs", "Prezentare_Laborator_TSS.pdf")
PDF_COPY = os.path.join(BASE, "docs", "Raport_Proiect_Laborator_TSS.pdf")
CEG_IMG = os.path.join(BASE, "docs", "img", "ceg_graph.png")
CFG_IMG = os.path.join(BASE, "docs", "img", "cfg_graph.png")
MUTATION_JSON = os.path.join(BASE, "mutation_results", "summary.json")


def h(text):
    return html.escape(str(text))


def build_mini_dt_html(upto_idx):
    """Generează tabelul de decizie parțial după primele `upto_idx` reguli."""
    rules = D.CEG_RULES[:upto_idx]
    ths = "".join(f"<th>{h(r[0])}</th>" for r in rules)
    rows = []
    for cid, _ in D.CAUSES:
        tds = [f"<td class='code bold'>{h(cid)}</td>"]
        for _, _, case in rules:
            v = str(D.causes_of(case)[cid])
            cls = "center code " + ("one-cell" if v == "1" else "zero-cell")
            tds.append(f"<td class='{cls}'>{v}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    for eid, _, _ in D.EFFECTS:
        tds = [f"<td class='code bold'>{h(eid)}</td>"]
        for _, active_eff, _ in rules:
            v = "1" if active_eff == eid else "0"
            cls = "center code " + ("effect-one" if v == "1" else "zero-cell")
            tds.append(f"<td class='{cls}'>{v}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    return f"""
    <table class="compact-table">
      <thead><tr><th></th>{ths}</tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


def build_html():
    with open(MUTATION_JSON, "r", encoding="utf-8") as fh:
        MUT = json.load(fh)

    src_path = os.path.join(BASE, "src", "parking_gate.py")
    with open(src_path, "r", encoding="utf-8") as f:
        src_lines = f.readlines()
    numbered_src = "\n".join(f"{i+1:2d} | {line.rstrip()}" for i, line in enumerate(src_lines))

    # 1. Output classes
    out_desc = {
        "I1": "Acces garantat necondiționat pe loc VIP (tier == VIP)",
        "I2": "Acces interzis pentru subcontractori în afara orelor 08:00–17:59",
        "I3": "Acces aprobat cu alocarea unei stații de încărcare EV",
        "I4": "Acces gratuit în limita cotei alocate companiei (occupied < quota)",
        "I5": "Acces suplimentar cu plată (overflow permis și off-peak sau depășire < 5)",
        "I6": "Acces refuzat — cota companiei este epuizată și overflow indisponibil",
        "I7": "Excepție ridicată pentru parametri numerici în afara domeniului valid",
    }
    out_rows = "".join(
        f"<tr><td class='code bold center'>{h(oid)}</td>"
        f"<td class='code bold'>{h(name)}</td>"
        f"<td>{h(out_desc[oid])}</td></tr>"
        for oid, name, _ in D.OUTPUTS
    )

    # 2. Input classes
    in_rows = []
    for param, val_c, inv_c in D.INPUT_CLASSES:
        v_str = " · ".join(f"{k}: {cond}" for k, cond in val_c)
        i_str = " · ".join(f"{k}: {cond}" for k, cond in inv_c) if inv_c else "—"
        in_rows.append(
            f"<tr><td class='code bold'>{h(param)}</td>"
            f"<td class='valid'>{h(v_str)}</td>"
            f"<td class='{'invalid' if inv_c else 'center'}'>{h(i_str)}</td></tr>"
        )
    in_rows_html = "".join(in_rows)

    # 3. Final Equivalence Classes (EC1..EC13)
    ep_rows = []
    for ec_id, in_cls, cases in D.EP_FINAL:
        for case in cases:
            res = D.run(case)
            oid = D.OUT_ID[res]
            in_desc = f"{in_cls} (restul valide)" if len(in_cls) <= 2 else in_cls.replace(" ", ", ")
            ep_rows.append(
                f"<tr><td class='code bold center'>{h(ec_id)}</td>"
                f"<td class='code'>{h(in_desc)}</td>"
                f"<td class='code bold center'>{h(oid)}</td>"
                f"<td class='code'>{h(D.fmt_case(case))}</td>"
                f"<td class='code bold'>{h(res)}</td></tr>"
            )
    ep_rows_html = "".join(ep_rows)

    # 4. All 25 BVA test cases
    bva_rows = []
    b_idx = 0
    for grp_name, var_sym, cases in D.BVA_GROUPS:
        bva_rows.append(
            f"<tr class='group-row'><td colspan='5'>Frontieră: {h(grp_name)} (variabila {h(var_sym)})</td></tr>"
        )
        for case in cases:
            b_idx += 1
            res = D.run(case)
            oid = D.OUT_ID[res]
            bva_rows.append(
                f"<tr><td class='code bold center'>B{b_idx:02d}</td>"
                f"<td>{h(grp_name)}</td>"
                f"<td class='code'>{h(D.fmt_case(case))}</td>"
                f"<td class='code bold center'>{h(oid)}</td>"
                f"<td class='code bold'>{h(res)}</td></tr>"
            )
    bva_rows_html = "".join(bva_rows)

    # 5. CEG Causes & Effects
    causes_rows = "".join(
        f"<tr><td class='code bold center'>{h(cid)}</td><td>{h(lbl)}</td></tr>"
        for cid, lbl in D.CAUSES
    )
    effects_rows = "".join(
        f"<tr><td class='code bold center'>{h(eid)}</td>"
        f"<td class='code center bold'>I{h(eid[2:])}</td>"
        f"<td class='code'>{h(name)}</td>"
        f"<td class='code bold'>{h(expr)}</td></tr>"
        for eid, name, expr in D.EFFECTS
    )

    # 6. Step-by-step decision table cards
    step_specs = [
        ("Pasul 1 — Efectul Ef1 = 1 (GRANTED_VIP)", "Ef1 = C1", 1, D.CEG_STEPS["Ef1"]),
        ("Pasul 2 — Efectul Ef2 = 1 (DENIED_RESTRICTED_HOURS)", "Ef2 = C2 ∧ ¬C3", 2, D.CEG_STEPS["Ef2"]),
        ("Pasul 3 — Efectul Ef3 = 1 (GRANTED_EV_CHARGING)", "Ef3 = C4 ∧ C5 ∧ (¬C3 ∨ C6)", 4, D.CEG_STEPS["Ef3"]),
        ("Pasul 4 — Efectul Ef4 = 1 (GRANTED_REGULAR)", "Ef4 = C6 (cu Ef1..Ef3 = 0)", 5, D.CEG_STEPS["Ef4"]),
        ("Pasul 5 — Efectul Ef5 = 1 (GRANTED_PAID_OVERFLOW)", "Ef5 = ¬C6 ∧ C7 ∧ (¬C3 ∨ C8)", 7, D.CEG_STEPS["Ef5"]),
        ("Pasul 6 — Efectul Ef6 = 1 (DENIED_QUOTA_EXCEEDED)", "Ef6 = ¬C6 ∧ ¬(C7 ∧ (¬C3 ∨ C8))", 9, D.CEG_STEPS["Ef6"]),
    ]
    step_cards = []
    for ttl, form, upto, lines in step_specs:
        notes_html = "<br>".join(h(ln) for ln in lines)
        step_cards.append(f"""
        <div class="step-card">
          <div class="step-header">
            <span class="step-title">{h(ttl)}</span>
            <span class="step-formula">{h(form)}</span>
          </div>
          <p class="step-note">{notes_html}</p>
          {build_mini_dt_html(upto)}
        </div>
        """)

    # 7. Final Decision Table (R1..R9)
    dt_ths = "".join(f"<th style='width:9%'>{h(r[0])}</th>" for r in D.CEG_RULES)
    dt_rows = []
    for cid, lbl in D.CAUSES:
        tds = [f"<td class='code bold'>{h(cid)}: {h(lbl)}</td>"]
        for _, _, case in D.CEG_RULES:
            v = str(D.causes_of(case)[cid])
            cls = "center code " + ("one-cell" if v == "1" else "zero-cell")
            tds.append(f"<td class='{cls}'>{v}</td>")
        dt_rows.append("<tr>" + "".join(tds) + "</tr>")

    dt_rows.append("<tr class='group-row'><td colspan='10'>Efecte (Ef1 .. Ef6) după aplicarea măștilor M</td></tr>")
    for eid, name, _ in D.EFFECTS:
        tds = [f"<td class='code bold'>{h(eid)}: {h(name)}</td>"]
        for _, active_eff, _ in D.CEG_RULES:
            v = "1" if active_eff == eid else "0"
            cls = "center code " + ("effect-one" if v == "1" else "zero-cell")
            tds.append(f"<td class='{cls}'>{v}</td>")
        dt_rows.append("<tr>" + "".join(tds) + "</tr>")

    in_tds = ["<td class='bold'>Input (q, o, h, tier, ev, sp, ovf)</td>"]
    out_tds = ["<td class='bold'>Output (decizie barieră)</td>"]
    for _, _, case in D.CEG_RULES:
        q, o, hr, tier, ev, sp, ovf = case
        b = lambda x: "T" if x else "F"
        in_tds.append(f"<td class='code small center'>({q},{o},{hr},{tier.name[:3]},{b(ev)},{b(sp)},{b(ovf)})</td>")
        res = D.run(case)
        oid = D.OUT_ID[res]
        short_res = res.replace("GRANTED_", "").replace("DENIED_", "")
        out_tds.append(f"<td class='code small center bold'>{h(oid)}: {h(short_res)}</td>")
    dt_rows.append("<tr>" + "".join(in_tds) + "</tr>")
    dt_rows.append("<tr>" + "".join(out_tds) + "</tr>")

    # 8. Coverage table
    cov_rows = []
    for s_name, n_tests, st_cov, br_cov, miss, expl in D.COVERAGE[:3]:
        st_pct = st_cov / D.TOTAL_STMTS * 100
        br_pct = br_cov / D.TOTAL_BRANCHES * 100
        tot_pct = (st_cov + br_cov) / (D.TOTAL_STMTS + D.TOTAL_BRANCHES) * 100
        cov_rows.append(
            f"<tr><td class='bold'>{h(s_name)}</td>"
            f"<td class='center'>{n_tests}</td>"
            f"<td class='center code'>{st_cov} / {D.TOTAL_STMTS} ({st_pct:.1f}%)</td>"
            f"<td class='center code'>{br_cov} / {D.TOTAL_BRANCHES} ({br_pct:.1f}%)</td>"
            f"<td class='center code bold'>{tot_pct:.0f}%</td>"
            f"<td class='center code'>{h(miss)}</td>"
            f"<td>{h(expl)}</td></tr>"
        )
    cov_rows_html = "".join(cov_rows)

    # 9. Mutation tools table
    mut_suites = [
        ("functional", "Suita Cerinței 1 — Teste funcționale (49 teste: EP 15 + BVA 25 + CEG 9)"),
        ("mcdc", "Suita Cerinței 4 — Teste structurale MC/DC (5 teste: T1..T5 în test_mcdc.py)"),
        ("combined", "Suita Combinată — Cerința 1 + Cerința 4 (54 teste)"),
    ]
    mut_rows = []
    for k, lbl in mut_suites:
        m = MUT["mutmut"][k]
        c = MUT["cosmic_ray"][k]
        mut_rows.append(
            f"<tr><td class='bold'>{h(lbl)}</td>"
            f"<td class='center code bold'>{m['killed']} / {m['total']} ({m['score']}%)</td>"
            f"<td class='center code bold'>{c['killed']} / {c['total']} ({c['score']}%)</td></tr>"
        )
    mut_rows_html = "".join(mut_rows)

    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<title>Documentație Proiect Laborator TSS — Smart Parking Gate</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 12mm 13mm 12mm 13mm;
  }}
  * {{
    box-sizing: border-box;
  }}
  body {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 9.1pt;
    line-height: 1.38;
    color: #0F172A;
    margin: 0;
    padding: 0;
  }}
  h1 {{
    font-size: 15pt;
    color: #FFFFFF;
    margin: 0 0 4px 0;
  }}
  h2 {{
    font-size: 11.8pt;
    color: #1E3A8A;
    border-bottom: 2px solid #1E3A8A;
    padding-bottom: 3px;
    margin: 13px 0 6px 0;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 10pt;
    color: #0F172A;
    margin: 8px 0 4px 0;
    page-break-after: avoid;
  }}
  p {{
    margin: 4px 0 6px 0;
  }}
  .header-banner {{
    background: #0F1B2D;
    color: #FFFFFF;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 9px;
  }}
  .header-banner .sub {{
    color: #93C5FD;
    font-size: 9.3pt;
  }}
  .meta-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 9px;
  }}
  .meta-box {{
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #5B4FD6;
    border-radius: 4px;
    padding: 7px 10px;
    font-size: 8.5pt;
  }}
  .meta-box.teal {{
    border-left-color: #0E8C7F;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 5px 0 8px 0;
    font-size: 8.1pt;
  }}
  th, td {{
    border: 1px solid #CBD5E1;
    padding: 3.5px 5px;
    text-align: left;
    vertical-align: middle;
  }}
  th {{
    background: #0F1B2D;
    color: #FFFFFF;
    font-weight: 600;
    text-align: center;
  }}
  tr:nth-child(even) td {{
    background: #F8FAFC;
  }}
  tr.group-row td {{
    background: #ECEAFB !important;
    color: #3730A3;
    font-weight: 700;
    font-size: 8.2pt;
  }}
  .code {{
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 7.8pt;
  }}
  .small {{
    font-size: 7.2pt;
  }}
  .center {{
    text-align: center;
  }}
  .bold {{
    font-weight: 700;
  }}
  .valid {{
    background: #F0FDF4 !important;
    color: #166534;
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 7.8pt;
  }}
  .invalid {{
    background: #FEF2F2 !important;
    color: #991B1B;
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 7.8pt;
  }}
  .one-cell {{
    background: #ECEAFB !important;
    color: #4338CA;
    font-weight: 700;
  }}
  .effect-one {{
    background: #DCFCE7 !important;
    color: #166534;
    font-weight: 700;
  }}
  .zero-cell {{
    color: #94A3B8;
  }}
  pre {{
    background: #0F172A;
    color: #F8FAFC;
    padding: 8px 10px;
    border-radius: 5px;
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 7.5pt;
    line-height: 1.3;
    overflow-x: auto;
    margin: 5px 0 8px 0;
  }}
  .callout {{
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-left: 4px solid #2563EB;
    padding: 6px 10px;
    border-radius: 4px;
    margin: 6px 0;
    font-size: 8.5pt;
    break-inside: avoid;
  }}
  .callout.warn {{
    background: #FFFBEB;
    border-color: #FDE68A;
    border-left-color: #D97706;
  }}
  .callout.green {{
    background: #F0FDF4;
    border-color: #BBF7D0;
    border-left-color: #16A34A;
  }}
  .img-wrap {{
    text-align: center;
    margin: 6px 0 8px 0;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 6px;
  }}
  .img-wrap img {{
    max-width: 100%;
    height: auto;
  }}
  .steps-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 6px 0;
  }}
  .step-card {{
    border: 1px solid #CBD5E1;
    border-radius: 5px;
    padding: 6px 8px;
    background: #FFFFFF;
    break-inside: avoid;
  }}
  .step-header {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 3px;
    margin-bottom: 3px;
  }}
  .step-title {{
    font-weight: 700;
    color: #1E3A8A;
    font-size: 8.4pt;
  }}
  .step-formula {{
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    font-size: 7.6pt;
    color: #0E8C7F;
    font-weight: 700;
  }}
  .step-note {{
    font-size: 7.7pt;
    color: #334155;
    margin: 2px 0 4px 0;
  }}
  .compact-table {{
    margin: 2px 0;
    font-size: 6.8pt;
  }}
  .compact-table th, .compact-table td {{
    padding: 1px 3px;
  }}
  .dt-final {{
    table-layout: fixed;
    width: 100%;
    font-size: 7.0pt;
    break-inside: avoid;
  }}
  .dt-final th, .dt-final td {{
    padding: 2px 2.5px;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }}
  .page-break {{
    page-break-before: always;
  }}
  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}
</style>
</head>
<body>

<div class="header-banner">
  <h1>PROIECT DE LABORATOR — TESTAREA SISTEMELOR SOFTWARE (TSS)</h1>
  <div class="sub">Sistemul de Control Acces într-o Parcare Corporate Multi-Tenant (<code>src/parking_gate.py</code>) · Universitatea din București · FMI · 2026</div>
</div>

<div class="meta-grid">
  <div class="meta-box">
    <strong>Student 1 — Natalia Moroz (50% contribuție):</strong><br>
    • <strong>Cerința 1:</strong> Generarea datelor de test funcționale (EP: 15 teste, BVA: 25 teste, Graf Cauză-Efect: 9 teste) în <code>pytest</code>.<br>
    • <strong>Cerința 2:</strong> Măsurarea acoperirii la nivel de instrucțiune și de ramură pe seturile de la Cerința 1.<br>
    • <strong>Cerința 5:</strong> Formularea și demonstrarea unui mutant de ordinul 1 echivalent.
  </div>
  <div class="meta-box teal">
    <strong>Student 2 — Victor Mura (50% contribuție):</strong><br>
    • <strong>Cerința 3:</strong> Construirea grafului orientat de control (CFG), calculul complexității ciclomatice <em>V(G) = 7</em> și extragerea căilor independente.<br>
    • <strong>Cerința 4:</strong> Generarea setului minimal de teste pentru criteriul <strong>MC/DC</strong> pe decizia compusă EV.<br>
    • <strong>Cerințele 6 &amp; 7:</strong> Doi mutanți ne-echivalenți (omorât vs. supraviețuitor) și analiza comparativă <code>mutmut</code> vs. <code>cosmic-ray</code>.
  </div>
</div>

<h2>0. Specificația Problematicii și Codul Sursă Supus Testării</h2>
<p>Funcția <code>evaluate_parking_access()</code> primește 7 parametri de intrare (cota companiei <code>company_allocated_quota</code>, locurile ocupate <code>company_current_occupied</code>, ora <code>entry_hour</code>, statutul angajatului <code>tier</code>, indicatorul <code>is_electric_vehicle</code>, disponibilitatea stațiilor EV <code>has_ev_spots_available</code> și permisiunea de depășire contra cost <code>company_allows_overflow</code>) și returnează decizia barierei (una din cele 6 valori <code>AccessDecision</code> sau excepția <code>ValueError</code>):</p>

<pre>{h(numbered_src)}</pre>

<h2>1. Cerința 1 — Testare Funcțională (Natalia Moroz)</h2>

<h3>1.1 Partiționarea în Clase de Echivalență (Equivalence Partitioning — EP)</h3>
<p>Pentru partiționarea domeniului în clase de echivalență, identificăm mai întâi <strong>clasele de ieșire (<em>I</em><sub>1</sub> … <em>I</em><sub>7</sub>)</strong> și <strong>clasele de intrare (valide și invalide)</strong> pentru fiecare parametru sau grup de parametri corelați, după care construim <strong>clasele de echivalență finale (<em>EC</em><sub>1</sub> … <em>EC</em><sub>13</sub>)</strong> ca asocieri între combinațiile de clase de intrare și clasa de ieșire produsă.</p>

<div class="two-col">
  <div>
    <table>
      <thead><tr><th style="width:15%">Clasă</th><th style="width:38%">Valoare / Excepție</th><th>Descriere</th></tr></thead>
      <tbody>{out_rows}</tbody>
    </table>
  </div>
  <div>
    <table>
      <thead><tr><th style="width:26%">Parametru</th><th style="width:44%">Clase de Intrare Valide</th><th>Clase Invalide</th></tr></thead>
      <tbody>{in_rows_html}</tbody>
    </table>
    <div class="callout" style="margin-top:4px;">
      <strong>Selecția claselor pentru <code>(is_ev, has_spot)</code>:</strong> Când <code>is_ev = True</code>, disponibilitatea stației schimbă decizia între <em>I</em><sub>3</sub> și fluxul standard, deci avem două clase: <em>V</em><sub>1</sub> = <code>(T, T)</code> și <em>V</em><sub>2</sub> = <code>(T, F)</code>. Când <code>is_ev = False</code>, conjuncția <code>is_electric_vehicle and has_ev_spots_available</code> este <code>False</code> indiferent de <code>has_spot</code>, deci <code>(F, T)</code> și <code>(F, F)</code> sunt echivalente comportamental și formează clasa <em>V</em><sub>3</sub> = <code>(F, –)</code>.
    </div>
  </div>
</div>

<h3>Tabelul Claselor de Echivalență Finale (<em>EC</em><sub>1</sub> … <em>EC</em><sub>13</sub>) și Valorile Testate (<code>tests/test_ep.py</code>)</h3>
<table>
  <thead>
    <tr>
      <th style="width:9%">Clasă Finală</th>
      <th style="width:24%">Combinație Clase de Intrare</th>
      <th style="width:9%">Clasă Ieșire</th>
      <th style="width:34%">Valoare Testată <code>(q, o, h, tier, ev, spot, ovf)</code></th>
      <th style="width:24%">Rezultat Obținut</th>
    </tr>
  </thead>
  <tbody>{ep_rows_html}</tbody>
</table>

<div class="page-break"></div>

<h3>1.2 Analiza Valorilor de Frontieră (Boundary Value Analysis — BVA)</h3>
<p>Pentru fiecare frontieră numerică a domeniilor de intrare și a pragurilor decizionale am testat tripletul <code>(frontieră − 1, frontieră, frontieră + 1)</code>. Mai jos sunt afișate <strong>toate cele 25 de cazuri BVA</strong> implementate în <code>tests/test_bva.py</code>:</p>

<table>
  <thead>
    <tr>
      <th style="width:7%">Caz #</th>
      <th style="width:23%">Frontieră Testată</th>
      <th style="width:36%">Valoare Testată <code>(q, o, h, tier, ev, spot, ovf)</code></th>
      <th style="width:10%">Clasă Ieșire</th>
      <th style="width:24%">Rezultat Obținut</th>
    </tr>
  </thead>
  <tbody>{bva_rows_html}</tbody>
</table>

<div class="page-break"></div>

<h3>1.3 Graful Cauză-Efect (Cause-Effect Graph — CEG)</h3>
<p>Pe domeniul valid al datelor de intrare, logica funcției este modelată prin <strong>8 cauze booleene (<em>C</em><sub>1</sub> … <em>C</em><sub>8</sub>)</strong>, <strong>3 noduri intermediare numerotate <code>1, 2, 3</code></strong> și <strong>6 efecte (<em>Ef</em><sub>1</sub> … <em>Ef</em><sub>6</sub>)</strong>:</p>

<div class="two-col">
  <div>
    <table>
      <thead><tr><th style="width:18%">Cauză</th><th>Semnificație Booleană</th></tr></thead>
      <tbody>{causes_rows}</tbody>
    </table>
  </div>
  <div>
    <table>
      <thead><tr><th style="width:13%">Efect</th><th style="width:13%">Ieșire</th><th style="width:40%">Decizie</th><th>Expresie din Graf</th></tr></thead>
      <tbody>{effects_rows}</tbody>
    </table>
  </div>
</div>

<div class="callout">
  <strong>Clarificarea Notațiilor și a Relațiilor de Mascare (<em>M</em>) între Efecte:</strong><br>
  • <strong>Eliminarea confuziei <em>I</em><sub>1</sub>, <em>I</em><sub>2</sub>, <em>I</em><sub>3</sub>:</strong> În secțiunea 1.1, notația <em>I</em><sub>1</sub> … <em>I</em><sub>7</sub> reprezintă <em>clasele de ieșire</em>. De aceea, nodurile intermediare din graf sunt notate cu cifrele <strong><code>1</code>, <code>2</code>, <code>3</code></strong> în cercuri: nodul <code>1</code> = ¬<em>C</em><sub>3</sub> ∨ <em>C</em><sub>6</sub>, nodul <code>2</code> = ¬<em>C</em><sub>3</sub> ∨ <em>C</em><sub>8</sub>, nodul <code>3</code> = <em>C</em><sub>7</sub> ∧ nodul <code>2</code>.<br>
  • <strong>Constrângerea de exclusivitate pe cauze <em>E</em>(<em>C</em><sub>1</sub>, <em>C</em><sub>2</sub>):</strong> Un angajat nu poate avea simultan rolul <code>VIP</code> (<em>C</em><sub>1</sub>=1) și <code>CONTRACTOR</code> (<em>C</em><sub>2</sub>=1).<br>
  • <strong>Relații de mascare (<em>M</em>) între efecte:</strong> Deoarece instrucțiunile <code>if ... return</code> se evaluează secvențial, activarea unui efect superior maschează efectele de mai jos (le forțează la <code>0</code>):
  <strong><em>M</em>(<em>Ef</em><sub>1</sub>, {{<em>Ef</em><sub>3</sub>, <em>Ef</em><sub>4</sub>, <em>Ef</em><sub>5</sub>, <em>Ef</em><sub>6</sub>}})</strong>, <strong><em>M</em>(<em>Ef</em><sub>2</sub>, {{<em>Ef</em><sub>3</sub>, <em>Ef</em><sub>4</sub>, <em>Ef</em><sub>5</sub>, <em>Ef</em><sub>6</sub>}})</strong> și <strong><em>M</em>(<em>Ef</em><sub>3</sub>, {{<em>Ef</em><sub>4</sub>, <em>Ef</em><sub>5</sub>, <em>Ef</em><sub>6</sub>}})</strong>. Efectele <em>Ef</em><sub>4</sub>, <em>Ef</em><sub>5</sub>, <em>Ef</em><sub>6</sub> sunt deja reciproc disjuncte prin condițiile <em>C</em><sub>6</sub> vs. ¬<em>C</em><sub>6</sub> și nodul <code>3</code> vs. ¬nodul <code>3</code>.
</div>

<div class="img-wrap">
  <img src="{CEG_IMG}" alt="Graful Cauză-Efect">
  <div class="small" style="color:#475569; margin-top:3px;">Figura 1 — Graful Cauză-Efect realizat în Draw.io (<code>docs/CEG_Drawio.drawio</code>). Negația este marcată prin simbolul <code>~</code> pe muchie, conjuncția/disjuncția prin arcele cu ∧ și ∨, exclusivitatea cauzelor prin <code>E</code>, iar mascarea între efecte prin <code>M</code>.</div>
</div>

<div class="page-break"></div>

<h3>1.4 Construcția Pas cu Pas a Tabelului de Decizie până la Forma Finală</h3>
<p>Pornind de la fiecare efect <em>Ef<sub>k</sub></em> = 1 (<em>k</em> = 1 … 6), parcurgem graful invers către cauze și adăugăm coloanele (regulile) corespunzătoare, ținând cont de exclusivitatea <em>E</em>(<em>C</em><sub>1</sub>, <em>C</em><sub>2</sub>) și de măștile <em>M</em>:</p>

<div class="steps-grid">
  {''.join(step_cards)}
</div>

<h3>Tabelul de Decizie Final (<em>R</em><sub>1</sub> … <em>R</em><sub>9</sub>) cu Valori de Intrare și Ieșire (<code>tests/test_ceg.py</code>)</h3>
<table class="dt-final">
  <thead>
    <tr><th style="width:19%">Cauză / Efect</th>{dt_ths}</tr>
  </thead>
  <tbody>{''.join(dt_rows)}</tbody>
</table>

<h2>2. Cerința 2 — Analiza Acoperirii Codului pe Seturile de la Cerința 1 (Natalia Moroz)</h2>

<div class="callout">
  <strong>Diferența dintre Acoperirea la Nivel de Instrucțiune (Statement Coverage) și Acoperirea la Nivel de Ramură (Branch Coverage):</strong><br>
  • <strong>Acoperirea la nivel de instrucțiune (29 instrucțiuni în <code>src/parking_gate.py</code>):</strong> Măsoară câte linii executabile au fost rulate cel puțin o dată. O instrucțiune <code>if cond:</code> este marcată ca executată chiar dacă expresia <code>cond</code> a luat doar valoarea <code>False</code>.<br>
  • <strong>Acoperirea la nivel de ramură (12 ramuri = 6 instrucțiuni <code>if</code> × 2 ieșiri <code>True</code>/<code>False</code>):</strong> Impune ca fiecare decizie <code>if</code> să fie parcursă atât pe ramura <code>True</code>, cât și pe ramura <code>False</code>. În <code>src/parking_gate.py</code>, neintrarea în corpul unui <code>if</code> lasă 1 instrucțiune din 29 neacoperită (−3.4%), dar lasă 1 ramură din 12 neacoperită (−8.3%).
</div>

<table>
  <thead>
    <tr>
      <th style="width:10%">Set Teste</th>
      <th style="width:8%">Nr. Teste</th>
      <th style="width:17%">Instrucțiuni Acoperite</th>
      <th style="width:16%">Ramuri Acoperite</th>
      <th style="width:10%">Total</th>
      <th style="width:10%">Linii Lipsă</th>
      <th>Interpretare și Motivul Neacoperirii</th>
    </tr>
  </thead>
  <tbody>{cov_rows_html}</tbody>
</table>

<h2>3. Cerința 3 — Graful Orientat de Control (CFG), Complexitatea Ciclomatică și Căile Independente (Victor Mura)</h2>

<div class="two-col">
  <div class="img-wrap" style="margin:0;">
    <img src="{CFG_IMG}" alt="Graful de Flux de Control" style="max-height:380px;">
    <div class="small" style="color:#475569;">Figura 2 — Graful Orientat de Flux de Control (<code>docs/CFG_Drawio.drawio</code>)</div>
  </div>
  <div>
    <h3>Calculul Complexității Ciclomatice McCabe <em>V</em>(<em>G</em>)</h3>
    <p>Graful orientat are <em>n</em> = 14 noduri (6 noduri predicat <code>N1, N3, N5, N7, N9, N11</code>, 7 noduri de retur/excepție <code>N2, N4, N6, N8, N10, N12, N13</code> și nodul de ieșire <code>N14</code>) și <em>e</em> = 19 arce orientate:</p>
    <ol>
      <li><strong>Formula cu arce și noduri:</strong><br>
      <em>V</em>(<em>G</em>) = <em>e</em> − <em>n</em> + 2 = 19 − 14 + 2 = <strong>7</strong><br>
      (sau <em>e</em><sub>ext</sub> − <em>n</em> + 1 = 20 − 14 + 1 = <strong>7</strong> incluzând arcul <code>N14 → N1</code>).</li>
      <li><strong>Formula cu noduri predicat (<em>P</em> = 6):</strong><br>
      <em>V</em>(<em>G</em>) = <em>P</em> + 1 = 6 + 1 = <strong>7</strong>.</li>
      <li><strong>Formula cu regiuni în plan:</strong><br>
      <em>V</em>(<em>G</em>) = <em>R</em> = 6 regiuni închise + 1 regiune exterioară = <strong>7</strong>.</li>
    </ol>
  </div>
</div>

<h3>Cele 7 Căi Liniar Independente (<em>P</em><sub>1</sub> … <em>P</em><sub>7</sub>)</h3>
<table>
  <thead>
    <tr>
      <th style="width:7%">Cale</th>
      <th style="width:36%">Secvența de Noduri Parcursă</th>
      <th style="width:32%">Intrare <code>(q, o, h, tier, ev, sp, ovf)</code></th>
      <th style="width:25%">Ieșire</th>
    </tr>
  </thead>
  <tbody>
    <tr><td class="code bold center">P1</td><td class="code">N1 → N2 → N14</td><td class="code">(0, 0, 10, REGULAR, F, F, F)</td><td class="code bold">I7: ValueError</td></tr>
    <tr><td class="code bold center">P2</td><td class="code">N1 → N3 → N4 → N14</td><td class="code">(10, 10, 22, VIP, F, F, F)</td><td class="code bold">I1: GRANTED_VIP</td></tr>
    <tr><td class="code bold center">P3</td><td class="code">N1 → N3 → N5 → N6 → N14</td><td class="code">(10, 2, 19, CONTRACTOR, F, F, F)</td><td class="code bold">I2: DENIED_RESTRICTED_HOURS</td></tr>
    <tr><td class="code bold center">P4</td><td class="code">N1 → N3 → N5 → N7 → N8 → N14</td><td class="code">(10, 10, 6, REGULAR, T, T, F)</td><td class="code bold">I3: GRANTED_EV_CHARGING</td></tr>
    <tr><td class="code bold center">P5</td><td class="code">N1 → N3 → N5 → N7 → N9 → N10 → N14</td><td class="code">(10, 5, 11, REGULAR, F, F, F)</td><td class="code bold">I4: GRANTED_REGULAR</td></tr>
    <tr><td class="code bold center">P6</td><td class="code">N1 → N3 → N5 → N7 → N9 → N11 → N12 → N14</td><td class="code">(10, 12, 11, REGULAR, F, F, T)</td><td class="code bold">I5: GRANTED_PAID_OVERFLOW</td></tr>
    <tr><td class="code bold center">P7</td><td class="code">N1 → N3 → N5 → N7 → N9 → N11 → N13 → N14</td><td class="code">(10, 10, 11, REGULAR, F, F, F)</td><td class="code bold">I6: DENIED_QUOTA_EXCEEDED</td></tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>4. Cerința 4 — Criteriul MC/DC pe Decizia Compusă EV (Victor Mura)</h2>
<p>Analizăm decizia compusă de la linia 69 din <code>src/parking_gate.py</code>, care conține <em>N</em> = 4 condiții atomice independente:</p>
<p class="code bold" style="background:#F1F5F9; padding:5px 8px; border-radius:4px;">
  D = (A ∧ B) ∧ (¬C ∨ Dq) &nbsp;&nbsp;unde:&nbsp; A = is_electric_vehicle, B = has_ev_spots_available, C = is_peak_hours, Dq = is_within_quota
</p>
<p>Setul minimal care satisface criteriul MC/DC are <em>N</em> + 1 = 5 teste (<code>T1..T5</code> în <code>tests/test_mcdc.py</code>):</p>

<table>
  <thead>
    <tr>
      <th style="width:7%">Test</th>
      <th style="width:5%">A</th>
      <th style="width:5%">B</th>
      <th style="width:5%">C</th>
      <th style="width:6%">Dq</th>
      <th style="width:6%">D</th>
      <th style="width:28%">Intrare <code>(q, o, h, tier, ev, sp, ovf)</code></th>
      <th style="width:20%">Rezultat</th>
      <th style="width:18%">Pereche Independență</th>
    </tr>
  </thead>
  <tbody>
    <tr><td class="code bold center">T1</td><td class="center code">1</td><td class="center code">1</td><td class="center code">0</td><td class="center code">0</td><td class="center code effect-one">1</td><td class="code">(10, 10, 6, REG, T, T, F)</td><td class="code bold">GRANTED_EV_CHARGING</td><td>Bază pt. A, B, C</td></tr>
    <tr><td class="code bold center">T2</td><td class="center code">0</td><td class="center code">1</td><td class="center code">0</td><td class="center code">0</td><td class="center code zero-cell">0</td><td class="code">(10, 10, 6, REG, F, T, F)</td><td class="code">DENIED_QUOTA_EXCEEDED</td><td class="code bold">A: (T1, T2)</td></tr>
    <tr><td class="code bold center">T3</td><td class="center code">1</td><td class="center code">0</td><td class="center code">0</td><td class="center code">0</td><td class="center code zero-cell">0</td><td class="code">(10, 10, 6, REG, T, F, F)</td><td class="code">DENIED_QUOTA_EXCEEDED</td><td class="code bold">B: (T1, T3)</td></tr>
    <tr><td class="code bold center">T4</td><td class="center code">1</td><td class="center code">1</td><td class="center code">1</td><td class="center code">0</td><td class="center code zero-cell">0</td><td class="code">(10, 10, 10, REG, T, T, F)</td><td class="code">DENIED_QUOTA_EXCEEDED</td><td class="code bold">C: (T1, T4)</td></tr>
    <tr><td class="code bold center">T5</td><td class="center code">1</td><td class="center code">1</td><td class="center code">1</td><td class="center code">1</td><td class="center code effect-one">1</td><td class="code">(10, 7, 10, REG, T, T, F)</td><td class="code bold">GRANTED_EV_CHARGING</td><td class="code bold">Dq: (T4, T5)</td></tr>
  </tbody>
</table>

<h2>5. Cerința 5 — Mutant de Ordinul 1 Echivalent (Natalia Moroz)</h2>
<pre>56 |     # Ore de vârf / program normal de lucru al campusului: 08:00 - 17:59
57 | -   is_peak_hours = (8 &lt;= entry_hour &lt;= 17)     # Programul original P
57 | +   is_peak_hours = (7 &lt; entry_hour &lt; 18)       # Mutantul echivalent M_eq (mutants/equivalent_mutant.py)</pre>
<p><strong>Demonstrație:</strong> Deoarece <code>entry_hour</code> este întreg (<em>h</em> ∈ ℤ), pe mulțimea numerelor întregi avem echivalențele <em>h</em> ≥ 8 ⇔ <em>h</em> &gt; 7 și <em>h</em> ≤ 17 ⇔ <em>h</em> &lt; 18. Astfel, valoarea booleană a lui <code>is_peak_hours</code> este identică în <em>P</em> și în <em>M</em><sub>eq</sub> pentru orice <em>h</em> ∈ ℤ, deci <em>P</em>(<em>x</em>) = <em>M</em><sub>eq</sub>(<em>x</em>) pentru toate intrările posibile (verificat exhaustiv pe 1 152 combinații în <code>tests/test_equivalent_mutant.py</code>).</p>

<h2>6. Cerința 6 — Doi Mutanți de Ordinul 1 Ne-echivalenți: Omorât vs. Neomorât (Victor Mura)</h2>
<p>Ambii mutanți sunt evaluați față de același caz de test din Cerința 1 (BVA, B08): <code>test_bva_occupied_exactly_at_quota</code>, care apelează funcția cu intrarea:<br>
<code>q = 10, o = 10, h = 12, tier = REGULAR, ev = False, spot = False, company_allows_overflow = False</code> și verifică <code>assert res == AccessDecision.DENIED_QUOTA_EXCEEDED</code>.</p>

<h3>6.1 Mutantul #1 (Ne-echivalent, OMORÂT de <code>test_bva_occupied_exactly_at_quota</code>)</h3>
<pre>68 | -   is_within_quota = company_current_occupied &lt; company_allocated_quota
68 | +   is_within_quota = company_current_occupied &lt;= company_allocated_quota   # Mutație ROR: &lt; înlocuit cu &lt;=
...
73 |     if is_within_quota:
74 |         return AccessDecision.GRANTED_REGULAR</pre>
<p>Pentru <code>(q=10, o=10)</code>, programul original calculează <code>10 &lt; 10 → False</code> și returnează la final <code>DENIED_QUOTA_EXCEEDED</code>. Mutantul #1 calculează <code>10 &lt;= 10 → True</code> și returnează la linia 74 <code>GRANTED_REGULAR</code>, deci aserțiunea testului eșuează și <strong>mutantul este omorât</strong>.</p>

<h3>6.2 Mutantul #2 (Ne-echivalent, NEOMORÂT de <code>test_bva_occupied_exactly_at_quota</code>)</h3>
<p>Mai jos este redată integral secvența liniilor 72–82 din <code>src/parking_gate.py</code> pentru a se vedea complet instrucțiunea mutată:</p>
<pre>72 |     # 4. Acces standard în cota gratuită a companiei
73 |     if is_within_quota:                                  # (10 &lt; 10) este False -&gt; nu intră
74 |         return AccessDecision.GRANTED_REGULAR
75 |
76 |     # 5. Politica de depășire cotă (Overflow plătit pe companie)
77 |     overflow_count = company_current_occupied - company_allocated_quota   # 10 - 10 = 0
78 | -   if company_allows_overflow and (not is_peak_hours or overflow_count &lt; 5):
78 | +   if company_allows_overflow and (not is_peak_hours or overflow_count &lt; 4):  # MUTAȚIE: 5 -&gt; 4
79 |         return AccessDecision.GRANTED_PAID_OVERFLOW
80 |
81 |     # 6. Cota epuizată și overflow nepermis / indisponibil
82 |     return AccessDecision.DENIED_QUOTA_EXCEEDED</pre>

<div class="callout warn">
  <strong>De ce expresia mutată <code>overflow_count &lt; 4</code> nu se evaluează în acest test:</strong><br>
  • În <code>test_bva_occupied_exactly_at_quota</code>, parametrul <code>company_allows_overflow</code> este <code>False</code>.<br>
  • La linia 78, operatorul <code>and</code> din Python evaluează cu <strong>scurtcircuitare (short-circuit evaluation)</strong>: deoarece operandul din stânga (<code>company_allows_overflow</code>) este deja <code>False</code>, rezultatul conjuncției este garantat <code>False</code>, iar Python <strong>nu mai execută deloc paranteza din dreapta <code>(not is_peak_hours or overflow_count &lt; 4)</code></strong>.<br>
  • Prin urmare, atât originalul <em>P</em>, cât și Mutantul #2 trec direct la linia 82 și returnează <code>DENIED_QUOTA_EXCEEDED</code> (mutantul supraviețuiește acestui test).<br>
  • Mutantul #2 <strong>nu este echivalent</strong>: pentru testul BVA B22 <code>(q=10, o=14, h=10, REGULAR, F, F, company_allows_overflow=True)</code>, unde <code>overflow_count = 4</code> și <code>company_allows_overflow = True</code>, paranteza se execută și <em>P</em> returnează <code>GRANTED_PAID_OVERFLOW</code> (4 &lt; 5), în timp ce <em>M</em><sub>2</sub> returnează <code>DENIED_QUOTA_EXCEEDED</code> (4 &lt; 4 este <code>False</code>).
</div>

<h2>7. Cerința 7 — Compararea Utilitarelor <code>mutmut</code> și <code>cosmic-ray</code> (Victor Mura)</h2>

<div class="callout">
  <strong>Semnificația suitelor „Cerința 1” și „Cerința 4” în evaluarea mutațiilor:</strong><br>
  • <strong>Suita Cerinței 1 (49 teste funcționale):</strong> Cuprinde testele Black-Box din <code>test_ep.py</code> (15), <code>test_bva.py</code> (25) și <code>test_ceg.py</code> (9).<br>
  • <strong>Suita Cerinței 4 (5 teste structurale MC/DC):</strong> Cuprinde doar cele 5 teste <code>T1..T5</code> din <code>test_mcdc.py</code> proiectate special pentru decizia EV de la linia 69.<br>
  • <strong>Suita Combinată (Cerința 1 + Cerința 4 = 54 teste):</strong> Reunește ambele seturi pentru a măsura capacitatea totală de detecție a defectelor.
</div>

<table>
  <thead>
    <tr>
      <th style="width:48%">Suită de Teste Rulată</th>
      <th style="width:26%"><code>mutmut</code> (Mutanți Uciși / Total)</th>
      <th style="width:26%"><code>cosmic-ray</code> (Mutanți Uciși / Total)</th>
    </tr>
  </thead>
  <tbody>{mut_rows_html}</tbody>
</table>

<p><strong>Argumentarea diferențelor dintre cele două utilitare:</strong> <code>mutmut</code> generează <strong>40 de mutanți</strong> pe expresiile logice, relaționale și literale: 39/40 (97.5%) sunt uciși de suita Cerinței 1, 10/40 (25.0%) de suita Cerinței 4 (care vizează exclusiv decizia EV de la linia 69), și <strong>40/40 (100.0%)</strong> de suita combinată (Cerința 1 + Cerința 4). <code>cosmic-ray</code> aplică o gamă mai largă de operatori AST (<strong>101 mutanți</strong>), din care 98/101 (97.03%) sunt uciși de Cerința 1, 50/101 (49.5%) de Cerința 4 și <strong>99/101 (98.02%)</strong> de suita combinată; cei 2 mutanți supraviețuitori sunt mutanți echivalenți, rezultând un scor de mutație ajustat <em>MS</em> = <em>D</em> / (<em>M</em> − <em>E</em>) = <strong>100%</strong>.</p>

<h2>8. Contribuția Echipei și Concluzii</h2>
<table>
  <thead>
    <tr>
      <th style="width:22%">Autor</th>
      <th style="width:9%">Pondere</th>
      <th>Activități Realizate și Contribuție Proprie</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="bold">Natalia Moroz</td>
      <td class="center bold">50%</td>
      <td><strong>Cerințele 1, 2, 5:</strong> Determinarea claselor de intrare/ieșire și a celor 13 clase finale EP (<code>test_ep.py</code>), proiectarea celor 25 de cazuri BVA (<code>test_bva.py</code>), modelarea grafului Cauză-Efect în Draw.io (<code>CEG_Drawio.drawio</code>) cu relațiile de mascare <em>M</em> și derivarea pas cu pas a tabelului de decizie (<code>test_ceg.py</code>); analiza acoperirii pe instrucțiuni vs. ramuri; demonstrarea și verificarea exhaustivă a mutantului echivalent. Referințe tehnice auxiliare în <code>AI_USAGE_LAB.md</code>.</td>
    </tr>
    <tr>
      <td class="bold">Victor Mura</td>
      <td class="center bold">50%</td>
      <td><strong>Cerințele 3, 4, 6, 7:</strong> Construirea grafului orientat de flux de control (<code>CFG_Drawio.drawio</code>), calculul complexității ciclomatice <em>V</em>(<em>G</em>)=7 prin 3 metode și extragerea celor 7 căi independente; determinarea perechilor de independență MC/DC și implementarea setului minimal de 5 teste (<code>test_mcdc.py</code>); proiectarea și analiza celor doi mutanți ne-echivalenți (omorât vs. supraviețuitor prin scurtcircuitare) și rularea comparativă <code>mutmut</code> vs. <code>cosmic-ray</code>.</td>
    </tr>
  </tbody>
</table>

</body>
</html>
"""


def main():
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Wrote HTML:", HTML_PATH)

    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_MAIN}",
        f"file://{HTML_PATH}",
    ]
    subprocess.run(cmd, check=True)
    shutil.copyfile(PDF_MAIN, PDF_COPY)
    print("Saved PDF:", PDF_MAIN)
    print("Saved copy:", PDF_COPY)


if __name__ == "__main__":
    main()
