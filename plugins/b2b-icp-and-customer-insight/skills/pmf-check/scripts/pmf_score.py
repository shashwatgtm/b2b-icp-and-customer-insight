"""pmf_score.py: compare product market fit metrics with the team's OWN targets, never with a published range.

Usage: python pmf_score.py FILE.json      (or - to read standard input)

Input (JSON object):
  {"business_model": "saas",                         (optional: saas, services, connectivity, transactions, marketplace, hardware_software, investment)
   "metrics": {"churn": 2.5, "nps": 31, "ltv": 90000, "cac": 30000, "retention": 88, "activation": 45},
   "targets": {"churn": 2, "nps": 40, "ltv_cac": 4, "retention": 92, "activation": 60},
   "custom": [{"name": "Revenue growth (%)", "value": -12, "target": 20, "better": "higher"}]}

Standard dimensions: churn in % (lower is better), nps (-100 to 100, in points), ltv_cac (derived from ltv and cac, or given),
retention in % (higher), activation in % (higher; not applicable for services, connectivity and investment models).
A dimension is scored only when the value and the user's own target are both given. Gaps: higher is better,
(target minus value) divided by value, times 100, as an increase needed; lower is better, (value minus target) divided by
value, times 100, as a reduction needed; NPS in points and never ranked against percentages; a value of 0 gives "n/a".
No stage label and no range table: the result is how many dimensions meet the user's targets and the weakest one.
Exit codes: 0 done; 1 FAIL (0 dimensions scored); 2 bad input. Standard library only; no network; writes no files.
"""
import json, math, sys
from decimal import Context, Decimal, ROUND_HALF_UP

STD = [("churn", "Churn (%)", "lower", (0, 100)), ("nps", "NPS", "higher", (-100, 100)), ("ltv_cac", "LTV to CAC ratio", "higher", (0, None)),
       ("retention", "Retention (%)", "higher", (0, 1000)), ("activation", "Activation (%)", "higher", (0, 100))]
INPUT_ONLY = {"ltv": (0, None), "cac": (0, None)}
MODELS = {"saas", "services", "connectivity", "transactions", "marketplace", "hardware_software", "investment"}
NO_ACTIVATION = {"services", "connectivity", "investment"}


class BadInput(Exception):
    pass


