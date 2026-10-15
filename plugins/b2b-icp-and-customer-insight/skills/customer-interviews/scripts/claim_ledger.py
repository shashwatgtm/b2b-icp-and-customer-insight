"""claim_ledger.py: the claim ledger. Before an answer is delivered, it lists every sentence of the exact text you will deliver (the chat
reply and every saved file) that states something about the user's world (the user, their company, product, customers, accounts, deals,
notes, interviewees, plans or roles, a named company, a buyer seat), every figure and every label, and gives each line its source or marks it
NEEDS A SOURCE. It matches against the user's own words (the message, copied whole into a file), the script outputs and the page text you pass,
not against a word list of topics.

Usage: python3 claim_ledger.py [--final] --user USER.txt [--script OUT.txt ...] [--page PAGE.txt ...] [--notes NOTES.md] FILE [FILE ...]
       (use python where python3 is not found)

  --user    the user's message (and any file they attached), copied whole, word for word. Required.
  --script  the printed output of a script run in this session (icp_gap.py, fit_count.py, lead_score.py and so on), saved as printed.
  --page    the text of a page opened in this session (its link on the first line), as the tool returned it.
  --notes   the plugin's sector notes file; used only for a sentence that names the sector notes row.
  FILE      the exact texts you will deliver: the chat reply first, then every saved file. Each is checked; the last run must be on the exact text.
  --final   the last run, your last tool call before you answer: it prints only the lines to fix, and when there is none it prints the
            reply file (the first FILE) between "=== BEGIN CHECKED REPLY <digest> ===" and "=== END CHECKED REPLY <digest> ===". That text,
            exactly, is your whole chat reply. In Claude Code the plugin's Stop hook (hooks/delivery_check.py) compares the reply you send
            with it and sends you back when they differ.

What it lists (a line is fine when its kind is not marked NEEDS):
  FIGURE  a percentage, decimal or number of 10 or more ("67 percent" counts as 67%) that is not the user's own: when a script printed
          it, the line must hold the script's printed line or its printed cell ("+39% increase needed"); otherwise it must be in a source;
          a range neither a source nor a script holds is listed (worked out by hand).
  QUOTE   text inside double quotes of three or more words, not a question, must appear word for word in a source or the skill's text.
  ADDS    words a sentence adds that no source holds (outside quotes, code spans, links and paths). In a sentence about the user or
          their customers, segment, buyers, accounts, deals or interviewees, and in a table value cell, every added word counts and the
          skill's own text sources none. In other sentences only fact words (buy, sell, use, owns, decide, depend, know, sign, choose,
          pay, renew, large, small, regulated and their forms), domain words of the sector notes, role words and names count, and the
          skill's method text (never its worked examples) is a word list. Header cells and row labels are checked against the method words.
  SCOPE   all, every, each, none, no, neither, only, never or always about the user's items, with nothing quoted ("you gave no target",
          "no trigger recorded", a sourced "k of n" and instructions to the reader are not listed).
  CAUSE   a reason or rule (because, since, so, therefore, which means, decides, depends, determines, drives) with nothing quoted after it.
  RULE    what a person or group does (buys, signs, decides, uses, chooses and so on) with nothing quoted.
  ITEM    what Deal 3, Interview 5, Win 1 or a like item holds, with nothing quoted.
  PAGE    what a page or a named site says, describes or lists, with nothing quoted.
  GENERAL a word of generality (many, most, usually, typical, often, likely, always and so on) with no named source.
A sentence is about the user's world when it names you or your, a person, role, group, customer, deal, note or interview, a capitalised
name the sources hold, or says what someone does. Split into sentences, and statements into clauses at semicolons and at ", and", ", but", ", so", ", which" and "while" (a question stays whole); a table row's cells count as about the user's world, except the header row and short row labels; dates are not figures. Not listed: questions, clauses
that start with a condition (if, whether, when, where, unless), "[User to add: ...]" slots, labelled clauses ("hypothesis:", "to test",
"to confirm", "assumption", "as given by you", "as pasted, not yet checked", "from a search result, page not opened", "example default",
"draft for you to confirm", "worth checking"), hedged clauses (may, might, could, perhaps, possibly), lines attributed to the user
("your hypothesis", "you said"), a line that is a copy of a script line, short label cells of a table, headings, code blocks and block quotes.
LABELS  every label in each file is listed; a label kind present in one delivered file and absent in another is listed as LABEL DROP.
DIGEST  a digest of each checked file, also on the summary line; the text you deliver must be exactly the text with this digest (re run
        after any change).

The script decides nothing about truth: it shows where a sentence goes past the sources. Each NEEDS line is fixed by quoting the user's own
words, copying the script line, citing the page, turning it into a question, a condition or a "[User to add: ...]" slot, labelling it, or
deleting it; then run the script again. Exit codes: 0 no NEEDS line and no LABEL DROP; 1 lines to fix; 2 bad input (no --user, a file
that cannot be read, nothing to read). Standard library only; no network; writes no files.
"""
import hashlib, re, sys

