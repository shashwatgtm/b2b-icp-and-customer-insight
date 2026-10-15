# ICP review method

## Part A: today's customers against the ICP

Split each profile (the user's description of today's customers, and the ICP they wrote) into parts. Keep the user's words for every part.

| Part | What to look for | Example wording to copy from the user |
|---|---|---|
| Segment | industry, sub sector, business model | "D2C brands", "regional NBFCs", "global capability centres" |
| Size | employees, revenue, volume (orders, vehicles, endpoints, sites) | "200 to 1,000 employees", "5,000 orders a month" |
| Buyer | the role that buys or champions | "head of operations", "CISO" |
| Problem | the job they need done or the pain | "who struggle with reconciliation" |
| Place | regions, cities, countries | "India and the Gulf" |
| Exclusions | who the ICP says to avoid | "not marketplaces", "no public sector" |
| Other | anything else the user wrote (stack, stage, trigger) | "on SAP", "Series A to C" |

Then class each part of today's base against the ICP:
- **Matches**: the same part in the user's words (or plainly the same thing, said why).
- **Partly**: overlaps but differs on size, region or sub segment; say how.
- **Not in the ICP**: a part of today's base the ICP does not name (a drift to check, not an error).
- **ICP part missing from today's base**: the ICP names it and no current customer description shows it (the gap to close or the ICP part to question).
- **Conflict**: the base and the ICP say opposite things (for example the ICP excludes marketplaces and the base lists marketplace customers).

Never decide a match from a part of a word (for example "fin" inside another word). When unsure, put it under Partly and ask.

## Part B: metric gaps (run scripts/icp_gap.py)

Give the script only figures the user gave. A metric with one side missing is reported missing; never filled with a typical value. After the table:
1. Name the largest percentage gap (the script's line) and the High priority gaps.
2. For each metric behind target, give the checks from references/causes-to-check.md that the user's own notes make most likely, and say which note points that way.
3. NPS is in points and never compared with a percentage.
4. When a target is already met, say so and do not suggest work on it.

## Part C: how the ICP should change (wins, losses, market changes)

For each recent win, loss or market change the user gives:

| Input | Class | How to decide |
|---|---|---|
| A win | Confirms the ICP | every part of the win sits inside the ICP's parts |
| A win | Candidate addition | it has a part the ICP does not name (a new segment, size, region, buyer); quote the words that make it new |
| A loss | Reason class | price or budget; one vendor or suite preferred; incumbent or competitor; timing or priority; fit (missing feature, wrong size); other. Read the class from the user's stated reason only; if the reason is not stated, write "reason not given" |
| A loss | Candidate disqualifier | the same reason appears in two or more losses with a shared part (size, segment, buyer) |
| A market change | Implication to check | which ICP part it may move (segment, size, buyer, problem), stated as a question |

Write each proposed change as a hypothesis:

| Proposed change | Evidence from your notes | How to test it in your CRM or next interviews | What would disprove it |
|---|---|---|---|
| Add on trial: [part] | "[the user's words]", wins 2 and 5 | compare win rate and cycle of deals with and without this part over the last two quarters | the part's deals close no better than the core |

A change is "on trial" until the user's own data confirms it. A single win or loss never changes the ICP by itself; it opens a hypothesis.

## Part D: the draft revised ICP

Write the revised ICP as the user's ICP with marked changes: Keep (unchanged parts), Add on trial, Qualify out on trial, Question (a part the evidence weakens), Open (a part no evidence touches). Then the CRM fields to pull to test it (for example industry, employee band, region, buyer role, loss reason, cycle days, contract value), named generically because the user's CRM is not known.

## Hand offs
- No ICP yet, or the user wants an ICP card from scratch or a list of accounts: account-research in the research plugin (b2b-research-market-and-account).
- Why deals are lost to a named competitor, battle cards: competitive-intelligence in b2b-sales-enablement.
- Saving one account at renewal: renewal-save-plan in b2b-customer-success.
