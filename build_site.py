"""Build docs/index.html, the mobile results page, from ledger.csv.

GitHub Pages serves the docs/ folder. The page is one self-contained HTML file
(inline CSS, SVG chart and a little JS for the chart tooltip), so it loads fast
on a phone and needs nothing else.

Strategies, same as the workbook:
  Top Pick:    $2 Win/Place/Show ($6) on the top pick
  Top 2 Picks: $6 WPS on the top pick plus $6 WPS on the second choice ($12)

Usage: python build_site.py [--csv ledger.csv] [--out docs/index.html]
"""
import argparse
import csv
import html
import json
import os
import re
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def num(v):
    try:
        return float(str(v).replace("$", "").replace(",", ""))
    except (TypeError, ValueError):
        return 0.0


def odds_to_float(s):
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", s or "")
    return float(m.group(1)) / float(m.group(2)) if m else None


def money(v, sign=False):
    s = f"${abs(v):,.2f}"
    if v < 0:
        return f"−{s}"
    return f"+{s}" if sign and v > 0 else s


def pct(v, sign=False):
    s = f"{abs(v) * 100:.1f}%"
    if v < 0:
        return f"−{s}"
    return f"+{s}" if sign and v > 0 else s


def ordinal(n):
    n = int(n)
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def esc(s):
    return html.escape(str(s or ""))


def md_inline(s):
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r'(?<!href=")(?<!">)(https?://[^\s<]+)', r'<a href="\1">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def md_to_html(text):
    """Small Markdown converter for the handicap write-ups: headings, paragraphs,
    bullet and numbered lists, pipe tables, bold, italic, code and links. Kept
    dependency-free so the unattended daily run never needs a pip install."""
    out, para, items, list_tag, table = [], [], [], None, []

    def flush():
        nonlocal para, items, list_tag, table
        if para:
            out.append(f"<p>{md_inline(' '.join(para))}</p>")
        if items:
            out.append(f"<{list_tag}>" + "".join(f"<li>{md_inline(i)}</li>" for i in items) + f"</{list_tag}>")
        if table:
            cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in table]
            body = [r for r in cells[1:] if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
            head = "".join(f"<th>{md_inline(c)}</th>" for c in cells[0])
            rows = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        para, items, list_tag, table = [], [], None, []

    for line in text.splitlines():
        s = line.strip()
        m_h = re.match(r"(#{1,4})\s+(.*)", s)
        m_ul = re.match(r"[-*]\s+(.*)", s)
        m_ol = re.match(r"\d+[.)]\s+(.*)", s)
        if not s:
            flush()
        elif m_h:
            flush()
            level = max(2, len(m_h.group(1)))  # the page title is the only h1
            out.append(f"<h{level}>{md_inline(m_h.group(2))}</h{level}>")
        elif s.startswith("|"):
            if para or items:
                flush()
            table.append(s)
        elif m_ul or m_ol:
            tag = "ul" if m_ul else "ol"
            if para or table or (list_tag and list_tag != tag):
                flush()
            list_tag = tag
            items.append((m_ul or m_ol).group(1))
        elif items and line[:1] in (" ", "\t"):
            items[-1] += " " + s  # continuation of a list item
        else:
            if items or table:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if any((v or "").strip() for v in r.values())]
    rows.sort(key=lambda r: (r.get("race_date") or "", str(r.get("race_number") or "")))
    for r in rows:
        r["a_bet"] = (r.get("status") or "").strip() == "graded"
        r["s_bet"] = (r.get("second_status") or "").strip() == "graded"
        r["a_wag"] = num(r.get("wagered")) if r["a_bet"] else 0.0
        r["a_ret"] = num(r.get("returned")) if r["a_bet"] else 0.0
        r["s_wag"] = num(r.get("second_wagered")) if r["s_bet"] else 0.0
        r["s_ret"] = num(r.get("second_returned")) if r["s_bet"] else 0.0
        r["b_wag"], r["b_ret"] = r["a_wag"] + r["s_wag"], r["a_ret"] + r["s_ret"]
        r["a_fin"] = int(num(r.get("finish_position"))) if r["a_bet"] and r.get("finish_position") else None
        r["s_fin"] = int(num(r.get("second_finish"))) if r["s_bet"] and r.get("second_finish") else None
    return rows


