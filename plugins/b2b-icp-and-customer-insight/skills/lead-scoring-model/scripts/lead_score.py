"""lead_score.py: a fit scoring model with points and tiers, and optional scoring of leads or accounts on it.

Usage: python lead_score.py FILE.json      (or - to read standard input)

Input (JSON object):
  {"criteria": [
     {"criterion": "Fleet size", "importance": "critical", "values": ["500 or more", "100 to 499", "under 100"]},
     {"criterion": "Region", "weight": 12, "values": ["India", "Southeast Asia"], "graded": false},
     {"criterion": "Stage", "weight": 20, "values": [{"value": "Series B", "points": 20}, {"value": "Seed", "points": 5}]}],
   "default_weights": {"critical": 25, "important": 15, "nice_to_have": 10},   (optional: your own weights per importance)
   "leads": [{"label": "Lead 1", "values": {"Fleet size": "100 to 499", "Region": "India", "Stage": "Seed"}}]}

Example defaults (starting examples, not a benchmark; replace them): importance weights critical 25, important 15,
nice to have 10. A criterion with no importance is scored as nice to have and labelled so, never as important.
Graded points for values listed best first: round half up of weight x (n - 1 - i) / (n - 1); "graded": false gives every
value the full weight; explicit points are kept as yours. Tiers: A from ceil(0.8 x max), B from ceil(0.6 x max),
C from ceil(0.4 x max), D below, computed exactly; "tier_percents": [A, B, C] replaces the example bands with yours.
Tier reading (run 34C): for tiers A, B and C the script prints the fewest criteria at full points that can reach the tier, with one
example pattern, and any criterion the tier cannot be reached without; copy these lines instead of writing a tier rule by hand
(not computed above 200,000 combinations of values, and it says so).
A lead value may be text or a plain number (a number is matched as its text); a placeholder such as N/A, unknown or TBD
counts as missing unless it is itself a listed value. Lead values match exactly (case and spaces aside), never by a
substring; a lead with a missing value is reported incomplete, with no tier; a lead with a value given but not exactly
on the list is reported pending your confirmation, with no tier, even when the match looks obvious.
Exit codes: 0 done; 1 FAIL (0 criteria); 2 bad input. Standard library only; no network; writes no files.
"""
import json, math, re, sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction

DEFAULTS = {"critical": 25, "important": 15, "nice_to_have": 10}
TIER_DEFAULT = (80, 60, 40)
PLACEHOLDERS = {"n/a", "na", "unknown", "not known", "tbd", "-", "?", "none given"}


class BadInput(Exception):
    pass


def norm(s):
    return re.sub(r"\s+", " ", s.strip()).lower()


def number(v, where):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise BadInput(f"{where} must be a number, got {json.dumps(v)}")
    if isinstance(v, float) and not math.isfinite(v):
        raise BadInput(f"{where} must be a finite number")
    if v < 0:
        raise BadInput(f"{where} is {v}; it cannot be negative")
    return v