def half_up(x):
    return int(Decimal(repr(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP, context=Context(prec=400)))   # run 32C: no traceback on a tiny base


def num(v, where, rng=None):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise BadInput(f"{where} must be a number, got {json.dumps(v)}")
    if isinstance(v, float) and not math.isfinite(v):
        raise BadInput(f"{where} must be a finite number")
    if rng:
        lo, hi = rng
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            raise BadInput(f"{where} is {v}; it must be " + (f"between {lo} and {hi}" if hi is not None else f"{lo} or more"))
    return v


def fmt(v):
    if float(v).is_integer():
        return f"{v:,.0f}"
    two = f"{v:,.2f}"
    return two if not two.endswith(".00") else f"{v:,.4g}"   # never show 3.999 as 4.00


def compare(key, name, better, value, target):
    row = {"dimension": key, "name": name, "value": value, "target": target, "better": better, "status": "", "text": "", "gap": None}
    if value is None or target is None:
        missing = " and ".join(s for s, v in (("value", value), ("target of yours", target)) if v is None)
        row.update(status="no target" if value is not None and target is None else "missing", text=f"not scored: no {missing} given")
        return row
    if key == "nps":
        pts = target - value
        row["gap"] = None
        row.update(status="met" if pts <= 0 else "behind", text="target met" if pts <= 0 else f"+{fmt(pts)} points needed")
        return row
    diff = (target - value) if better == "higher" else (value - target)
    if diff <= 0:   # met or better, decided on the raw values, never on a rounded gap
        row.update(status="met", text="target met")
        return row
    if value == 0:
        row.update(status="n/a", text="n/a: the value is 0, so no percentage can be taken")
        return row
    g = half_up(diff / abs(value) * 100)   # the size of the value, sign ignored, is the base
    word = "increase" if better == "higher" else "reduction"
    if g == 0:   # behind by less than half a percent: still behind, never shown as met
        row.update(status="behind", gap=0.5, text=f"less than 1% {word} needed")
    else:
        row.update(status="behind", gap=g, text=(f"+{g}% " if better == "higher" else f"{g}% ") + f"{word} needed")
    return row


def check(data):
    if not isinstance(data, dict):
        raise BadInput("the input must be a JSON object with 'metrics' and 'targets'")
    for k in data:
        if k not in ("business_model", "metrics", "targets", "custom"):
            raise BadInput(f"unknown key '{k}' (allowed: business_model, metrics, targets, custom)")
    model = data.get("business_model")
    if model is not None and model not in MODELS:
        raise BadInput(f"business_model must be exactly one of {', '.join(sorted(MODELS))} (got {json.dumps(model)})")
    ranges = {k: r for k, _, _, r in STD}
    ranges.update(INPUT_ONLY)
    vals = {}
    for side in ("metrics", "targets"):
        obj = data.get(side) or {}
        if not isinstance(obj, dict):
            raise BadInput(f"'{side}' must be an object")
        vals[side] = {}
        for k, v in obj.items():
            allowed = ranges if side == "metrics" else {k2: r for k2, _, _, r in STD}
            if k not in allowed:
                raise BadInput(f"unknown {side[:-1]} '{k}' (allowed: {', '.join(allowed)})")
            if v is not None:
                vals[side][k] = num(v, f"{k} in {side}", allowed[k])
    m, t = vals["metrics"], vals["targets"]
    if "ltv_cac" not in m and "ltv" in m and "cac" in m and m["cac"] > 0:
        m["ltv_cac"] = m["ltv"] / m["cac"]   # run 32C: raw ratio for the comparison; rounded only for display
    rows = []
    for key, name, better, _ in STD:
        if key == "activation" and model in NO_ACTIVATION:
            rows.append({"dimension": key, "name": name, "value": m.get(key), "target": t.get(key), "better": better, "status": "not applicable",
                         "text": f"not applicable for a {model} business: use the adoption measure your buyers use", "gap": None})
            continue
        if key == "ltv_cac" and "ltv_cac" not in m and ("ltv" in m or "cac" in m):
            rows.append({"dimension": key, "name": name, "value": None, "target": t.get(key), "better": better, "status": "missing",
                         "text": "not scored: needs both LTV and CAC, and CAC above 0", "gap": None})
            continue
        rows.append(compare(key, name, better, m.get(key), t.get(key)))
    custom = data.get("custom") or []
    if not isinstance(custom, list):
        raise BadInput("'custom' must be a list")
    for i, c in enumerate(custom, 1):
        if not isinstance(c, dict):
            raise BadInput(f"custom dimension {i} must be an object")
        name = c.get("name")
        if not isinstance(name, str) or not name.strip():
            raise BadInput(f"custom dimension {i} needs a name")
        if c.get("better") not in ("higher", "lower"):
            raise BadInput(f"custom dimension '{name}': 'better' must be exactly higher or lower")
        v = None if c.get("value") is None else num(c["value"], f"value of '{name}'")
        tg = None if c.get("target") is None else num(c["target"], f"target of '{name}'")
        rows.append(compare(f"custom:{name}", name.strip(), c["better"], v, tg))
    scored = [r for r in rows if r["status"] in ("met", "behind", "n/a")]
    met = [r for r in rows if r["status"] == "met"]
    ranked = [r for r in rows if r["status"] == "behind" and r["gap"] is not None]
    top = max((r["gap"] for r in ranked), default=None)
    ties = [r["dimension"] for r in ranked if r["gap"] == top]
    weakest = ties[0] if ties else None
    return {"rows": rows, "scored": len(scored), "met": len(met), "weakest": weakest, "weakest_ties": ties if len(ties) > 1 else [], "model": model}


def render(res):
    out = ["PMF check against your own targets (pmf_score.py)", "", "| Dimension | Your value | Your target | Gap | Status |", "|---|---|---|---|---|"]
    for r in res["rows"]:
        v = "not given" if r["value"] is None else fmt(r["value"])
        tg = "not given" if r["target"] is None else fmt(r["target"])
        out.append(f"| {r['name']} | {v} | {tg} | {r['text']} | {r['status']} |")
    out += ["", f"{res['met']} of {res['scored']} scored dimensions meet your own targets."]
    if res["weakest"]:
        names = [next(r["name"] for r in res["rows"] if r["dimension"] == d) for d in (res["weakest_ties"] or [res["weakest"]])]
        out.append(f"Furthest behind (largest percentage gap): {' and '.join(names)}" + (" (tied)." if len(names) > 1 else "."))
    nps = next(r for r in res["rows"] if r["dimension"] == "nps")
    if nps["status"] == "behind":
        out.append(f"NPS is in points, so it is reported on its own and not ranked against the percentages: {nps['text']}.")
    out.append("Every comparison is against your own targets. No published range or benchmark is used, and no stage label is given.")
    gaps = [r["name"] for r in res["rows"] if r["status"] in ("missing", "no target")]
    if gaps:
        out.append("Not scored (a value or your target is missing): " + ", ".join(gaps) + ".")
    return "\n".join(out)


def main(argv):
    for stream in (sys.stdout, sys.stdin):   # run 32C: UTF-8 on Windows consoles and pipes, so non Latin text never gives a traceback
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print("Usage: python pmf_score.py FILE.json (or - for standard input)"); return 2
    try:
        text = sys.stdin.read().lstrip("﻿") if argv[1] == "-" else open(argv[1], encoding="utf-8-sig").read()
    except OSError as e:
        print(f"Bad input: cannot read the file ({e.strerror})"); return 2

    def no_const(c):
        raise BadInput(f"{c} is not a number this script accepts")
    try:
        res = check(json.loads(text, parse_constant=no_const))
    except json.JSONDecodeError as e:
        print(f"Bad input: not valid JSON (line {e.lineno}, column {e.colno})"); return 2
    except BadInput as e:
        print(f"Bad input: {e}"); return 2
    if res["scored"] == 0:
        print("FAIL: 0 dimensions scored. Give at least one metric together with your own target for it."); return 1
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