def strategy_stats(races, wag_key, ret_key, won, cashed):
    races = [r for r in races if r[wag_key] > 0]
    n = len(races)
    wag = sum(r[wag_key] for r in races)
    ret = sum(r[ret_key] for r in races)
    streak = longest = 0
    for r in races:
        streak = streak + 1 if r[ret_key] - r[wag_key] < 0 else 0
        longest = max(longest, streak)
    return {
        "races": n, "wagered": wag, "returned": ret, "net": ret - wag,
        "roi": (ret - wag) / wag if wag else 0.0,
        "per_race": ret / n if n else 0.0,
        "win_rate": sum(1 for r in races if won(r)) / n if n else 0.0,
        "itm_rate": sum(1 for r in races if cashed(r)) / n if n else 0.0,
        "profit_rate": sum(1 for r in races if r[ret_key] > r[wag_key]) / n if n else 0.0,
        "best": max((r[ret_key] for r in races), default=0.0),
        "streak": streak, "longest": longest,
    }


def legs(races, prefix, bet_key):
    out = []
    graded = [r for r in races if r[bet_key]]
    for name, key in (("Win", "win_payout"), ("Place", "place_payout"), ("Show", "show_payout")):
        wag = 2.0 * len(graded)
        ret = sum(num(r.get(prefix + key)) for r in graded)
        out.append((name, wag, ret, (ret - wag) / wag if wag else 0.0))
    return out


