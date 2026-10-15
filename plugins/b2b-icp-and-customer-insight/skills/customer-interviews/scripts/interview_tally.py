"""interview_tally.py: count what customers said across many interviews, each item once per interview.

Usage: python interview_tally.py FILE.json      (or - to read standard input)

Input (JSON object):
  {"hypotheses": ["H1", "H2"],                       (optional: the ids or texts of the team's hypotheses)
   "interviews": [
     {"label": "Interview 1", "role": "Head of finance",
      "pains": ["..."], "triggers": ["..."], "objections": ["..."], "value": ["..."], "quotes": ["..."],
      "hypotheses": {"H1": "supports", "H2": "no evidence"}}],
   "next_round": {"minimum_per_group": 5, "groups": [{"name": "Paying teams", "done": 0, "planned": 3}]}}   (optional)

Rules: an item is counted once per interview, after a light normalisation (case, spaces, end punctuation, outer quotes);
items match exactly, never by a substring. Shares read "k of n interviews (x%)". Ties at the top are named.
If every interview has identical items, a warning says the notes may be copied or summarised.
Hypothesis verdicts are exactly "supports", "contradicts" or "no evidence"; the reading is never "confirmed".
Interviewees are shown by label and role only. Quotes are printed word for word.
next_round (optional): per group of interviewees, done + planned = total, and how many short of the minimum per group
(yours; if not given, 5, the script's own direction line, not a research standard).
Exit codes: 0 done; 1 FAIL (0 interviews); 2 bad input. Standard library only; no network; writes no files.
"""
import json, re, sys
from decimal import Decimal, ROUND_HALF_UP

CATS = ["pains", "triggers", "objections", "value"]
TITLES = {"pains": "Pains", "triggers": "Buying triggers", "objections": "Objections", "value": "Value realised", "roles": "Roles interviewed"}
VERDICTS = ("supports", "contradicts", "no evidence")


class BadInput(Exception):
    pass


def norm(s):
    s = re.sub(r"\s+", " ", s.strip()).strip("\"'“”‘’ ")
    return re.sub(r"[.,;:!?]+$", "", s).strip().lower()


