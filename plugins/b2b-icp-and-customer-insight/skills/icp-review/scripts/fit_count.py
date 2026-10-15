"""fit_count.py: how many customers can fit two or more ICP parts at once, when only each part's count is known.

Usage: python3 fit_count.py FILE.json      (or - to read standard input; use python where python3 is not found)

Input (JSON object): {"total": 22, "parts": {"ICP segments": 15, "500 or more seats": 14}}
  total: the number of customers; parts: for each ICP part, how many of them fit it (whole numbers, 0 to total; two or more parts).
Output: the number that fits every part lies between max(0, sum of the parts minus (number of parts minus 1) times total) and the
smallest part. The true number needs the customer list; this range is what the counts alone allow.
Exit codes: 0 done; 2 bad input or a file that cannot be read. Standard library only; no network; writes no files.
"""
import json, sys


class BadInput(Exception):
    pass


def both_range(total, counts):
    low = max(0, sum(counts) - (len(counts) - 1) * total)
    return low, min(counts)


def whole(v, where):
    if isinstance(v, bool) or not isinstance(v, int):
        raise BadInput(f"{where} must be a whole number, got {json.dumps(v)}")
    return v


def main(argv):
    name = argv[1] if len(argv) > 1 else "-"
    try:
        raw = sys.stdin.buffer.read() if name == "-" else open(name, "rb").read()
    except OSError as e:
        print(f"fit_count: cannot read {name}: {e.strerror}")
        return 2
    text = raw.decode("utf-8-sig", errors="replace")
    if not text.strip():
        print("fit_count: nothing to read")
        return 2
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise BadInput("the input must be a JSON object")
        total = whole(data.get("total"), "total")
        parts = data.get("parts")
        if not isinstance(parts, dict) or len(parts) < 2:
            raise BadInput("parts must name two or more ICP parts with their counts")
        counts = []
        for label, v in parts.items():
            v = whole(v, f"parts[{label}]")
            if v < 0 or v > total:
                raise BadInput(f"parts[{label}] is {v}, outside 0 to {total}")
            counts.append(v)
        if total < 0:
            raise BadInput("total must be 0 or more")
    except (ValueError, BadInput) as e:
        print(f"fit_count: bad input: {e}")
        return 2
    low, high = both_range(total, counts)
    labels = " and ".join(parts)
    print(f"Customers fitting {labels} at once: between {low} and {high} of {total} (from the counts alone; the customer list gives the exact number).")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