def build(rows):
    """Return (index page html, {race page filename: html})."""
    hdir = os.path.join(HERE, "handicaps")
    write_ups = {f[:-3] for f in os.listdir(hdir) if f.endswith(".md")} if os.path.isdir(hdir) else set()
    graded = [r for r in rows if r["b_wag"] > 0]
    top = strategy_stats(graded, "a_wag", "a_ret",
                         lambda r: r["a_fin"] == 1, lambda r: r["a_ret"] > 0)
    two = strategy_stats(graded, "b_wag", "b_ret",
                         lambda r: r["a_fin"] == 1 or r["s_fin"] == 1, lambda r: r["b_ret"] > 0)
    sec = strategy_stats(graded, "s_wag", "s_ret",
                         lambda r: r["s_fin"] == 1, lambda r: r["s_ret"] > 0)
    pending = [r for r in rows if "pending" in ((r.get("status") or "").strip(),
                                                 (r.get("second_status") or "").strip())]

    # Chart series: cumulative net after each graded race, starting at $0.
    pts, a_cum, b_cum = [{"i": 0, "label": "Start", "a": 0.0, "b": 0.0}], 0.0, 0.0
    for i, r in enumerate(graded, start=1):
        a_cum += r["a_ret"] - r["a_wag"]
        b_cum += r["b_ret"] - r["b_wag"]
        pts.append({"i": i, "label": f'{r["race_date"][5:].replace("-", "/")} {r["track_code"]} R{r["race_number"]}',
                    "a": round(a_cum, 2), "b": round(b_cum, 2)})

    updated = datetime.now().strftime("%b %-d, %Y %-I:%M %p") if os.name != "nt" else \
        datetime.now().strftime("%b %#d, %Y %#I:%M %p")

    def tile(label, value, sub, cls=""):
        return (f'<div class="tile"><div class="tile-label">{label}</div>'
                f'<div class="tile-value {cls}">{value}</div><div class="tile-sub">{sub}</div></div>')

    def signcls(v):
        return "pos" if v > 0 else "neg" if v < 0 else ""

    def strat_card(title, key, s, per):
        return f'''
<section class="card strat">
  <h2><span class="swatch {key}"></span>{title} <span class="muted">({per} per race)</span></h2>
  <div class="tiles">
    {tile("Net", money(s["net"], True), f'{s["races"]} races', signcls(s["net"]))}
    {tile("ROI", pct(s["roi"], True), "net ÷ wagered", signcls(s["roi"]))}
    {tile("Win rate", pct(s["win_rate"]), "a pick won")}
    {tile("In the money", pct(s["itm_rate"]), "a ticket cashed")}
  </div>
  <dl class="kv">
    <dt>Wagered</dt><dd>{money(s["wagered"])}</dd>
    <dt>Returned</dt><dd>{money(s["returned"])}</dd>
    <dt>Avg return / race</dt><dd>{money(s["per_race"])}</dd>
    <dt>Profitable races</dt><dd>{pct(s["profit_rate"])}</dd>
    <dt>Biggest race</dt><dd>{money(s["best"])}</dd>
    <dt>Losing streak</dt><dd>{s["streak"]} now · {s["longest"]} longest</dd>
  </dl>
</section>'''

    def leg_table():
        a, s = legs(graded, "", "a_bet"), legs(graded, "second_", "s_bet")
        body = "".join(
            f'<tr><th scope="row">{a[i][0]}</th><td>{money(a[i][2])}</td>'
            f'<td class="{signcls(a[i][3])}">{pct(a[i][3], True)}</td>'
            f'<td>{money(s[i][2])}</td><td class="{signcls(s[i][3])}">{pct(s[i][3], True)}</td></tr>'
            for i in range(3))
        return (f'<table><thead><tr><th></th><th>Top pick<br>returned</th><th>ROI</th>'
                f'<th>2nd pick<br>returned</th><th>ROI</th></tr></thead><tbody>{body}</tbody></table>'
                f'<p class="note">Each pick is $2 to win, place and show. Wagered per leg = $2 × races.</p>')

    def finish_txt(fin, status):
        status = (status or "").strip()
        if status == "graded" and fin:
            return ordinal(fin)
        return status.replace("_", " ") or "–"

    def pick_line(label, key, horse, odds, fin, status, ret, wag):
        net = ret - wag
        result = (f'<span class="{signcls(net)}">{money(net, True)}</span>'
                  if (status or "").strip() == "graded" else "")
        return (f'<div class="pick"><span class="swatch {key}"></span>'
                f'<span class="pick-name">{esc(horse)} <span class="muted">({esc(odds)})</span></span>'
                f'<span class="pick-fin">{finish_txt(fin, status)}</span>'
                f'<span class="pick-net">{result}</span></div><div class="pick-label">{label}</div>')

    def race_card(r, upcoming=False, show_link=True):
        base = write_up_name(r)
        link = (f' · <a href="races/{base}.html">Handicap write-up</a>'
                if show_link and base in write_ups else "")
        date = datetime.strptime(r["race_date"], "%Y-%m-%d").strftime("%a %b %d")
        head = (f'<div class="race-head"><strong>{esc(r["track_name"])} R{esc(r["race_number"])}</strong>'
                f'<span class="muted">{date}</span></div>'
                f'<div class="race-sub muted">{esc(r.get("surface"))}</div>')
        picks = (pick_line("Top pick", "a", r["pick_horse"], r["pick_ml_odds"], r["a_fin"],
                           r.get("status"), r["a_ret"], r["a_wag"])
                 + pick_line("2nd pick", "s", r["second_choice"], r.get("second_ml_odds"), r["s_fin"],
                             r.get("second_status"), r["s_ret"], r["s_wag"]))
        if upcoming:
            foot = f'<div class="race-foot muted">Awaiting result{link}</div>'
        else:
            bnet = r["b_ret"] - r["b_wag"]
            winner = esc(r.get("winner"))
            wpay = num(r.get("winner_win_payout"))
            foot = (f'<div class="race-foot"><span>Top 2 net: <b class="{signcls(bnet)}">{money(bnet, True)}</b></span>'
                    f'<span class="muted">Won by {winner}{f" (${wpay:.2f})" if wpay else ""}{link}</span></div>')
        return f'<article class="race">{head}{picks}{foot}</article>'

    upcoming_html = "".join(race_card(r, True) for r in reversed(pending)) or \
        '<p class="muted">No pick pending. The next one posts after the 9 AM run.</p>'
    history_html = "".join(race_card(r) for r in reversed(graded)) or \
        '<p class="muted">No graded races yet.</p>'
    added = two["net"] - top["net"]

    pages = {}
    for r in rows:
        base = write_up_name(r)
        if base not in write_ups:
            continue
        with open(os.path.join(hdir, base + ".md"), encoding="utf-8") as f:
            text = f.read()
        m = re.search(r"^#\s+(.+)$", text, re.M)
        title = m.group(1).strip() if m else f'{r["track_name"]} R{r["race_number"]}'
        text = re.sub(r"^#\s+.+$", "", text, count=1, flags=re.M)  # shown as the page title
        is_pending = "pending" in ((r.get("status") or "").strip(), (r.get("second_status") or "").strip())
        pages[base + ".html"] = RACE_TEMPLATE.format(
            css=SHARED_CSS, icon_tags=icon_tags("../"), title=esc(title), updated=updated,
            card=race_card(r, is_pending, show_link=False), body=md_to_html(text))

    index_html = TEMPLATE.format(
        icon_tags=icon_tags(),
        updated=updated,
        n_races=two["races"],
        headline_top=money(top["net"], True), headline_top_cls=signcls(top["net"]),
        headline_two=money(two["net"], True), headline_two_cls=signcls(two["net"]),
        added=money(added, True), added_cls=signcls(added),
        sec_net=money(sec["net"], True), sec_roi=pct(sec["roi"], True),
        strat_top=strat_card("Top Pick", "a", top, "$6"),
        strat_two=strat_card("Top 2 Picks", "b", two, "$12"),
        legs=leg_table(),
        upcoming=upcoming_html, history=history_html,
        data=json.dumps(pts),
    )
    return index_html, pages


