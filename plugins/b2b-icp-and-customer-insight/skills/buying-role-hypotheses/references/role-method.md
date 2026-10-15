# Buying role hypotheses method

## The roles (product level, before any deal)
- **Champion**: the person who owns the problem day to day, gains most if it is solved, and will spend their own credibility to push the purchase inside. Signs: they describe the problem in their own measures, they ask how to get it approved, they introduce others.
- **Economic buyer**: the person who can release the budget and say yes when others disagree. Who this is depends on the price band and the buyer's own approval rules, which differ by company; the skill asks rather than assumes a threshold.
- **Technical evaluator**: the person who tests whether it works in their environment (IT, security, engineering, operations systems). Whether they can stop or start a deal at this buyer is part of the hypothesis to test.
- **Other reviewers**: procurement, legal, finance, risk and compliance, data protection, information security or vendor risk review; they check terms and risk. For a larger or regulated buyer (enterprise, bank or NBFC, insurer, telco, government body), or a product that touches the buyer's data or systems, always name procurement and the security or vendor risk review as hypotheses (decide "larger or regulated" from the user's words or a page; if neither says, write "if your buyers are large or regulated" rather than stating it), each with a validation question ("Which teams reviewed the last purchase of this kind, in what order, and how long did each take?") and what would disprove it.
- **Daily users**: the people whose work changes; whether their adoption shapes renewal is a hypothesis to test with the user's own renewal history, never a fact to state.

## Building each hypothesis
The role descriptions above define the words this method uses; they are not facts about any buyer. The "why" for a title comes from the user's words, the deal notes (for example "Deal 1: found you after a petty cash audit") or the sector notes row named and marked to test, never from a description of what that role does at every company.

For each role, write:
| Role | Hypothesis (the likely title and why, from the user's words) | Validation question | What would disprove it |
|---|---|---|---|
- "Why" comes from the user's own description of the problem, product and buyer, the deal notes, or the sector notes row named and marked to test; quote the user's words.
- The validation question is one a seller or researcher can ask a real buyer (open, about past events): "Who brought this problem to leadership last time?", "Who signed the last purchase of this size?", "Who tested the last tool like this before it was approved?"
- What would disprove it: the evidence that would move the role elsewhere ("the last two purchases were signed by the COO, not the CFO"). Every role row carries one, the short form included ("disproved if ...").

## Evidence moves hypotheses
When the user gives interview notes, win notes or loss notes, mark each hypothesis: supported (with the note), contradicted (with the note), or untested. Roles, not names. A hypothesis is never "confirmed" by a handful of notes.

## Anti champion signs (to test, not to judge people)
- Talks only about features, never about the problem's cost.
- Cannot say who else would be involved or how a purchase is approved.
- Hands every step to someone junior.
- No reason why now.
Each sign comes with the question that tests it ("What happens if this is not solved this year?").

## Price and approval
Whether a higher price band brings more reviewers or a more senior signer, and where the line sits, is the buyer's own rule. The skill asks for the price band and, if known, the buyer's approval rules; it never invents a threshold.

## What this skill does not do
- It does not map the buying group of one live deal with named people (Deal Execution plugin, discovery-and-buying-group).
- It does not write messages for each role (positioning-and-messaging in gtm-skills).
- It does not find accounts or people (account-research in the research plugin).

## Check before delivering
Run `python3 "<skill folder>/scripts/role_check.py" draft.md` with the full path to this skill's folder (or `python` where `python3` is not found, as on Windows) on the draft: it flags long or short dashes, a role label damaged by a part word replace, and a hypothesis row without a validation question.