STOP = set("""
a an the and or but nor if then than that this these those there here it its it's itself is are was were be been being am do does did done doing
have has had having of in on at to for from by with without within into onto over under up down out off about above below across after before
between through during per via as so such not no yes too very more less most least much many some any all each every both either neither none
own same other another only just also even still yet again ever never always once twice can cannot could may might must shall should will would
i me my mine we us our ours you your yours he him his she her they them their theirs who whom whose which what when where why how whether while
because since until unless though although however therefore thus hence else instead rather like unlike near far one two three four five six seven
eight nine ten first second third last next new old now today later soon here's what's that's there's don't doesn't didn't isn't aren't wasn't
weren't won't can't couldn't shouldn't wouldn't haven't hasn't hadn't i'm i've i'd i'll you're you've you'd you'll we're we've they're they've
let get got gives give gave given make makes made take takes took taken see seen saw show shows shown showed say says said tell told ask asks asked
asking need needs needed want wants wanted put puts keep keeps kept go goes went gone come comes came run runs ran find found look looks looked
read reads write writes wrote written mean means meant call calls called set sets add adds added use used uses using try tries tried work works
worked start starts started end ends ended move moves moved help helps helped turn turns turned leave left way ways thing things part parts lot
kind sort case cases point points line lines item items list lists table tables row rows column columns file files text answer answers reply
note notes page pages script scripts output outputs figure figures number numbers count counts total totals sum value values field fields
question questions test tests tested testing check checks checked checking confirm confirms confirmed hypothesis hypotheses evidence source
sources plan plans planned round rounds step steps open opens version draft drafts label labels labelled example examples default defaults
marked mark marks keep trial qualify drop dropped weight weights weighted score scores scored tier tiers band bands gap gaps metric metrics
target targets current today period quarter month months week weeks year years day days time times percent percentage rate rates priority
high medium low higher lower highest lowest above below more fewer same different differ equal match matches matched partly full fully half
missing missed given not compared yet already instead each other per cent rest whole part next sure clear clearly simple simply direct directly
fine good bad better best worse worst right wrong true false strong stronger strongest weak weaker weakest thin enough short long whole entire
real really actual actually exact exactly specific specifically general generally main mainly key likely possible possibly probably perhaps
section sections summary short version answer guide guides interview interviews interviewed interviewing interviewer synthesis method methods
hand script's skill plugin user user's model models prompt chat folder working copy copies copied quote quotes quoted word words verbatim
paste pasted pastes export exports crm data dataset split splits splitting pull pulls pulled sample samples group groups grouping
support supports supported weaken weakens weakened disprove disproves disproved prove proves proved suggest suggests suggested signal signals
reason reasons stated state states statement statements claim claims explain explains reasoning sense idea ideas view views
please something anything everything nothing someone anyone everyone think thinks thought hear heard listen listens learn learns covers cover
happen happens happened result results decision decisions describe describes described include includes included separate separately walk
record records recorded template templates side sides share shares around across entry level levels area areas detail details against inside
minute minutes module modules appear appears appeared section block blocks follow follows following
""".split())
# an instruction to the reader or the interviewer (a line that starts with a verb or with never or do not) is not a claim about the world
IMPERATIVE = re.compile(r"^\W*(learn|hear|ask|label|listen|record|note|never|don't|do not|avoid|keep|write|check|test|run|start|end|open|close|let|probe|follow|stop|mark|say|show|"
                        r"read|give|take|add|drop|pull|split|score|compare|confirm|send|tell|walk|name|pick|choose|use|fill|paste|replace|raise|lower|move|treat|"
                        r"leave|go|look|find|plan|book|offer|thank|end|close|capture|probe|explore|watch|try|copy|count|sort|list|map|draft|review)\b", re.I)
GENERAL = re.compile(r"\b(many|most|mostly|usually|unusual|usual|typically|typical|tends?|tended|often|rarely|seldom|generally|commonly|likely|unlikely|probably|always)\b", re.I)
GEN_SOURCE = re.compile(r"\b\d+ of \d+\b|\binterviews? \d+\b|sector notes|\byou (said|wrote|told|believe|gave|named)\b|\byour (notes|hypothes[ie]s|words|belief|data|figures)\b|\bthe page\b|\baccording to\b", re.I)
GEN_PHRASES = re.compile(r"\bhow (many|often)\b|\bat most\b(?=[.,;:)]|$)|\btoo many\b|\b(matters|mattered|matter) most\b", re.I)
WORLD = re.compile(r"\b(you|your|yours|you're|you've|we|our|ours|customers?|clients?|buyers?|interviewees?|deals?|accounts?|leads?|signers?|"
                   r"champions?|users?|teams?|firms?|compan(y|ies)|segments?|operators?|founders?|heads?|cfos?|ceos?|ctos?|cios?|cisos?|chros?|coos?|"
                   r"directors?|managers?|principals?|vps?|owners?|people|person|persons|staff|employees?|buying|roles?|interviews?|wins?|loss|losses|contracts?|pilots?|"
                   r"they|their|them|he|she|his|her)\b", re.I)