def write_up_name(r):
    return f'{r["race_date"]}_{r["track_code"]}_R{r["race_number"]}'


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DRF Race Tracker</title>
{icon_tags}
<meta name="description" content="Daily DRF Race of the Day picks and $2 Win/Place/Show results: top pick vs top 2 picks.">
<style>
:root {{
  color-scheme: light;
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --border: rgba(11,11,11,0.10);
  --pos: #006300; --neg: #c0302f;
  --series-a: #2a78d6; --series-b: #eb6834; --series-s: #1baf7a;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --border: rgba(255,255,255,0.10);
    --pos: #0ca30c; --neg: #e66767;
    --series-a: #3987e5; --series-b: #d95926; --series-s: #199e70;
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --border: rgba(255,255,255,0.10);
  --pos: #0ca30c; --neg: #e66767;
  --series-a: #3987e5; --series-b: #d95926; --series-s: #199e70;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--page); color: var(--ink);
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif; }}
main {{ max-width: 760px; margin: 0 auto; padding: 16px 16px 48px; }}
h1 {{ font-size: 22px; margin: 4px 0 2px; }}
h2 {{ font-size: 16px; margin: 0 0 12px; display: flex; align-items: center; gap: 8px; }}
h3 {{ font-size: 15px; margin: 28px 0 10px; color: var(--ink-2); text-transform: uppercase; letter-spacing: .04em; }}
.muted {{ color: var(--muted); font-weight: normal; }}
.pos {{ color: var(--pos); }} .neg {{ color: var(--neg); }}
a {{ color: var(--series-a); }}
.card, .race {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 12px; }}
.hero {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0 12px; }}
.hero .card {{ margin: 0; }}
.hero-label {{ font-size: 13px; color: var(--ink-2); display: flex; align-items: center; gap: 6px; }}
.hero-value {{ font-size: 30px; font-weight: 700; margin-top: 2px; }}
.added {{ font-size: 14px; color: var(--ink-2); margin: 0 0 12px; }}
.swatch {{ width: 10px; height: 10px; border-radius: 3px; display: inline-block; flex: none; }}
.swatch.a {{ background: var(--series-a); }} .swatch.b {{ background: var(--series-b); }} .swatch.s {{ background: var(--series-s); }}
.tiles {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }}
.tile {{ background: var(--page); border-radius: 8px; padding: 8px; text-align: center; }}
.tile-label {{ font-size: 11px; color: var(--ink-2); text-transform: uppercase; letter-spacing: .03em; }}
.tile-value {{ font-size: 18px; font-weight: 700; }}
.tile-sub {{ font-size: 11px; color: var(--muted); }}
.kv {{ display: grid; grid-template-columns: 1fr auto; gap: 4px 12px; margin: 12px 0 0; font-size: 14px; }}
.kv dt {{ color: var(--ink-2); }} .kv dd {{ margin: 0; text-align: right; font-variant-numeric: tabular-nums; }}
.legend {{ display: flex; gap: 16px; font-size: 13px; color: var(--ink-2); margin-bottom: 6px; }}
.legend span {{ display: flex; align-items: center; gap: 6px; }}
.chart-wrap {{ position: relative; }}
svg {{ display: block; width: 100%; height: auto; touch-action: pan-y; }}
.tip {{ position: absolute; pointer-events: none; background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 6px 8px; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,.12); display: none; white-space: nowrap; }}
.tip b {{ display: block; margin-bottom: 2px; }}
.tip div {{ display: flex; align-items: center; gap: 6px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; font-variant-numeric: tabular-nums; }}
th, td {{ padding: 6px 4px; text-align: right; border-bottom: 1px solid var(--grid); }}
th:first-child, td:first-child {{ text-align: left; }}
thead th {{ font-size: 12px; color: var(--ink-2); font-weight: 600; }}
.note {{ font-size: 12px; color: var(--muted); margin: 8px 0 0; }}
.race-head {{ display: flex; justify-content: space-between; gap: 8px; }}
.race-sub {{ font-size: 13px; margin-bottom: 8px; }}
.pick {{ display: grid; grid-template-columns: auto 1fr auto auto; align-items: center; gap: 8px; margin-top: 6px; }}
.pick-name {{ font-weight: 600; }}
.pick-fin {{ color: var(--ink-2); font-size: 14px; }}
.pick-net {{ min-width: 64px; text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; }}
.pick-label {{ font-size: 11px; color: var(--muted); margin-left: 18px; }}
.race-foot {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 4px 12px; font-size: 13px;
  margin-top: 10px; padding-top: 8px; border-top: 1px solid var(--grid); }}
