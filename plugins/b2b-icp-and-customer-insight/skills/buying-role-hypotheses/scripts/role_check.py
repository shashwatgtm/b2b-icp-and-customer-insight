"""role_check.py: a text check for a buying role hypotheses draft.

Usage: python role_check.py FILE [FILE ...]      (or - to read standard input)

Checks: no long or short dashes (or spaced hyphens used as dashes); no role or function label damaged by a part word replace (for example the source
tool's "securIT infrastructurey", where "it" inside "security" was replaced); in every table that has a
"Validation question" column, every row has a question, and where the table has a "what would disprove it" column, every row fills it
(n/a, none, TBD or a lone hyphen count as empty). Real mixed case terms (vCISO, eSIM, mTLS, gRPC) and indented bullets are not flagged.
Exit codes: 0 clean; 1 problems found; 2 nothing to read. Standard library only; no network; writes no files.
"""
import re, sys

DASH = re.compile("[\u2012\u2013\u2014\u2015]| -{1,2} ")
# a word with lower case letters on a side of a run of 2 or 3 capitals (securIT, mAInager), and "infrastructure" with letters glued on
DAMAGED = [re.compile(r"\b[a-z]+[A-Z]{2,3}[A-Za-z]*|\b[A-Za-z]*[a-z][A-Z]{2,3}[a-z]+\w*"), re.compile(r"\binfrastructure(?!s\b)[a-z]+")]
KNOWN = {"ITeS", "SaaS", "PaaS", "IaaS", "iPaaS", "CPaaS", "eKYC", "iOS", "macOS", "vCISO", "vCIO", "eSIM", "eUICC", "mTLS", "gRPC", "iPhone", "iPad", "eSOC"}
EMPTY = {"", "n/a", "na", "-", "none", "tbd", "?"}


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def check_text(text):
    problems = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        body = line[len(line) - len(line.lstrip()):] if line.lstrip().startswith("- ") else line   # an indented bullet is not a dash
        body = body[2:] if body.startswith("- ") else body
        body = re.sub(r"\|\s*-{1,2}\s*(?=\|)", "| ", body) if body.lstrip().startswith("|") else body   # a lone hyphen cell is empty, not a dash
        if DASH.search(body):
            problems.append(f"line {i}: long or short dash")
        for rx in DAMAGED:
            for m in rx.finditer(line):
                if m.group(0) in KNOWN:
                    continue
                problems.append(f"line {i}: damaged label '{m.group(0)}' (a part word replace)")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = [h.lower() for h in cells(line)]
            col = head.index("validation question") if "validation question" in head else None
            dis = next((k for k, h in enumerate(head) if "disprove" in h), None)
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                if col is not None:
                    row = cells(lines[j])
                    if col >= len(row) or row[col].strip().lower() in EMPTY:
                        problems.append(f"line {j + 1}: hypothesis row with no validation question")
                    if dis is not None and (dis >= len(row) or row[dis].strip().lower() in EMPTY):
                        problems.append(f"line {j + 1}: hypothesis row with nothing under what would disprove it")
                j += 1
            i = j
        else:
            i += 1
    return problems


def main(argv):
    for stream in (sys.stdout, sys.stdin):   # run 32C: UTF-8 on Windows consoles and pipes, so non Latin text never gives a traceback
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if len(argv) < 2:
        print("Usage: python role_check.py FILE [FILE ...] (or - for standard input)"); return 2
    total, bad = 0, 0
    for a in argv[1:]:
        try:
            text = sys.stdin.read().lstrip("﻿") if a == "-" else open(a, encoding="utf-8-sig").read()
        except OSError as e:
            print(f"Cannot read {a}: {e.strerror}"); return 2
        except UnicodeDecodeError:
            print(f"Cannot read {a}: it is not UTF-8 text; save it as UTF-8 and run again"); return 2
        if not text.strip():
            print(f"{a}: empty, nothing to check"); return 2
        total += 1
        for p in check_text(text):
            bad += 1; print(f"{a}: {p}")
    print(f"role_check: {total} files, {bad} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
