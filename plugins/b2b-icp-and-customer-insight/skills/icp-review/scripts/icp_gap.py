"""icp_gap.py: metric gaps between today's customers and the ICP targets.

Usage: python icp_gap.py FILE.json      (or - to read standard input)

Input (JSON object):
  {"current": {"acv": 30000, "cycle": 90, "win_rate": 18, "churn": 14, "nps": 22},
   "target":  {"acv": 45000, "cycle": 60, "win_rate": 25, "churn": 8, "nps": 40},
   "bands": {"acv": [50, 25]}}            (optional: your own High and Medium bands per metric)

Metrics: acv (0 or more), cycle in days (0 or more), win_rate in % (0 to 100), churn in % (0 to 100), nps (-100 to 100).
Gaps: ACV % = (target minus current) divided by current, times 100; cycle and churn as reductions, (current minus target)
divided by current, times 100; win rate as a relative change, with the points difference beside it; NPS in points (target minus current).
A metric is compared only when both values are given; a base of 0 gives "n/a".
Priority bands are example defaults (ACV 50 and 25, cycle 30 and 15, win rate 40 and 20, churn 40 and 20, NPS 50 and 25
on its relative change) that you can replace. The largest gap is chosen among the percentage gaps; the NPS points gap is
reported on its own line and never ranked against percentages.
Exit codes: 0 done; 1 FAIL (0 metrics compared); 2 bad input. Standard library only; no network; writes no files.
"""
import json, math, sys
from decimal import Decimal, ROUND_HALF_UP

METRICS = ["acv", "cycle", "win_rate", "churn", "nps"]
NAMES = {"acv": "Average contract value", "cycle": "Sales cycle (days)", "win_rate": "Win rate (%)", "churn": "Churn (%)", "nps": "NPS"}
RANGES = {"acv": (0, None), "cycle": (0, None), "win_rate": (0, 100), "churn": (0, 100), "nps": (-100, 100)}
DEFAULT_BANDS = {"acv": (50, 25), "cycle": (30, 15), "win_rate": (40, 20), "churn": (40, 20), "nps": (50, 25)}
UP = {"acv", "win_rate", "nps"}   # higher is better; cycle and churn: lower is better


class BadInput(Exception):
    pass


