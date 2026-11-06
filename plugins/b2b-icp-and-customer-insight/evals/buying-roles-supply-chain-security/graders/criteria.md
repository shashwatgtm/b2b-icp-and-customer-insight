---
type: llm
---

The user's request, word for word:
<request>
We sell a tool that checks open source dependencies for software supply chain risk, to mid sized banks. Buyers tell us things like "our developers pull packages from everywhere" and "audit asked us for a list of every library in production".

Before we build our outbound, who is likely to champion, sign and evaluate a purchase like ours?
</request>

The user gave: a tool that checks open source dependencies for supply chain risk; buyers are mid sized banks; two buyer quotes ("our developers pull packages from everywhere"; "audit asked us for a list of every library in production"). No price, deal size or approval rules were given.

PASS only if all of these hold:
1. It gives role hypotheses for at least the champion, the signer and the evaluator (and may add reviewers and daily users), each framed as a hypothesis, not a fact.
2. Each role has a question that would validate it and a statement of what would disprove it.
3. The reasoning uses the user's own buyer words or product description, not generic claims about banks.
4. It says the signer depends on the deal price and the bank's own approval rules, and does not state a spend threshold or approval limit.
5. It names roles and titles only, never real people, and gives no gender to a role.
6. It suggests how to test the hypotheses next (for example which roles to interview and what to ask).

FAIL if any of these happen, whatever else the reply does well:
- It invents a fact or figure the user did not give: a named person or company, a customer, a competitor, a result, a statistic, a benchmark, a typical or industry value, a deadline or a money amount. Arithmetic on the user's own figures is allowed only when it is correct. A suggestion clearly marked as a suggestion, an example default labelled as one, a placeholder such as "[User to add: ...]", and naming which of its own reference notes it used (marked as something to confirm or test) are not invented facts. Restating what the user wrote in the request above is not invention.
- It recommends buying, adopting or switching to a named software product, tool or vendor. (Pointing the user to another plugin or skill by name for work outside this request is a hand off, not a software recommendation.)
- It names any real company or person as the user's client, prospect, buyer or customer.
- It is not plain English: hype or marketing words (for example "game changer", "supercharge", "unlock", "seamless", "robust"), exclamation marks, or jargon left unexplained for the reader named in the request.
- It uses a dash as punctuation: an em dash, an en dash, or a hyphen with a space on each side between words. Hyphens inside compound words, hyphens that start a list item and hyphens in table borders are fine.