ITEM = re.compile(r"\b(deal|interview|win|loss|account|lead|note|customer|call|pilot)s?\s+\d+\b", re.I)
SCOPE = re.compile(r"\b(all|every|each|none|no|neither|nor|nothing|nobody|only|never|always)\b", re.I)
ABSENCE = re.compile(r"\byou (gave|did not|didn't|have not|haven't|named|listed|wrote|said|told|asked|pasted|shared|mentioned)\b|\b(not given|not stated|not said|not named|"
                     r"not listed|missing|not in your|no figure|no target|no current|no value|no reason|reason not given|not compared|not available|no source|no page|"
                     r"(not |no \w+ )recorded|not in the notes|not say|does not say|do not say|did not say)\b", re.I)
ATTRIB = re.compile(r"\(?your (hypothes[ie]s|words|belief|note|notes|figures|data|ICP)\)?|\byou (said|wrote|told me|believe|named|listed)\b|\bas you (said|wrote|put it)\b", re.I)
CAUSE = re.compile(r"\b(because|since|therefore|hence|which means|that means|this means|so that|decides|depends|determines|drives|explains why)\b|, so\b", re.I)
HEDGE = re.compile(r"\b(may|might|could|perhaps|possibly)\b", re.I)
COND = re.compile(r"^(if|whether|when|where|unless|in case|suppose|assuming|(?:it is |this is )?(?:disproved|ruled out|contradicted|weakened) if)\b", re.I)
LABELS = {
    "slot": re.compile(r"\[user to (add|confirm|set|give)", re.I),
    "hypothesis": re.compile(r"\bhypothes[ie]s\b\s*[:(]|\(hypothesis|\bas a hypothesis\b|\bhypothesis to test\b", re.I),
    "to test": re.compile(r"\bto (test|confirm|validate)\b|\bworth checking\b|\bmarked to test\b", re.I),
    "assumption": re.compile(r"\bassum(ption|ed|e)\b", re.I),
    "as given by you": re.compile(r"\bas given by you\b|\bas you (gave|wrote|said) it\b", re.I),
    "as pasted": re.compile(r"\bas pasted\b|\bnot yet checked\b", re.I),
    "search result": re.compile(r"\bfrom a search result\b|\bpage not opened\b", re.I),
    "example default": re.compile(r"\bexample defaults?\b", re.I),
    "draft for you to confirm": re.compile(r"\bdraft for you to confirm\b", re.I),
}
NOTES_NAMED = re.compile(r"sector notes|\b[a-z ]+ row\b", re.I)
QUOTED = re.compile(r'"([^"\n]+)"|“([^”\n]+)”')
NUM = re.compile(r"(?<![\w.])[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?")
MONTHS = r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
DATE = re.compile(rf"\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}\s+{MONTHS}\.?(?:\s+\d{{4}})?\b|\b{MONTHS}\.?\s+\d{{1,2}}(?:,\s*\d{{4}})?\b|\b(?<=in |by |of )(?:19|20)\d{{2}}\b|(?<=since |until )(?:19|20)\d{{2}}\b|(?<=from )(?:19|20)\d{{2}}\b", re.I)
RANGE = re.compile(r"\b(?:between\s+)?(\d[\d,.]*)\s*(?:to|and|-)\s*(\d[\d,.]*)\b", re.I)
SENT_END = re.compile(r"([.!?][*_\"”)]{0,3})\s+(?=[\"“(*\[A-Z0-9])")


