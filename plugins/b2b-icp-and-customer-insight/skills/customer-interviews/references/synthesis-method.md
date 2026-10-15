# Synthesis method

## 1. Structure each interview (in the interviewee's words)
For each interview, fill these fields from the notes, quoting or closely keeping the words used:
- label (Interview 1, 2 ...) and role (the job title or function exactly as the notes give it, nothing added: company size, sector or stage stay out of the role field (keep them in your own reading of each interview, for the ICP changes in section 4), so two interviews with the same title count as the same role; never the person's name in the output unless the user asks)
- pains: problems they described
- triggers: the event that made them look or act
- objections: concerns, doubts, reasons not to buy or to leave
- value: outcomes they said they got or want, in their measures
- quotes: memorable lines, word for word
- hypotheses: for each team hypothesis, exactly "supports", "contradicts" or "no evidence" from this interview

## 1a. The JSON shape for scripts/interview_tally.py

```
{"hypotheses": ["H1", "H2"],
 "interviews": [
   {"label": "Interview 1", "role": "Head of finance",
    "pains": ["..."], "triggers": ["..."], "objections": ["..."], "value": ["..."], "quotes": ["..."],
    "hypotheses": {"H1": "supports", "H2": "no evidence"}}],
 "next_round": {"minimum_per_group": 5, "groups": [{"name": "Paying teams", "done": 0, "planned": 3}]}}
```
"next_round" is optional: one entry per group the next round plan names, with whole numbers for done and planned; "minimum_per_group" is the user's own (if left out, the script uses 5 and labels it as its own line, not a research standard).
Every list holds text items. Verdicts are exactly supports, contradicts or no evidence. A hypothesis id in an interview must be one of the ids in the top level list (case aside); otherwise the script stops and names it. An interview that points both ways on one hypothesis gets "no evidence" and the split is listed in the open questions.

One item is one idea. Two notes saying the same thing in the same words are one item. When two items differ only in wording but mean the same, write them in the same words in both interviews and tell the user you merged them (list each merge). Never merge items that differ in meaning ("not a priority" is not "a priority").

## 2. Count (run scripts/interview_tally.py)
Each item counts once per interview. The script prints "k of n interviews (x%)", names ties at the top, warns when every interview has identical items (copied template or summary), tallies the hypotheses and adds a note when there are fewer than five interviews.

## 3. Read the counts
- A pattern needs the same item in several interviews; with fewer than five interviews, call it a direction.
- A hypothesis with both support and counter evidence is mixed, never confirmed. Support from some interviews is "leans towards support (not proof)".
- Separate what customers said they did (behaviour) from what they said they would do (opinion); weight behaviour.
- Keep a result the customer stated apart from a claim the team or a website made.

## 4. Turn patterns into changes (all hypotheses)
- ICP: segments, sizes or roles where the pains and triggers cluster; a candidate change to test with icp-review if installed.
- Messages: the pain and value phrases customers used, word for word, to test in copy (messaging work itself is positioning-and-messaging in gtm-skills).
- Discovery questions: new questions that probe the top pains and triggers.
- Next round: what to ask, and who to interview, to settle mixed hypotheses; the numbers per group come from the script's next round lines (done + planned = total, and how many short), never from a sum done by eye.

## 5. People and privacy
Notes may name interviewees and their companies. The output refers to them by label and role ("Interview 3, head of operations") unless the user asks for names. Quotes are kept word for word; if a quote itself contains a person's name, the name alone is replaced by "[name removed]" and the user is told, or the quote is left out with a note. A label is never a name. Nothing about health, family or private life is carried into the synthesis even if it appears in the notes.
