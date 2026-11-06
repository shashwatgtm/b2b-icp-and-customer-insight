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
# A damaged label: lower case letters before a run of 2 or 3 capitals (securIT), or lower case letters on both sides of
# such a run (mAInager), or "infrastructure" with letters glued on (infrastructurey; the plural "infrastructures" is fine).
# Each pattern is short and plain, with no look ahead or look behind.
CAPS_AFTER_LOWER = re.compile(r"\b[a-z]+[A-Z]{2,3}[A-Za-z]*")
CAPS_INSIDE_WORD = re.compile(r"\b[A-Za-z]*[a-z][A-Z]{2,3}[a-z]+\w*")
INFRA_GLUED = re.compile(r"\binfrastructure[a-z]+")


def first_of(patterns, line):
    """Matches of several patterns, left to right, the earlier pattern first at the same place, never overlapping:
    the same matches one pattern written as an alternation (a|b) gives."""
    found = sorted((m.start(), k, m.end(), m.group(0)) for k, rx in enumerate(patterns) for m in rx.finditer(line))
    out, end = [], -1
    for start, _, stop, text in found:
        if start >= end:
            out.append(text)
            end = stop
    return out


def damaged_labels(line):
    caps = first_of([CAPS_AFTER_LOWER, CAPS_INSIDE_WORD], line)
    infra = [m.group(0) for m in INFRA_GLUED.finditer(line) if not plural_word(line, m)]
    return caps + infra


def plural_word(line, m):
    """True for the whole word "infrastructures" (a plural, not a damaged label)."""
    after = line[m.end():m.end() + 1]
    return m.group(0) == "infrastructures" and not (after.isalnum() or after == "_")


def blank_hyphen_cells(row):
    """In a table row, a cell holding only one or two hyphens (between two pipes) is an empty cell, not a dash."""
    parts = row.split("|")
    cells_between = [" " if p.strip() in ("-", "--") else p for p in parts[:-1]]
    return "|".join(cells_between + parts[-1:])
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
        body = blank_hyphen_cells(body) if body.lstrip().startswith("|") else body   # a lone hyphen cell is empty, not a dash
        if DASH.search(body):
            problems.append(f"line {i}: long or short dash")
        for label in damaged_labels(line):
            if label in KNOWN:
                continue
            problems.append(f"line {i}: damaged label '{label}' (a part word replace)")
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
            text = sys.stdin.read().lstrip("\ufeff") if a == "-" else open(a, encoding="utf-8-sig").read()
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