.sr {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }}
@media (max-width: 480px) {{
  .tiles {{ grid-template-columns: repeat(2, 1fr); }}
  .hero-value {{ font-size: 24px; }}
}}
</style>
</head>
<body>
<main>
  <h1>DRF Race of the Day Tracker</h1>
  <div class="muted">Updated {updated} · {n_races} races graded</div>

  <div class="hero">
    <div class="card"><div class="hero-label"><span class="swatch a"></span>Top Pick net</div>
      <div class="hero-value {headline_top_cls}">{headline_top}</div></div>
    <div class="card"><div class="hero-label"><span class="swatch b"></span>Top 2 Picks net</div>
      <div class="hero-value {headline_two_cls}">{headline_two}</div></div>
  </div>
  <p class="added">Adding the 2nd pick changed the net by <b class="{added_cls}">{added}</b>.
    The 2nd pick on its own: <b>{sec_net}</b> ({sec_roi} ROI).</p>

  <section class="card">
    <h2>Cumulative net by race</h2>
    <div class="legend"><span><span class="swatch a"></span>Top Pick</span><span><span class="swatch b"></span>Top 2 Picks</span></div>
    <div class="chart-wrap" id="chart"></div>
  </section>

  <h3>Next pick</h3>
  {upcoming}

  <h3>Strategies</h3>
  {strat_top}
  {strat_two}

  <h3>Return by bet type</h3>
  <section class="card">{legs}</section>

  <h3>Race history</h3>
  {history}

  <p class="note">Top Pick = $2 Win + $2 Place + $2 Show on the top pick from the handicap-race method.
    Top 2 Picks = the same on the top pick and the second choice. Scratched picks are refunded.
    Morning-line odds shown. For tracking only; no real bets placed.</p>