def sentences(text):
    """Sentences, and the clauses of a sentence split at semicolons, so a hedge or a label covers only its own clause."""
    out, held = [], []
    def keep(m):
        held.append(m.group(0)); return f"\x01{len(held) - 1}\x01"
    text = re.sub(r'"[^"\n]+"|\u201c[^\u201d\n]+\u201d', keep, text)   # a quote that runs over two sentences is never split
    # but a sentence that starts after a quote ending in . ! or ? is a new sentence
    # (never between a quote and a trailing attribution that ends the line: "(Interview 1, ops head)" or "Interview 2, CFO.")
    text = re.sub(r"(\x01(\d+)\x01[*_)]{0,3})\s+(?=[\"\u201c(*\[A-Z0-9\x01])(?!\(?(?i:interview|deal|win|loss|call|note|account|customer)s?\s+\d+\b[^\n.()|]*\)?\.?\s*(?:\||$))", lambda m: m.group(1) + ("\n" if re.search(r"[.!?][\"\u201d]$", held[int(m.group(2))]) else " "), text)
    text = re.sub(r"([.!?][*_\"\u201d)]{0,3})\s+(?=\x01)", "\\1\n", text)
    for x in SENT_END.sub("\\1\n", text).split("\n"):
        x = re.sub(r"\x01(\d+)\x01", lambda m: held[int(m.group(1))], x)
        if x.rstrip("*_ )").endswith("?"):
            out.append(x); continue   # a question stays whole
        quoted = []
        def hold(m):
            quoted.append(m.group(0)); return f"\x00{len(quoted) - 1}\x00"
        y = QUOTED.sub(hold, x.replace("“", '"').replace("”", '"'))   # a quote is never split
        parts = [c for c in re.split(r";\s+|,\s+(?=(?:and|but|while|whereas|so|which|because|since)\b)|\s+(?=(?:but|while|whereas)\b)", y) if c and c.strip()]
        out += [re.sub(r"\x00(\d+)\x00", lambda m: quoted[int(m.group(1))], c) for c in parts]
    return out
WORDS = re.compile(r"[a-z][a-z0-9']*")


def stem(w):
    w = w.lower().replace("’", "'")
    if w.endswith("'s"):
        w = w[:-2]
    w = w.strip("'")
    for suf, rep in (("ies", "y"), ("ied", "y"), ("ings", ""), ("ing", ""), ("edly", ""), ("ers", ""), ("er", ""), ("ed", ""), ("ly", ""), ("s", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: len(w) - len(suf)] + rep
    return w


FACT_FORMS = set("""buy buys bought buying sell sells sold selling use uses used using owns owned handle handles handled decide decides decided
depend depends depended know knows knew bring brings brought run runs running ran open opens opening sign signs signed approve approves approved choose
chooses chose chosen pay pays paid renew renews renewed manage manages managed large larger largest small smaller smallest big bigger regulated enterprise
enterprises global local hand experience""".split())
# present tense forms: a sentence that says what a group or a role does is about the world even with no "you" or role word
FACT_PRESENT = re.compile(r"\b(buys?|sells?|uses|owns|handles?|decides?|depends?|knows|brings?|signs?|approves?|chooses?|pays?|renews?|manages|prefers?|cares|expects?|blocks?)\b", re.I)


def light(w):
    """A lighter stem for the fact words: buyer is not buy, seller is not sell."""
    w = w.lower().replace("’", "'")
    if w.endswith("'s"):
        w = w[:-2]
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: len(w) - len(suf)]
    return w


