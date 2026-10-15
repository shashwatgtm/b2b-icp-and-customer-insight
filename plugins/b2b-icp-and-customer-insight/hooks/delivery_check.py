"""delivery_check.py: the plugin's Stop hook (Claude Code only). When one of this plugin's skills ran its claim ledger
(scripts/claim_ledger.py) in the current turn, it checks, before Claude stops, that the reply Claude is about to send is exactly the text the
ledger last checked, and sends Claude back with the reason when it is not:
  1. the last claim_ledger.py run of the turn is a passing --final run (its first line: "claim_ledger --final: PASS, reply digest <d>");
  2. no tool that can change a file ran after it (Write, Edit, MultiEdit, NotebookEdit, or a shell command that is not a plain read);
  3. the reply's digest (the ledger's digest rule: line ends and trailing spaces ignored) is that digest. The reply is all the text Claude
     wrote after that run, joined, so a line before the checked text counts too.
Only a python run of a claim_ledger.py with --user, whose output carries this ledger's summary line or whose path names one of the five skills, starts the check; a turn without one
is left alone, so the hook does nothing in any other conversation. It sends Claude back at most twice per turn, then lets the reply through.
What it guarantees: the final reply of the turn (the result of `claude -p`, and the last message in interactive use) and the saved files
the --final run checked. In interactive use the screen also shows any text written earlier in the turn; the skills write none.

What it reads: the Stop hook input (on standard input) and the session transcript file it names, both on this computer. What it writes: one
small counter file per session in a folder of your own in the system temporary folder (b2b-icp-claim-ledger-<user id>/ on macOS and Linux,
b2b-icp-claim-ledger/ on Windows, where that folder is already your own), so it never sends Claude back more than twice.
It sends nothing anywhere and makes no network call. Standard library only. It always exits 0; on any error it lets the reply through.
"""
import hashlib, json, os, re, sys, tempfile

MARK = "[b2b-icp claim ledger delivery check]"
MAX_SEND_BACKS = 2
READ_ONLY = re.compile(r"^\s*(cat|type|ls|dir|head|tail|wc|sha256sum|md5sum|echo|pwd|cut|sort|grep|Get-Content|gc)\b[^>|;&]*$")
CHANGERS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SHELLS = ("Bash", "PowerShell")
SKILLS = ("icp-review", "customer-interviews", "lead-scoring-model", "buying-role-hypotheses", "pmf-check")
RUN = re.compile(r"\bpython[0-9.]*(\.exe)?\b[^|;&\n]*?(?<![\w-])claim_ledger\.py\b[^|;&\n]*--user\b")


def digest(text):
    t = "\n".join(l.rstrip() for l in (text or "").replace("\r\n", "\n").strip().splitlines())
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def body(c):
    b = c.get("content")
    b = "\n".join(y.get("text", "") for y in b if isinstance(y, dict)) if isinstance(b, list) else (b or "")
    return b.replace("\r\n", "\n")