</main>
<script>
const pts = {data};
let resizeTimer;
drawChart();
addEventListener("resize", () => {{ clearTimeout(resizeTimer); resizeTimer = setTimeout(drawChart, 150); }});
function drawChart() {{
  const el = document.getElementById("chart");
  const css = getComputedStyle(document.documentElement);
  // Size the drawing to the real container width so text stays 12px on phones.
  const W = Math.max(300, Math.round(el.clientWidth || 700)), H = W < 500 ? 220 : 280;
  const m = {{l: 52, r: 16, t: 12, b: 28}};
  const vals = pts.flatMap(p => [p.a, p.b]).concat([0]);
  let lo = Math.min(...vals), hi = Math.max(...vals);
  if (hi - lo < 10) {{ hi += 5; lo -= 5; }}
  const step = niceStep((hi - lo) / 4);
  lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step;
  const n = Math.max(pts.length - 1, 1);
  const x = i => m.l + (W - m.l - m.r) * i / n;
  const y = v => m.t + (H - m.t - m.b) * (hi - v) / (hi - lo);
  const fmt = v => (v < 0 ? "−$" : "$") + Math.abs(v).toFixed(0);
  let g = "";
  for (let v = lo; v <= hi + 1e-9; v += step) {{
    g += `<line x1="${{m.l}}" x2="${{W - m.r}}" y1="${{y(v)}}" y2="${{y(v)}}" stroke="var(${{v === 0 ? "--axis" : "--grid"}})" stroke-width="1"/>`;
    g += `<text x="${{m.l - 8}}" y="${{y(v) + 4}}" text-anchor="end" font-size="12" fill="var(--muted)">${{fmt(v)}}</text>`;
  }}
  const every = Math.max(1, Math.ceil(n / 8));
  pts.forEach(p => {{ if (p.i % every === 0 || p.i === n)
    g += `<text x="${{x(p.i)}}" y="${{H - 8}}" text-anchor="middle" font-size="12" fill="var(--muted)">${{p.i}}</text>`; }});
  const path = k => pts.map((p, i) => `${{i ? "L" : "M"}}${{x(p.i).toFixed(1)}},${{y(p[k]).toFixed(1)}}`).join("");
  const last = pts[pts.length - 1];
  g += `<path d="${{path("b")}}" fill="none" stroke="var(--series-b)" stroke-width="2" stroke-linejoin="round"/>`;
  g += `<path d="${{path("a")}}" fill="none" stroke="var(--series-a)" stroke-width="2" stroke-linejoin="round"/>`;
  ["b", "a"].forEach(k => g += `<circle cx="${{x(last.i)}}" cy="${{y(last[k])}}" r="4" fill="var(--series-${{k}})" stroke="var(--surface)" stroke-width="2"/>`);
  g += `<line id="xh" y1="${{m.t}}" y2="${{H - m.b}}" stroke="var(--axis)" stroke-width="1" visibility="hidden"/>`;
  g += `<rect x="${{m.l}}" y="0" width="${{W - m.l - m.r}}" height="${{H}}" fill="transparent" id="hit"/>`;
  el.innerHTML = `<svg viewBox="0 0 ${{W}} ${{H}}" role="img" aria-label="Cumulative net by race for both strategies">${{g}}</svg><div class="tip" id="tip"></div>` +
    `<table class="sr"><tr><th>Race</th><th>Top Pick</th><th>Top 2</th></tr>${{pts.map(p => `<tr><td>${{p.label}}</td><td>${{p.a}}</td><td>${{p.b}}</td></tr>`).join("")}}</table>`;
  const svg = el.querySelector("svg"), tip = el.querySelector("#tip"), xh = el.querySelector("#xh");
  function show(evt) {{
    const r = svg.getBoundingClientRect();
    const cx = ((evt.touches ? evt.touches[0].clientX : evt.clientX) - r.left) * W / r.width;
    const i = Math.max(0, Math.min(n, Math.round((cx - m.l) / (W - m.l - m.r) * n)));
    const p = pts[i]; if (!p) return;
    xh.setAttribute("x1", x(p.i)); xh.setAttribute("x2", x(p.i)); xh.setAttribute("visibility", "visible");
    const money = v => (v < 0 ? "−$" : v > 0 ? "+$" : "$") + Math.abs(v).toFixed(2);
    tip.innerHTML = `<b>${{p.label}}</b><div><span class="swatch a"></span>Top Pick ${{money(p.a)}}</div><div><span class="swatch b"></span>Top 2 ${{money(p.b)}}</div>`;
    tip.style.display = "block";
    const px = x(p.i) * r.width / W, tw = tip.offsetWidth;
    tip.style.left = Math.max(0, Math.min(r.width - tw, px - tw / 2)) + "px";
    tip.style.top = "0px";
  }}
  function hide() {{ tip.style.display = "none"; xh.setAttribute("visibility", "hidden"); }}
  const hit = el.querySelector("#hit");
  hit.addEventListener("mousemove", show); hit.addEventListener("touchstart", show, {{passive: true}});
  hit.addEventListener("touchmove", show, {{passive: true}}); hit.addEventListener("mouseleave", hide);
  function niceStep(raw) {{
    const p = Math.pow(10, Math.floor(Math.log10(raw))); const f = raw / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10) * p;
  }}
}}
</script>
</body>
</html>
"""


def icon_tags(prefix=""):
    """Home-screen icon, favicon and app manifest links (prefix '../' for race pages)."""
    return (f'<link rel="icon" href="{prefix}icon.svg" type="image/svg+xml">\n'
            f'<link rel="icon" href="{prefix}favicon-32.png" sizes="32x32" type="image/png">\n'
            f'<link rel="apple-touch-icon" href="{prefix}apple-touch-icon.png">\n'
            f'<link rel="manifest" href="{prefix}manifest.webmanifest">\n'
            '<meta name="theme-color" content="#1f4e3d">\n'
            '<meta name="apple-mobile-web-app-title" content="Winners">\n'
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">')


SHARED_CSS = re.search(r"<style>(.*?)</style>", TEMPLATE, re.S).group(1) \
    .replace("{{", "{").replace("}}", "}")

RACE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{icon_tags}
<style>{css}
.back {{ display: inline-block; margin: 4px 0 10px; font-size: 14px; text-decoration: none; }}
.prose h2 {{ display: block; font-size: 17px; margin: 22px 0 8px; }}
.prose h2:first-child {{ margin-top: 0; }}
.prose h3, .prose h4 {{ font-size: 15px; margin: 18px 0 6px; text-transform: none; letter-spacing: 0; color: var(--ink); }}
.prose p, .prose li {{ margin: 0 0 10px; }}
.prose ul, .prose ol {{ padding-left: 20px; margin: 0 0 10px; }}
.prose a {{ overflow-wrap: anywhere; }}
.prose code {{ font-size: 13px; background: var(--page); padding: 1px 4px; border-radius: 4px; }}
.table-wrap {{ overflow-x: auto; margin: 0 0 12px; }}
.prose table {{ font-size: 13px; }}
.prose td, .prose th {{ text-align: left; vertical-align: top; }}
</style>
</head>
<body>
<main>
  <a class="back" href="../">← All races</a>
  <h1>{title}</h1>
  <div class="muted" style="margin-bottom:12px">Updated {updated}</div>
  {card}
  <article class="card prose">{body}</article>
  <a class="back" href="../">← All races</a>
</main>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(HERE, "ledger.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "docs", "index.html"))
    args = ap.parse_args()
    rows = load(args.csv)
    index_html, pages = build(rows)
    out_dir = os.path.dirname(os.path.abspath(args.out))
    races_dir = os.path.join(out_dir, "races")
    os.makedirs(races_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(index_html)
    for name, page in pages.items():
        with open(os.path.join(races_dir, name), "w", encoding="utf-8") as f:
            f.write(page)
    for stale in set(os.listdir(races_dir)) - set(pages):  # write-up removed from the ledger
        if stale.endswith(".html"):
            os.remove(os.path.join(races_dir, stale))
    print(f"Wrote {args.out} and {len(pages)} race pages: "
          f"{sum(1 for r in rows if r['b_wag'] > 0)} graded races.")


if __name__ == "__main__":
    main()
