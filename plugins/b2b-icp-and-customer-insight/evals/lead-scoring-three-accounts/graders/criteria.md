---
type: llm
---

The user's request, word for word:
<request>
Build a fit scoring model from our ICP and score these three accounts.

Criteria:
- Industry (critical): logistics best, then retail, then other.
- Company size (important): 500 to 2,000 employees best, then 200 to 499, then under 200.
- Own delivery fleet (nice to have): yes is better than no.

Accounts:
- Account 1: logistics, 500 to 2,000 employees, own fleet yes.
- Account 2: retail, 200 to 499 employees, own fleet not known.
- Account 3: manufacturing, 500 to 2,000 employees, own fleet no.
</request>

The user gave three criteria with an importance each but no weights, and three accounts. Account 2's own fleet value is not known. Account 3's industry is "manufacturing", which is not literally one of the listed values (logistics, retail, other).

PASS only if all of these hold:
1. If the user gave no weights, any weights used are labelled as example defaults or starting examples the team can change, never as a benchmark, standard or best practice.
2. The maximum score equals the sum of the top points of each criterion, and Account 1 (best value on every criterion) gets the maximum and the top tier.
3. Account 2 is not given a final score or tier as if complete: it is marked incomplete or provisional because own fleet is not known, and the missing value is not scored as 0 without saying so.
4. Account 3's "manufacturing" is either marked for the user to confirm before scoring, or scored as "other" with a clear note that this mapping is an assumption for the user to confirm.
5. It explains how to check the model against the team's own closed won and lost deals, and does not give conversion rates, win rates or response times for tiers.

FAIL if any of these happen, whatever else the reply does well:
- It invents a fact or figure the user did not give: a named person or company, a customer, a competitor, a result, a statistic, a benchmark, a typical or industry value, a deadline or a money amount. Arithmetic on the user's own figures is allowed only when it is correct. A suggestion clearly marked as a suggestion, an example default labelled as one, a placeholder such as "[User to add: ...]", and naming which of its own reference notes it used (marked as something to confirm or test) are not invented facts. Restating what the user wrote in the request above is not invention.
- It recommends buying, adopting or switching to a named software product, tool or vendor. (Pointing the user to another plugin or skill by name for work outside this request is a hand off, not a software recommendation.)
- It names any real company or person as the user's client, prospect, buyer or customer.
- It is not plain English: hype or marketing words (for example "game changer", "supercharge", "unlock", "seamless", "robust"), exclamation marks, or jargon left unexplained for the reader named in the request.
- It uses a dash as punctuation: an em dash, an en dash, or a hyphen with a space on each side between words. Hyphens inside compound words, hyphens that start a list item and hyphens in table borders are fine.