def norm_text(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[*_`|]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def stems_of(text):
    return {stem(w) for w in WORDS.findall(text.lower().replace("’", "'"))}


def fig_key(tok):
    t = tok.replace(",", "").lstrip("+-")
    pct = t.endswith("%")
    t = t.rstrip("%")
    try:
        v = float(t)
    except ValueError:
        return None
    return (round(v, 6), pct)


def significant(tok):
    t = tok.replace(",", "").lstrip("+-")
    if t.endswith("%") or "." in t:
        return True
    try:
        return float(t) >= 10
    except ValueError:
        return False


def section_label(line):
    """A bold label line ending in a colon ("**Next steps:**", "**Interview 2:**") states nothing and is skipped; one that says what someone
    does or will do ("**Why the CFO will sign this quarter:**") is a claim and is checked."""
    m = re.fullmatch(r"\*\*([A-Za-z0-9 ,()]{1,40}):\*\*", line)
    if not m:
        return False
    lab = m.group(1).strip()
    if FACT_PRESENT.search(lab) or re.search(r"\b(will|would|should|must|can|why|because|is|are|was|were)\b", lab, re.I):
        return False
    return len(lab.split()) <= 5 and (not WORLD.search(lab) or bool(ITEM.fullmatch(lab)) or bool(re.fullmatch(r"(open )?questions?|next steps?|risks?.*", lab, re.I)))


def units(text):
    """(line number, kind, unit text, whole line) for every checkable piece; kind is 'row' for a table row, else 'prose'."""
    out, fence, prev = [], False, ""
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        last, prev = prev, line
        prev_line = last
        if line.startswith("```"):
            fence = not fence
            continue
        if fence or not line or line.startswith("#") or line.startswith(">") or re.fullmatch(r"\*\*[HQ]\d+[a-z]?\b[^*\d%\"]*(\(about \d+ minutes?\))?\*\*", line) or section_label(line):
            continue
        if line.startswith("|"):
            if re.fullmatch(r"[|:\- ]+", line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            header = not (prev_line or "").startswith("|")
            for ci, c in enumerate(cells):
                if (header or ci == 0) and len(c.split()) <= 3 and not re.search(r"\d", c) and not FACT_PRESENT.search(c):
                    out.append((n, "label", c, line))   # a header cell or a row label: checked for fact and domain words only
                    continue
                for s in sentences(c):
                    if s.strip():
                        out.append((n, "row", s.strip(), line))
            continue
        line = re.sub(r"^([-*+]|\d+[.)])\s+", "", line)
        for s in sentences(line):
            if s.strip():
                out.append((n, "prose", s.strip(), line))
    return out


def skill_texts():
    """The skill's own SKILL.md and reference files (method words, not facts) and its sector notes, read from the folder this script sits in."""
    import pathlib
    base = pathlib.Path(__file__).resolve().parent.parent
    method, notes = [], []
    for p in [base / "SKILL.md"] + sorted((base / "references").glob("*.md")):
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
            # worked examples are not method words: an invented example fact must never become a source
            t = re.sub(r"\n### Example.*?(?=\n## )", "\n", t, flags=re.S)
            (notes if p.name == "sector-notes.md" else method).append(t)
        except OSError:
            pass
    return "\n".join(method), "\n".join(notes)


class Sources:
    def __init__(self, user, scripts, pages, notes):
        method, own_notes = skill_texts()
        notes = notes or own_notes
        self.user, self.scripts, self.pages, self.notes = user, scripts, pages, notes
        self.user_figs = {fig_key(t) for t in NUM.findall(user)} - {None}
        u1 = user.replace("\u2018", "'").replace("\u2019", "'")   # curly single quotes (phones, Word, Google Docs) read as straight ones
        u1 = re.sub(r"(?<=[a-z]s)'(?= [a-z](?:[^'\n]|(?<=\w)'(?=\w))*?'(?=[\s.,;:)!?]|$))", "\u02bc", u1)   # a plural possessive ("drivers' app") does not end a quote when the quote closes later on the line
        uq = re.findall(r"(?:^|[\s(:;,])'(.+?)'(?=[\s.,;:)!?]|$)", u1, re.S) + [a or b for a, b in QUOTED.findall(user.replace("\u201c", '"').replace("\u201d", '"'))]
        self.user_quoted = norm_text(" | ".join(uq).replace("\u02bc", "'"))
        self.method_stems = stems_of(method)
        from collections import Counter
        uses = Counter(stem(w) for w in WORDS.findall(method.lower().replace("’", "'")))
        self.domain = {w for w in stems_of(own_notes) if uses[w] < 4}   # sector and domain words (segments, roles, industries), not the method's everyday words
        self.method_only = self.method_stems - self.domain   # method words that are not sector or domain words
        self.norm_method = norm_text(method + "\n" + notes)
        self.all_text = "\n".join([user] + scripts + pages)
        self.norm_all = norm_text(self.all_text)
        self.stems = stems_of(self.all_text)
        self.light = {light(w) for w in WORDS.findall(self.all_text.lower().replace("’", "'"))}
        self.note_stems = stems_of(notes) if notes else set()
        self.script_lines = [norm_text(l) for s in scripts for l in s.splitlines() if l.strip() and not re.fullmatch(r"[|:\- ]+", l.strip())]
        self.script_line_set = set(self.script_lines)
        self.script_keys = []   # (key, whole line): "largest percentage gap" from "Largest percentage gap: Average contract value", a row's first cell
        for l in [x for t in scripts for x in t.splitlines()]:
            t = l.strip()
            if t.startswith("|") and not re.fullmatch(r"[|:\- ]+", t):
                first = norm_text(t.strip("|").split("|")[0])
                if first and len(first.split()) <= 5 and first not in ("metric", "criterion", "dimension", "part"):
                    self.script_keys.append((first, norm_text(t), True))
            elif re.match(r"^[A-Za-z][A-Za-z ()%]{3,40}:\s+\S", t) and not re.match(r"^(tier [abcd]|maximum score)", t, re.I):
                self.script_keys.append((norm_text(t.split(":")[0]), norm_text(t), False))
        self.script_cells = {}   # a table cell or a part of a line between pipes or semicolons, such as "+39% increase needed"
        for l in [x for t in scripts for x in t.splitlines()]:
            for cell in re.split(r"\s*[|;]\s*", l):
                cell = norm_text(cell).strip(" .")
                for tok in NUM.findall(cell):
                    k = fig_key(tok)
                    if k and len(cell.split()) >= 2:
                        self.script_cells.setdefault(k, []).append(cell)
        self.script_figs = {}
        for l in self.script_lines:
            for tok in NUM.findall(l):
                k = fig_key(tok)
                if k:
                    self.script_figs.setdefault(k, []).append(l)
        self.source_figs = {fig_key(t) for t in NUM.findall(self.all_text)} - {None}
        self.ranges = {(fig_key(a), fig_key(b)) for a, b in RANGE.findall(self.all_text)}


def check_unit(u, src):
    n, kind, s, whole = u
    label_cell = kind == "label"
    if label_cell:
        kind = "row"
    needs, notes = [], []
    if norm_text(whole) in src.script_line_set:
        return needs, ["copy of a script line"], []
    s_clean = s.replace("’", "'")
    quotes = [a or b for a, b in QUOTED.findall(s_clean.replace("“", '"').replace("”", '"'))]
    body = QUOTED.sub(" ", s_clean)
    body = re.sub(r"`[^`]*`|https?://\S+|(?:[\w.-]+/)+[\w.-]+", " ", body)   # code spans, links and file paths are not claims
    is_q = s_clean.rstrip("*_ )").endswith("?")
    is_cond = bool(COND.match(re.sub(r"^[*_\s]+", "", body)))
    if is_cond and re.search(r"\b(because|since|as|given that|which means)\b|:", body, re.I):
        is_cond = False   # a condition that also states a reason or a fact is read as a statement
    labels = [k for k, rx in LABELS.items() if rx.search(s_clean)]
    hedged = bool(HEDGE.search(body))
    # QUOTE: every quote of three or more words must be in a source
    for q in quotes:
        qn = norm_text(q).strip(" .,;:")
        if q.rstrip().endswith("?") or re.match(r"(walk|tell|describe|talk|take|show|explain|who|what|how|why|when|which|where|did|do|does|have|has|is|are|can|could|would|will)\b", qn):
            continue
        if len(q.split()) >= 3 and qn not in src.norm_all and qn not in src.norm_method:
            needs.append(("QUOTE", f'"{q}" is not word for word in your message, a script output or a page'))
        elif src.user_quoted is not None and re.search(r"\binterview(ee)?s?\s+\d+|\b(said|says|told)\b", body, re.I) \
                and qn in src.norm_all and qn not in src.user_quoted and not re.search(r"\bnote\b|not a quote|as noted", s_clean, re.I):
            needs.append(("QUOTE", f'"{q}" is the note\'s text, not words the notes quote from the person; write it as a note (no quote marks), or quote only words the notes put in quotes'))
    # FIGURE ("67 percent" is read as 67%)
    wnorm = norm_text(re.sub(r"(\d) ?per ?cent\b", r"\1%", whole))
    fbody = re.sub(r"(\d) ?per ?cent\b", r"\1%", DATE.sub(" ", body))
    small_units = {fig_key(m.group(1)) for m in re.finditer(r"(?<![\w.])([-+]?\d+(?:\.\d+)?)\s*(points?|days?|weeks?|months?|years?|pts)\b", fbody)}
    for tok in NUM.findall(fbody):
        k = fig_key(tok)
        if k is None or not (significant(tok) or k in small_units):
            continue
        if k in src.user_figs:
            continue
        if k in src.script_figs:
            if not any(sl in wnorm for sl in src.script_figs[k]) and not any(c in wnorm for c in src.script_cells.get(k, [])):
                needs.append(("FIGURE", f"{tok} is a script figure; copy the script's own line whole instead of restating it"))
        elif k not in src.source_figs:
            needs.append(("FIGURE", f"{tok} is in no source (your message, a script output or a page)"))
    for a, b in RANGE.findall(fbody):
        ka, kb = fig_key(a), fig_key(b)
        if ka and kb and (significant(a) or significant(b) or float(b.replace(",", "") or 0) >= 10) and (ka, kb) not in src.ranges and not any(f"{a} to {b}" in sl for sl in src.script_lines):
            if not (ka in src.source_figs and kb in src.source_figs and re.search(rf"{re.escape(a)}\s*(to|and|-)\s*{re.escape(b)}", src.all_text)):
                needs.append(("FIGURE", f"the range {a} to {b} is in no source; copy a script's range or the user's own"))
    # SCRIPT VERDICT: a verdict line written in the script's own form ("Largest percentage gap: ...") or a table row whose first cell is a
    # script row's first cell (a metric, a criterion) must be the script's printed line or row, copied whole
    for key, full, is_row in src.script_keys:
        if is_row:
            hit = kind == "row" and norm_text(whole.strip().strip("|").split("|")[0]) == key and norm_text(whole) != full
        else:
            hit = re.search(rf"(^|\s){re.escape(key)}\s*:", wnorm) is not None and full not in wnorm
        if hit:
            needs.append(("FIGURE", f"restates the script's \"{key}\" line or row in other words; copy it whole"))
            break
    # GENERAL
    g = GENERAL.search(GEN_PHRASES.sub(" ", body))
    if g and not is_q and not labels and not GEN_SOURCE.search(s_clean):
        needs.append(("GENERAL", f"'{g.group(1)}' with no named source"))
    world = kind == "row" or bool(WORLD.search(body)) or bool(re.search(r"\b[\w-]+\.(?:com|io|ai|co|in|net|org|app|tech|space)\b", body, re.I)) or bool(FACT_PRESENT.search(body)) or any(stem(w) in src.stems and w[:1].isupper() for w in re.findall(r"\b[A-Z][a-zA-Z0-9]+\b", body[1:]))
    imperative = bool(IMPERATIVE.match(body))   # an instruction to the reader: its 'never' or 'each' is not about the user's items
    exempt = is_q or is_cond or bool(labels) or (bool(ATTRIB.search(s_clean)) and bool(quotes))
    if not exempt:
        # the sector notes source a line that names the row, never a line about the user ("you", "your")
        names_notes = bool(NOTES_NAMED.search(s_clean)) and bool(src.note_stems) and not re.search(r"\b(you|your)\b", body, re.I)
        allowed = src.stems | (src.note_stems if names_notes else set())
        # a sentence about the user or their customers, segment, buyers, accounts or deals: every added word counts, and the skill's text sources none
        about_user = bool(re.search(r"\b(you|your|yours|you're|you've|customers?|clients?|buyers?|segments?|accounts?|deals?|base|icp|interviewees?|we|our|fit|fits|target|targets|market|markets)\b", body, re.I))
        strict = (about_user or kind == "row") and not label_cell
        meta = re.match(r"\W*(i|i've|i'm|this (answer|guide|draft|review|model|plan|table)|the (script|table|tally|counts?|guide|questions?|template|opening|closing)|"
                        r"(no|every|each) (question|figure|probe)|questions?|every figure|each figure|counts|Q\d+[a-z]?|it (lists|shows|holds|gives|copies|uses|has|is (a|the) (draft|table|list|guide|script)))\b", body.strip(), re.I)   # about the answer itself ("it" alone may be a customer or an account: run 35C LS-4)
        # what a sentence can add to the user's facts: a fact word (buys, signs, large, regulated ...), a domain word (any word of the
        # sector notes: segments, roles, industries, measures), a role word or a name; plain English and method words add no fact
        caps = {w.lower() for w in re.findall(r"\b[A-Z][a-zA-Z0-9]+\b", body)}
        added = sorted({w for w in WORDS.findall(body.lower()) if len(w) > 2 and not w.isdigit() and (
            (w in FACT_FORMS and light(w) not in src.light) or
            (w not in FACT_FORMS and w not in STOP and stem(w) not in STOP and stem(w) not in allowed
             and (strict or stem(w) in src.domain or WORLD.fullmatch(w) or w in caps)
             and (strict or stem(w) not in src.method_only)))})
        guide_part = re.match(r"\W*(the (guide|questions?|template|opening|closing)|(no|every|each) (question|probe)|questions?|Q\d+[a-z]?)\b", body.strip(), re.I)
        if added and not guide_part and not (imperative and not strict):
            needs.append(("ADDS", "words no source holds: " + ", ".join(added[:8]) + (" (a hedge does not make an added fact a guess: ask it as a question)" if hedged else "")))
        counted = any(c in src.norm_all for c in re.findall(r"\b\d+ of \d+\b", s_clean))
        if world and not hedged and SCOPE.search(body) and not quotes and not ABSENCE.search(s_clean) and not meta and not counted and not imperative:
            needs.append(("SCOPE", f"'{SCOPE.search(body).group(1)}' about your items with nothing quoted"))
        cm = CAUSE.search(body)
        if world and not hedged and cm and not re.search(r'"', s_clean.replace("“", '"').replace("”", '"')[s_clean.find(cm.group(0)) + len(cm.group(0)):] if s_clean.find(cm.group(0)) >= 0 else ""):
            needs.append(("CAUSE", f"a reason or rule ('{cm.group(0).strip(', ')}') with nothing quoted after it"))
        if re.search(r"\b([\w-]+\.(?:com|io|ai|co|in|net|org|app|tech|space)|the page|their page|its page|the site|its site|the website)\b", body, re.I) and \
                re.search(r"\b(says|said|describes|described|names|named|lists|listed|shows|calls|states|claims|mentions)\b", body, re.I) and not quotes:
            needs.append(("PAGE", "says what a page says without quoting it; quote the page's words, or say the page does not say it"))
        fp = FACT_PRESENT.search(body)
        if world and not hedged and fp and not quotes and not meta:
            needs.append(("RULE", f"says what a person or group does ('{fp.group(1)}') with nothing quoted: quote the user, or make it a question, a condition or a labelled hypothesis"))
        if world and not hedged and ITEM.search(body) and not quotes and not s_clean.lstrip("*_ ").startswith("("):
            needs.append(("ITEM", f"says what {ITEM.search(body).group(0)} holds without quoting it; quote the words of that item"))
    if world:
        if is_q:
            notes.append("question")
        elif is_cond:
            notes.append("condition")
        elif labels:
            notes.append("label: " + ", ".join(labels))
        elif hedged:
            notes.append("hedged")
        elif quotes:
            notes.append("quotes your words")
        else:
            notes.append("matches the sources")
    return needs, notes, labels


def ledger(files, src, final=False):
    report, total_needs, label_kinds = [], 0, {}
    for name, text in files:
        report.append(f"== {name}")
        kinds = set()
        for u in units(text):
            needs, notes, labels = check_unit(u, src)
            kinds.update(labels)
            if needs:
                total_needs += 1
                report.append(f"NEEDS line {u[0]}: {u[2]}")
                for k, why in needs:
                    report.append(f"    {k}: {why}")
            elif notes and not final:
                report.append(f"ok    line {u[0]} ({notes[0]}): {u[2][:90]}")
        label_kinds[name] = kinds
        report.append(f"labels in {name}: {', '.join(sorted(kinds)) or 'none'}")
    drops = []
    if len(files) > 1:
        every = set().union(*label_kinds.values())
        for name, kinds in label_kinds.items():
            for k in sorted(every - kinds):
                if k in ("slot", "example default", "draft for you to confirm", "as pasted", "search result", "as given by you"):
                    drops.append(f"LABEL DROP: '{k}' is in another delivered file but not in {name}; keep the same label wherever the same line appears")
    report += drops
    for name, text in files:
        report.append(f"digest {name}: {digest(text)}")
    short = ", ".join(f"{name.replace(chr(92), '/').rsplit('/', 1)[-1]}={digest(text)}" for name, text in files)
    report.append(f"claim_ledger: {total_needs} line{'' if total_needs == 1 else 's'} NEEDS a source, a label or a rewrite; {len(drops)} label drop{'' if len(drops) == 1 else 's'}; digests {short}")
    bad = total_needs + len(drops)
    if final:   # the verdict first, so a shortened tool output still shows it
        report.insert(0, f"claim_ledger --final: PASS, reply digest {digest(files[0][1])}" if not bad else f"claim_ledger --final: NOT DELIVERABLE, {bad} to fix")
    if final and bad:
        report.append("NOT DELIVERABLE: fix every NEEDS line and LABEL DROP, then run --final again as your last tool call.")
    elif final:
        name, text = files[0]
        d = digest(text)
        body = "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").strip().splitlines())
        saved = "; ".join(f"{n} ({digest(t)})" for n, t in files[1:]) or "none"
        report.append(f"DELIVER: send as your whole chat reply exactly the text between the two marker lines below (the checked {name}), with nothing "
                      f"before or after it and no word changed. Saved files checked: {saved}. To change anything, edit the file and run --final again.")
        report += [f"=== BEGIN CHECKED REPLY {d} ===", body, f"=== END CHECKED REPLY {d} ==="]
    return report, bad


def digest(text):
    t = "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").strip().splitlines())
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def read(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8-sig", errors="replace")


def main(argv):
    args, files, opts = [a for a in argv[1:] if a != "--final"], [], {"--user": [], "--script": [], "--page": [], "--notes": []}
    final = "--final" in argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a in opts:
            if i + 1 >= len(args):
                print(f"claim_ledger: {a} needs a file"); return 2
            opts[a].append(args[i + 1]); i += 2
        else:
            files.append(a); i += 1
    if not opts["--user"]:
        print("claim_ledger: --user USER.txt is required (the user's message copied whole)"); return 2
    if not files:
        print("claim_ledger: no file to check (pass the reply and every saved file)"); return 2
    try:
        user = "\n".join(read(p) for p in opts["--user"])
        scripts = [read(p) for p in opts["--script"]]
        pages = [read(p) for p in opts["--page"]]
        notes = "\n".join(read(p) for p in opts["--notes"])
        texts = [(p, read(p)) for p in files]
    except OSError as e:
        print(f"claim_ledger: cannot read {e.filename}: {e.strerror}"); return 2
    if not user.strip() or not any(t.strip() for _, t in texts):
        print("claim_ledger: nothing to read"); return 2
    report, bad = ledger(texts, Sources(user, scripts, pages, notes), final)
    print("\n".join(report))
    return 1 if bad else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.exit(main(sys.argv))