def pct(k, n):
    return int((Decimal(k) * 100 / Decimal(n)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def strings(v, where):
    if v is None:
        return []
    if not isinstance(v, list):
        raise BadInput(f"{where} must be a list of text items")
    out = []
    for x in v:
        if not isinstance(x, str):
            raise BadInput(f"{where} holds {json.dumps(x)}; every item must be text")
        if x.strip():
            out.append(x.strip())
    return out


def next_round(data):
    nr = data.get("next_round")
    if nr is None:
        return None
    if not isinstance(nr, dict):
        raise BadInput("'next_round' must be an object with a 'groups' list")
    mn = nr.get("minimum_per_group")
    yours = mn is not None
    if not yours:
        mn = 5
    if isinstance(mn, bool) or not isinstance(mn, int) or mn < 1:
        raise BadInput(f"next_round minimum_per_group must be a whole number of 1 or more, got {json.dumps(mn)}")
    groups = nr.get("groups")
    if not isinstance(groups, list) or not groups:
        raise BadInput("next_round needs a non empty 'groups' list such as [{\"name\": \"Paying teams\", \"done\": 0, \"planned\": 3}]")
    rows, names = [], set()
    for i, g in enumerate(groups, 1):
        if not isinstance(g, dict):
            raise BadInput(f"next_round group {i} must be an object, got {json.dumps(g)[:40]}")
        name = g.get("name")
        if not isinstance(name, str) or not name.strip():
            raise BadInput(f"next_round group {i} has no name")
        if name.strip().lower() in names:
            raise BadInput(f"next_round group '{name.strip()}' appears twice; give each group once")
        names.add(name.strip().lower())
        vals = []
        for k in ("done", "planned"):
            v = g.get(k, 0)
            if isinstance(v, bool) or not isinstance(v, int) or v < 0:
                raise BadInput(f"next_round group '{name}': '{k}' must be a whole number of 0 or more, got {json.dumps(v)}")
            vals.append(v)
        total = vals[0] + vals[1]
        rows.append({"name": name.strip(), "done": vals[0], "planned": vals[1], "total": total, "minimum": mn, "yours": yours, "short_by": max(0, mn - total)})
    return rows


def tally(data):
    if not isinstance(data, dict):
        raise BadInput("the input must be a JSON object with an 'interviews' list")
    ivs = data.get("interviews")
    if not isinstance(ivs, list):
        raise BadInput("'interviews' must be a list")
    hyp_ids = data.get("hypotheses") or []
    if not isinstance(hyp_ids, list) or not all(isinstance(h, str) for h in hyp_ids):
        raise BadInput("'hypotheses' must be a list of text ids")
    n = len(ivs)
    counts = {c: {} for c in CATS + ["roles"]}
    first = {c: {} for c in CATS + ["roles"]}
    order = {c: [] for c in CATS + ["roles"]}
    sets, quotes = [], []
    hyp = {h: {"supports": 0, "contradicts": 0, "no evidence": 0} for h in hyp_ids}
    hyp_order = list(hyp_ids)
    for i, iv in enumerate(ivs, 1):
        if not isinstance(iv, dict):
            raise BadInput(f"interview {i} must be an object, got {json.dumps(iv)[:40]}")
        label = iv.get("label") or f"Interview {i}"
        role = iv.get("role")
        if label is not None and not isinstance(label, str) or role is not None and not isinstance(role, str):
            raise BadInput(f"interview {i}: label and role must be text")
        sig = []
        for c in CATS:
            items = strings(iv.get(c), f"interview {i} {c}")
            seen = set()
            for it in items:
                k = norm(it)
                if not k or k in seen:
                    continue
                seen.add(k)
                if k not in counts[c]:
                    counts[c][k] = 0; first[c][k] = it; order[c].append(k)
                counts[c][k] += 1
            sig.append(frozenset(seen))
        sets.append(tuple(sig))
        if role and role.strip():
            k = norm(role)
            if k not in counts["roles"]:
                counts["roles"][k] = 0; first["roles"][k] = role.strip(); order["roles"].append(k)
            counts["roles"][k] += 1
        for q in strings(iv.get("quotes"), f"interview {i} quotes"):
            quotes.append((q, label, role.strip() if role and role.strip() else "role not given"))
        hv = iv.get("hypotheses") or {}
        if not isinstance(hv, dict):
            raise BadInput(f"interview {i} hypotheses must be an object such as {{\"H1\": \"supports\"}}")
        for h, verdict in hv.items():
            if not isinstance(verdict, str) or verdict.strip().lower() not in VERDICTS:
                raise BadInput(f"interview {i} hypothesis {h}: the verdict must be exactly one of supports, contradicts, no evidence (got {json.dumps(verdict)})")
            listed = next((x for x in hyp_ids if x.strip().lower() == str(h).strip().lower()), None)
            if hyp_ids and listed is None:
                raise BadInput(f"interview {i} names hypothesis {json.dumps(h)}, which is not in the 'hypotheses' list ({', '.join(hyp_ids)}); check the id")
            h = listed or h
            if h not in hyp:
                hyp[h] = {"supports": 0, "contradicts": 0, "no evidence": 0}; hyp_order.append(h)
            hyp[h][verdict.strip().lower()] += 1
    res = {"n": n, "categories": {}, "ties": {}, "quotes": quotes, "hypotheses": {}, "next_round": next_round(data)}
    for c in CATS + ["roles"]:
        ranked = sorted(order[c], key=lambda k: (-counts[c][k], order[c].index(k)))
        res["categories"][c] = [{"text": first[c][k], "count": counts[c][k], "share": f"{counts[c][k]} of {n} interviews ({pct(counts[c][k], n)}%)"} for k in ranked] if n else []
        if ranked:
            top = counts[c][ranked[0]]
            tied = [first[c][k] for k in ranked if counts[c][k] == top]
            if len(tied) > 1:
                res["ties"][c] = tied
    res["same_across"] = n >= 2 and len(set(sets)) == 1 and any(sets[0])
    for h in hyp_order:
        d = dict(hyp[h]); d["not asked"] = n - sum(hyp[h].values())
        s, x = d["supports"], d["contradicts"]
        d["reading"] = "mixed" if s and x else "leans towards support (not proof)" if s else "leans against" if x else "no evidence yet"
        res["hypotheses"][h] = d
    return res


def render(res):
    n = res["n"]
    out = [f"Interview tally (interview_tally.py): {n} interview{'' if n == 1 else 's'}, each item counted once per interview", ""]
    if res["same_across"]:
        out += ["WARNING: every interview has identical items. The notes may be copied from one template or summarised the same way, so these counts do not show a pattern yet. Check the raw notes.", ""]
    for c in CATS + ["roles"]:
        rows = res["categories"][c]
        if not rows:
            continue
        out.append(f"{TITLES[c]}:")
        for r in rows:
            out.append(f"- {r['text']}: {r['share']}")
        if c in res["ties"]:
            out.append(f"  (tied at the top: {', '.join(res['ties'][c])})")
        out.append("")
    if res["quotes"]:
        out.append("Quotes, word for word (by interview label and role):")
        for q, label, role in res["quotes"]:
            out.append(f'- "{q}" ({label}, {role})')
        out.append("")
    if res["hypotheses"]:
        out.append("Hypotheses (supports / contradicts / no evidence / not asked; a reading is never proof):")
        for h, d in res["hypotheses"].items():
            out.append(f"- {h}: {d['supports']} / {d['contradicts']} / {d['no evidence']} / {d['not asked']}: {d['reading']}")
        out.append("")
    if res.get("next_round"):
        rows = res["next_round"]
        out.append("Next round plan (done + planned per group):")
        for r in rows:
            who = f"your minimum of {r['minimum']}" if r["yours"] else str(r["minimum"])
            state = f"meets {who}" if not r["short_by"] else f"{r['short_by']} short of {who}"
            out.append(f"- {r['name']}: {r['done']} done + {r['planned']} planned = {r['total']}; {state}")
        if not rows[0]["yours"]:
            out.append("  (5 is this script's own line for a direction, not a research standard; give your own minimum per group)")
        out.append("")
    if n < 5:
        out.append("Note: 1 interview shows a direction, not a pattern." if n == 1 else f"Note: {n} interviews show a direction, not a pattern.")
    return "\n".join(out).rstrip()


def main(argv):
    for stream in (sys.stdout, sys.stdin):   # run 32C: UTF-8 on Windows consoles and pipes, so non Latin text never gives a traceback
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print("Usage: python interview_tally.py FILE.json (or - for standard input)"); return 2
    try:
        text = sys.stdin.read().lstrip("﻿") if argv[1] == "-" else open(argv[1], encoding="utf-8-sig").read()
    except OSError as e:
        print(f"Bad input: cannot read the file ({e.strerror})"); return 2

    def no_const(c):
        raise BadInput(f"{c} is not a value this script accepts")
    try:
        res = tally(json.loads(text, parse_constant=no_const))
    except json.JSONDecodeError as e:
        print(f"Bad input: not valid JSON (line {e.lineno}, column {e.colno})"); return 2
    except BadInput as e:
        print(f"Bad input: {e}"); return 2
    if res["n"] == 0 and not res.get("next_round"):
        print("FAIL: 0 interviews in the input, so there is nothing to count."); return 1
    if res["n"] == 0:
        print("No interviews counted yet (0 in the input); next round plan only.")
        plan = [l for l in render(res).splitlines() if not l.startswith("Interview tally") and not l.startswith("Note:")]
        print(chr(10).join(plan).strip())
        return 0
    print(render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