def is_prompt(m):
    """A message the person typed (not a tool result, a compaction summary or any hook's feedback)."""
    if m.get("type") != "user" or m.get("isMeta") or m.get("isCompactSummary") or m.get("isVisibleInTranscriptOnly"):
        return False
    c = (m.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return False
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return isinstance(c, str) and MARK not in c and not c.lstrip().startswith(("Stop hook feedback", "This session is being continued"))


def turn(path):
    """The messages of the current turn: everything after the last message the person typed."""
    msgs, prompts = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if isinstance(m, dict):
                if is_prompt(m):
                    msgs, prompts = [], prompts + 1
                else:
                    msgs.append(m)
    return msgs, prompts


def decide(inp):
    msgs, prompts = turn(inp["transcript_path"])
    inp["_turn"] = prompts
    calls, results, order, texts, feedback = {}, {}, [], [], -1
    for m in msgs:
        c = (m.get("message") or {}).get("content")
        if m.get("type") == "user" and not (isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c)):
            feedback = len(order)   # hook feedback or any other message in the turn: the reply starts after it
            texts = [(n, s) for n, s in texts if n > feedback]
            if isinstance(c, list):
                continue
        if not isinstance(c, list):
            continue
        for x in c:
            if not isinstance(x, dict):
                continue
            if x.get("type") == "tool_use":
                calls[x.get("id")] = (x.get("name"), x.get("input") or {})
                order.append(x.get("id"))
            elif x.get("type") == "tool_result" and x.get("tool_use_id") in calls:
                results[x.get("tool_use_id")] = body(x)
            elif x.get("type") == "text" and m.get("type") == "assistant":
                texts.append((len(order), x.get("text", "")))
    led = [i for i in order if calls[i][0] in SHELLS and RUN.search(str(calls[i][1].get("command", "")))
           and (re.search(r"^claim_ledger(?: --final)?: ", results.get(i, ""), re.M) or any(s in str(calls[i][1].get("command", "")) for s in SKILLS))]
    if not led:
        return None   # this plugin's ledger did not run in this turn: not ours to check
    last = led[-1]
    out = results.get(last, "")
    begin = re.search(r"^claim_ledger --final: PASS, reply digest ([0-9a-f]{16})$", out, re.M) or re.search(r"^=== BEGIN CHECKED REPLY ([0-9a-f]{16}) ===$", out, re.M)
    if "--final" not in str(calls[last][1].get("command", "")) or not begin:
        return ("The claim ledger ran in this turn, but its last run was not a passing --final run. Fix every NEEDS line, then run "
                "claim_ledger.py --final with the same files as your last tool call (no pipe, no grep), and send as your whole reply exactly "
                "the text between its BEGIN CHECKED REPLY and END CHECKED REPLY lines.")
    for i in order[order.index(last) + 1:]:
        name, ti = calls[i]
        if not (name in CHANGERS or (name in SHELLS and not all(READ_ONLY.match(s) for s in str(ti.get("command", "")).split("|")))):
            continue
        return (f"A tool that can change a file ({name}) ran after the last claim_ledger.py --final run, so the checked text may not be what "
                "you deliver. Run claim_ledger.py --final again on the reply file and every saved file as your last tool call, and send exactly "
                "the text between its BEGIN CHECKED REPLY and END CHECKED REPLY lines.")
    want = begin.group(1)
    k = order.index(last) + 1
    after = [x for n, x in texts if n >= k]   # texts written before the last feedback message were dropped above
    reply = "\n\n".join(after) if after else (inp.get("last_assistant_message") or "")
    if len(after) == 1 and inp.get("last_assistant_message") is not None:
        reply = inp["last_assistant_message"]
    if digest(reply) == want:
        return None
    return (f"Your reply is not the text the claim ledger checked (digest {want}). Send as your whole reply exactly the text between "
            f"=== BEGIN CHECKED REPLY {want} === and === END CHECKED REPLY {want} === in the last claim_ledger.py --final output: nothing "
            "before it (no summary, no 'here it is'), nothing after it, no word or line changed. To say anything else, put it in the reply "
            "file and run --final again.")


def counter_dir():
    """The folder for the counter files: per user, from the user id where the system has one; on Windows the temporary folder is per user."""
    name = f"b2b-icp-claim-ledger-{os.getuid()}" if hasattr(os, "getuid") else "b2b-icp-claim-ledger"
    return os.path.join(tempfile.gettempdir(), name)


def main():
    try:
        raw = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
        inp = json.loads(raw.decode("utf-8", errors="replace") or "{}")
        if not isinstance(inp, dict) or not inp.get("transcript_path"):
            return 0
        reason = decide(inp)
        d = counter_dir()
        sid = re.sub(r"[^A-Za-z0-9_-]", "_", str(inp.get("session_id") or "nosession"))[:80]
        p = os.path.join(d, sid + ".json")
        if reason is None:
            if os.path.exists(p):
                os.remove(p)   # the turn ends cleanly: the next turn starts a new count
            return 0
        os.makedirs(d, mode=0o700, exist_ok=True)
        if os.path.islink(d) or os.path.islink(p):
            return 0
        try:
            with open(p, encoding="utf-8") as f:
                st = json.load(f)
            n = int(st.get("n", 0)) if st.get("turn") == inp["_turn"] else 0
        except (OSError, ValueError, AttributeError, TypeError):
            n = 0
        if n >= MAX_SEND_BACKS:
            return 0
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"turn": inp["_turn"], "n": n + 1}, f)
        print(json.dumps({"decision": "block", "reason": f"{MARK} {reason}"}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