def half_up(x):
    return int(Decimal(repr(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def num(v, where):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise BadInput(f"{where} must be a number, got {json.dumps(v)}")
    if isinstance(v, float) and not math.isfinite(v):
        raise BadInput(f"{where} must be a finite number")
    return v


def fmt(v):
    return f"{v:,.0f}" if float(v).is_integer() else f"{v:,.2f}"


def analyse(data):
    if not isinstance(data, dict):
        raise BadInput("the input must be a JSON object with 'current' and 'target'")
    for k in data:
        if k not in ("current", "target", "bands"):
            raise BadInput(f"unknown key '{k}' (allowed: current, target, bands)")
    sides = {}
    for side in ("current", "target"):
        obj = data.get(side, {})
        if obj is None:
            obj = {}
        if not isinstance(obj, dict):
            raise BadInput(f"'{side}' must be an object of metrics")
        clean = {}
        for k, v in obj.items():
            if k not in METRICS:
                raise BadInput(f"unknown metric '{k}' in {side} (allowed: {', '.join(METRICS)})")
            if v is None:
                continue
            v = num(v, f"{k} in {side}")
            lo, hi = RANGES[k]
            if v < lo or (hi is not None and v > hi):
                raise BadInput(f"{k} in {side} is {v}; it must be between {lo} and {hi}" if hi is not None else f"{k} in {side} is {v}; it cannot be negative")
            clean[k] = v
        sides[side] = clean
    bands, user_bands = dict(DEFAULT_BANDS), set()
    raw_b = data.get("bands") or {}
    if not isinstance(raw_b, dict):
        raise BadInput("'bands' must be an object such as {\"acv\": [50, 25]}")
    for k, pair in raw_b.items():
        if k not in METRICS:
            raise BadInput(f"unknown metric '{k}' in bands")
        if not isinstance(pair, list) or len(pair) != 2:
            raise BadInput(f"bands for {k} must be two numbers [High above, Medium above]")
        hi, me = num(pair[0], f"High band for {k}"), num(pair[1], f"Medium band for {k}")
        if hi < me:
            raise BadInput(f"bands for {k}: the High band must be at least the Medium band")
        bands[k] = (hi, me); user_bands.add(k)

    rows = []
    for m in METRICS:
        c, t = sides["current"].get(m), sides["target"].get(m)
        row = {"metric": m, "name": NAMES[m], "current": c, "target": t, "status": "compared", "met": False, "ranked": False,
               "gap": None, "text": "", "band": "", "band_source": "your bands" if m in user_bands else "example default bands"}
        if c is None or t is None:
            gone = " and ".join(s for s, v in (("current", c), ("target", t)) if v is None)
            row.update(status="missing", text=f"missing: no {gone} value given, not compared", band="not compared")
            rows.append(row); continue
        hi, me = bands[m]
        if m == "nps":
            pts = t - c
            row["gap"] = pts
            row["text"] = f"+{fmt(pts)} points needed" if pts > 0 else ("target met" if pts == 0 else f"target met: already {fmt(-pts)} points above target")
            row["met"] = pts <= 0
            if row["met"]:
                row["band"] = "None (target met)"
            elif c <= 0:
                row["band"] = "Not rated (today's NPS is 0 or below, so a relative change means nothing)"
            else:
                rel = half_up((t - c) / c * 100)
                row["band"] = ("High" if rel > hi else "Medium" if rel > me else "Low") + f" (on the relative change, {rel}%)"
            rows.append(row); continue
        diff = (t - c) if m in UP else (c - t)
        if diff <= 0:   # met or better, decided on the raw values, never on a rounded gap
            row["met"] = True
            row["band"] = "None (target met)"
            better_by = half_up(-diff / c * 100) if c > 0 else 0
            row["gap"] = -better_by
            row["text"] = f"target met: already {better_by}% better than target" if better_by > 0 else "target met"
            rows.append(row); continue
        if c == 0:
            row.update(status="n/a", text="n/a: today's value is 0, so no percentage can be taken", band="Not rated")
            rows.append(row); continue
        g = half_up(diff / c * 100)
        row["gap"] = g
        if g == 0:   # behind by less than half a percent: still behind, never shown as met
            row["gap"] = 0.5
            row["ranked"] = True
            row["band"] = "Low"
            row["text"] = "less than 1% increase needed" if m in UP else "less than 1% reduction needed"
        else:
            row["ranked"] = True
            row["band"] = "High" if g > hi else "Medium" if g > me else "Low"
            if m == "acv":
                row["text"] = f"+{g}% increase needed"
            elif m == "win_rate":
                row["text"] = f"+{g}% relative increase needed (+{fmt(t - c)} points)"
            else:
                row["text"] = f"{g}% reduction needed"
        rows.append(row)
    compared = [r for r in rows if r["status"] != "missing"]
    if not compared:
        return {"rows": rows, "largest": None, "compared": 0}
    ranked = [r for r in rows if r["ranked"]]
    largest = max(ranked, key=lambda r: r["gap"])["metric"] if ranked else None
    ties = [r["metric"] for r in ranked if largest and r["gap"] == next(x["gap"] for x in ranked if x["metric"] == largest)]
    return {"rows": rows, "largest": largest, "largest_ties": ties if len(ties) > 1 else [], "compared": len(compared)}


def render(res):
    out = ["ICP metric gaps (icp_gap.py)", ""]
    out.append("| Metric | Today | Target | Gap | Priority |")
    out.append("|---|---|---|---|---|")
    for r in res["rows"]:
        cur = "missing" if r["current"] is None else fmt(r["current"])
        tgt = "missing" if r["target"] is None else fmt(r["target"])
        out.append(f"| {r['name']} | {cur} | {tgt} | {r['text']} | {r['band']} |")
    out.append("")
    if res["largest"]:
        names = [NAMES[m] for m in (res.get("largest_ties") or [res["largest"]])]
        out.append(f"Largest percentage gap: {' and '.join(names)} (tied)" if len(names) > 1 else f"Largest percentage gap: {names[0]}")
    else:
        out.append("Largest percentage gap: none (no percentage metric is behind its target)")
    nps = next(r for r in res["rows"] if r["metric"] == "nps")
    if nps["status"] == "compared":
        out.append(f"NPS is measured in points, so it is reported on its own and not ranked against the percentages: {nps['text']}.")
    srcs = sorted({r["band_source"] for r in res["rows"] if r["status"] == "compared" and not r["met"]})
    if srcs:
        out.append("Priority bands used: " + " and ".join(srcs) + (". The example default bands (ACV 50 and 25, cycle 30 and 15, win rate 40 and 20, churn 40 and 20, NPS 50 and 25) are starting examples, not a benchmark; replace them with your own." if "example default bands" in srcs else "."))
    missing = [r["name"] for r in res["rows"] if r["status"] == "missing"]
    if missing:
        out.append("Not compared (a value is missing): " + ", ".join(missing) + ".")
    return "\n".join(out)


def main(argv):
    for stream in (sys.stdout, sys.stdin):   # run 32C: UTF-8 on Windows consoles and pipes, so non Latin text never gives a traceback
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print("Usage: python icp_gap.py FILE.json (or - for standard input)"); return 2
    try:
        text = sys.stdin.read().lstrip("﻿") if argv[1] == "-" else open(argv[1], encoding="utf-8-sig").read()
    except OSError as e:
        print(f"Bad input: cannot read the file ({e.strerror})"); return 2

    def no_const(c):
        raise BadInput(f"{c} is not a number this script accepts")
    try:
        data = json.loads(text, parse_constant=no_const)
        res = analyse(data)
    except json.JSONDecodeError as e:
        print(f"Bad input: not valid JSON (line {e.lineno}, column {e.colno})"); return 2
    except BadInput as e:
        print(f"Bad input: {e}"); return 2
    if res["compared"] == 0:
        print("FAIL: 0 metrics compared. Give both today's value and the target for at least one metric."); return 1
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