def half_up(fr):
    return int((Decimal(fr.numerator) / Decimal(fr.denominator)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def ceil_frac(fr):
    return -((-fr.numerator) // fr.denominator)


def show(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{float(x):g}"


def build(data):
    if not isinstance(data, dict):
        raise BadInput("the input must be a JSON object with a 'criteria' list")
    crit = data.get("criteria")
    if not isinstance(crit, list):
        raise BadInput("'criteria' must be a list")
    dw_raw = data.get("default_weights")
    dw, dw_keys = dict(DEFAULTS), set()
    if dw_raw is not None:
        if not isinstance(dw_raw, dict):
            raise BadInput("'default_weights' must be an object such as {\"critical\": 25}")
        for k, v in dw_raw.items():
            if k not in DEFAULTS:
                raise BadInput(f"unknown importance '{k}' in default_weights (allowed: critical, important, nice_to_have)")
            dw[k] = number(v, f"default weight for {k}")
            dw_keys.add(k)
    model, names = [], set()
    for i, c in enumerate(crit, 1):
        if not isinstance(c, dict):
            raise BadInput(f"criterion {i} must be an object, got {json.dumps(c)[:40]}")
        name = c.get("criterion")
        if not isinstance(name, str) or not name.strip():
            raise BadInput(f"criterion {i} has no name ('criterion')")
        if norm(name) in names:
            raise BadInput(f"criterion '{name}' appears twice")
        names.add(norm(name))
        imp = c.get("importance")
        if imp is not None and imp not in DEFAULTS:
            raise BadInput(f"criterion '{name}': importance must be exactly critical, important or nice_to_have (got {json.dumps(imp)})")
        src_for = lambda k: "your default weight" if k in dw_keys else "example default"
        src = src_for(imp or "nice_to_have")
        if "weight" in c and c["weight"] is not None:
            w = Fraction(number(c["weight"], f"weight of '{name}'"))
            wl, il = "your weight", (imp if imp else "importance not given")
        elif imp:
            w, wl, il = Fraction(dw[imp]), f"{src} for {imp}", imp
        else:
            w = Fraction(dw["nice_to_have"])
            wl, il = f"{src} for nice to have", f"importance not given, scored as nice to have ({show(w)}, {src})"
        vals = c.get("values")
        if not isinstance(vals, list) or not vals:
            raise BadInput(f"criterion '{name}' needs a non empty 'values' list, best value first")
        graded = c.get("graded", True)
        if not isinstance(graded, bool):
            raise BadInput(f"criterion '{name}': 'graded' must be true or false")
        n, out, seen = len(vals), [], set()
        for j, v in enumerate(vals):
            if isinstance(v, dict):
                vt = v.get("value")
                if not isinstance(vt, str) or not vt.strip():
                    raise BadInput(f"criterion '{name}' value {j + 1} has no text")
                pts, ps = Fraction(number(v.get("points"), f"points for '{vt}'")), "your points"
                if pts > w:
                    raise BadInput(f"points for '{vt}' ({show(pts)}) are more than the weight of '{name}' ({show(w)})")
            elif isinstance(v, str) and v.strip():
                vt = v
                if not graded or n == 1:
                    pts = w
                else:
                    pts = Fraction(half_up(w * (n - 1 - j) / (n - 1)))
                ps = "graded" if graded and n > 1 else "full weight"
            else:
                raise BadInput(f"criterion '{name}' value {j + 1} must be text")
            if norm(vt) in seen:
                raise BadInput(f"criterion '{name}' lists '{vt}' twice")
            seen.add(norm(vt))
            out.append({"value": vt.strip(), "points": pts, "points_source": ps})
        model.append({"criterion": name.strip(), "weight": w, "weight_label": wl, "importance_label": il, "values": out})
    mx = sum((c["weight"] for c in model), Fraction(0))
    if model and mx == 0:
        raise BadInput("the weights add up to 0, so no lead can score; give at least one criterion a weight above 0")
    tp_raw = data.get("tier_percents")
    if tp_raw is None:
        tp, tp_yours = TIER_DEFAULT, False
    else:
        if not isinstance(tp_raw, list) or len(tp_raw) != 3:
            raise BadInput("'tier_percents' must be three numbers, A then B then C, for example [80, 60, 40]")
        tp = tuple(number(x, "a tier percent") for x in tp_raw)
        if not (100 >= tp[0] > tp[1] > tp[2] > 0):
            raise BadInput(f"'tier_percents' {list(tp)} must fall from A to C, each above 0 and A at most 100")
        tp_yours = True
    tiers = {k: ceil_frac(mx * Fraction(str(v)) / 100) for k, v in zip("ABC", tp)}
    res = {"criteria": model, "max": mx, "tiers": tiers, "tier_percents": tp, "tier_percents_yours": tp_yours, "leads": [], "example_keys": sorted(set(DEFAULTS) - dw_keys)}
    leads = data.get("leads") or []
    if not isinstance(leads, list):
        raise BadInput("'leads' must be a list")
    for i, ld in enumerate(leads, 1):
        if not isinstance(ld, dict):
            raise BadInput(f"lead {i} must be an object, got {json.dumps(ld)[:40]}")
        label = ld.get("label") or f"Lead {i}"
        vals = ld.get("values")
        if not isinstance(vals, dict):
            raise BadInput(f"lead {i} needs 'values' as an object of criterion to value")
        byname, clash = {}, set()
        for k, v in vals.items():
            if norm(k) in byname and byname[norm(k)] != v:
                clash.add(norm(k))
            byname[norm(k)] = v
        score, missing, pending, detail = Fraction(0), [], [], []
        for c in model:
            v = byname.get(norm(c["criterion"]))
            hit = None
            if norm(c["criterion"]) in clash:
                missing.append(c["criterion"]); detail.append((c["criterion"], "two different values given", None)); continue
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if isinstance(v, float) and not math.isfinite(v):
                    raise BadInput(f"lead '{label}': the value for '{c['criterion']}' must be a finite number or text")
                v = show(Fraction(str(v)))
            if isinstance(v, str):
                hit = next((x for x in c["values"] if norm(x["value"]) == norm(v)), None)
            elif v is not None:
                raise BadInput(f"lead '{label}': the value for '{c['criterion']}' must be text")
            if hit is None:
                missing.append(c["criterion"]); detail.append((c["criterion"], v, None))
                if isinstance(v, str) and v.strip() and norm(v) not in PLACEHOLDERS:
                    pending.append((c["criterion"], v.strip()))
            else:
                score += hit["points"]; detail.append((c["criterion"], hit["value"], hit["points"]))
        extra = [k for k in vals if norm(k) not in {norm(c["criterion"]) for c in model}]
        tier = None
        if not missing:
            tier = "A" if score >= tiers["A"] else "B" if score >= tiers["B"] else "C" if score >= tiers["C"] else "D"
        res["leads"].append({"label": label, "score": score, "tier": tier, "missing": missing, "pending": pending, "ignored": extra, "detail": detail})
    return res


LIMIT = 200000


def tier_reading(res):
    """Which match patterns reach each tier: the fewest criteria at full points that can reach it (with one example), and the
    criteria a tier cannot do without. Run 34C: printed so that no tier rule is ever written by hand."""
    crit = res["criteria"]
    combos = 1
    for c in crit:
        combos *= len(c["values"])
    if combos > LIMIT:
        return ["Tier reading: not computed (more than 200,000 combinations of values); read the tier from each scored lead instead."]
    import itertools
    mx, out = res["max"], ["Tier reading (from the points above; copy these lines, never write a tier rule by hand):"]
    for tier in "ABC":
        th = res["tiers"][tier]
        best = None
        for pick in itertools.product(*[c["values"] for c in crit]):
            score = sum((v["points"] for v in pick), Fraction(0))
            if score < th:
                continue
            full = sum(1 for c, v in zip(crit, pick) if c["weight"] > 0 and v["points"] == c["weight"])
            key = (full, score)   # the fewest full matches, then the lowest score that still reaches the tier (so the example sits inside it)
            if best is None or key < best[0]:
                best = (key, pick, score)
        if best is None:
            out.append(f"Tier {tier} (from {th} of {show(mx)} points): no combination of values reaches it.")
            continue
        (full, _), pick, score = best
        at_full = [c["criterion"] for c, v in zip(crit, pick) if c["weight"] > 0 and v["points"] == c["weight"]]
        others = [f"{c['criterion']} = {v['value']}" for c, v in zip(crit, pick) if not (c["weight"] > 0 and v["points"] == c["weight"])]
        example = (", ".join(at_full) + " at full points" if at_full else "no criterion at full points") + ("; " + ", ".join(others) if others else "")
        out.append(f"Tier {tier} (from {th} of {show(mx)} points): the fewest criteria at full points that reach it: {full} of {len(crit)} (for example {example}: {show(score)} points).")
        needed = []
        for i, c in enumerate(crit):
            below = [v["points"] for v in c["values"] if v["points"] < c["weight"]]
            if not below:
                continue
            rest = sum((max(v["points"] for v in d["values"]) for j, d in enumerate(crit) if j != i), Fraction(0))
            if rest + max(below) < th:
                needed.append(c["criterion"])
        if needed:
            out.append(f"Tier {tier}: needs full points on {', '.join(needed)} (without them the most it can score is below {th}).")
        else:
            out.append(f"Tier {tier}: no single criterion is required at full points.")
    return out


def render(res):
    mx, t = res["max"], res["tiers"]
    out = ["Fit scoring model (lead_score.py)", "", "| Criterion | Importance | Weight | Values and points (best first) |", "|---|---|---|---|"]
    for c in res["criteria"]:
        vals = "; ".join(f"{v['value']} = {show(v['points'])}" for v in c["values"])
        out.append(f"| {c['criterion']} | {c['importance_label']} | {show(c['weight'])} ({c['weight_label']}) | {vals} |")
    out += ["", f"Maximum score: {show(mx)}",
            f"Tier A: {t['A']} to {show(mx)}", f"Tier B: {t['B']} to {t['A'] - 1}", f"Tier C: {t['C']} to {t['B'] - 1}", f"Tier D: 0 to {t['C'] - 1}",
            (f"Tier bands: {', '.join(show(Fraction(str(x))) + '%' for x in res['tier_percents'])} of the maximum, rounded up (your tier bands)." if res.get("tier_percents_yours")
             else "Tier bands: 80%, 60% and 40% of the maximum, rounded up (example default bands).")]
    out += tier_reading(res)
    if any("example default" in c["weight_label"] or "example default" in c["importance_label"] for c in res["criteria"]):
        names = {"critical": "critical 25", "important": "important 15", "nice_to_have": "nice to have 10"}
        used = [names[k] for k in ("critical", "important", "nice_to_have") if k in res.get("example_keys", list(names))]
        out.append(f"Example defaults: the weights {', '.join(used)} are starting examples, not a benchmark. Replace them with your own; validate the model on your closed won and lost deals before you rely on it.")
    for ld in res["leads"]:
        if ld.get("pending"):
            lists = {c["criterion"]: [v["value"] for v in c["values"]] for c in res["criteria"]}
            pend = "; ".join(f'{k} = "{v}" (listed: {", ".join(lists[k])})' for k, v in ld["pending"])
            rest = [m for m in ld["missing"] if m not in {k for k, _ in ld["pending"]}]
            line = f"{ld['label']}: pending your confirmation, no tier (not exactly on the list: {pend}; tell me which listed value it is)"
            if rest:
                line += f"; also missing: {', '.join(rest)}"
            line += f"; points from the criteria it has: {show(ld['score'])}"
        elif ld["missing"]:
            line = f"{ld['label']}: incomplete, no tier (missing, or two different values given: {', '.join(ld['missing'])}); points from the criteria it has: {show(ld['score'])}"
        else:
            line = f"{ld['label']}: {show(ld['score'])} of {show(mx)}, tier {ld['tier']}"
        if ld["ignored"]:
            line += f"; ignored, not a criterion: {', '.join(ld['ignored'])}"
        out.append(line)
    return "\n".join(out)


def main(argv):
    for stream in (sys.stdout, sys.stdin):   # run 32C: UTF-8 on Windows consoles and pipes, so non Latin text never gives a traceback
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print("Usage: python lead_score.py FILE.json (or - for standard input)"); return 2
    try:
        text = sys.stdin.read().lstrip("﻿") if argv[1] == "-" else open(argv[1], encoding="utf-8-sig").read()
    except OSError as e:
        print(f"Bad input: cannot read the file ({e.strerror})"); return 2

    def no_const(c):
        raise BadInput(f"{c} is not a number this script accepts")
    try:
        res = build(json.loads(text, parse_constant=no_const))
    except json.JSONDecodeError as e:
        print(f"Bad input: not valid JSON (line {e.lineno}, column {e.colno})"); return 2
    except BadInput as e:
        print(f"Bad input: {e}"); return 2
    if not res["criteria"]:
        print("FAIL: 0 criteria in the input, so there is no model to build."); return 1
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
