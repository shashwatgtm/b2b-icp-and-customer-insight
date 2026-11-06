---
type: llm
---

The user's request, word for word:
<request>
PMF check please. We sell route planning software to fleet operators. Last quarter against our targets:
- Monthly logo churn: 3.1% (target 2%)
- NPS: 28 (target 40)
- LTV 9 lakh and CAC 4 lakh (target LTV to CAC of 3)
- 90 day retention: 81% (target 85%)
- Activation, meaning first route planned within 7 days: 64% (target 70%)

Customer feedback: one customer wrote "We cut planning time from two hours to forty minutes." Another wrote "Setup took longer than the sales team said."
</request>

The user gave five metrics with their own targets: monthly logo churn 3.1% vs 2%; NPS 28 vs 40; LTV 9 lakh and CAC 4 lakh vs a target LTV to CAC of 3; 90 day retention 81% vs 85%; activation 64% vs 70%; and two customer quotes.

Correct arithmetic: LTV to CAC is 9 / 4 = 2.25, behind the target of 3 (a 33% increase needed). NPS is 12 points behind. Churn is 1.1 percentage points above target (a 35% reduction needed from 3.1%). Retention is 4 percentage points behind (a 5% increase needed from 81%). Activation is 6 percentage points behind (a 9% increase needed from 64%). A gap may be given in percentage points or as a relative change from the user's value, as long as the figure is correct. All five are behind target.

PASS only if all of these hold:
1. Each of the five metrics is compared with the user's own target and marked behind, with correct arithmetic (LTV to CAC 2.25 against 3).
2. The NPS gap is given in points, not as a percentage, and NPS is not ranked against the percentage metrics as if they were the same unit.
3. The two customer quotes are kept word for word, and the reply does not treat the first quote's time saving as verified.
4. It gives no fit stage label or verdict (such as "strong fit", "emerging", "pre PMF", "you have product market fit", "you do not have product market fit") and no published benchmark or typical value for any metric.
5. It suggests what to check next for the metrics behind target, tied to the user's own data.

FAIL if any of these happen, whatever else the reply does well:
- It invents a fact or figure the user did not give: a named person or company, a customer, a competitor, a result, a statistic, a benchmark, a typical or industry value, a deadline or a money amount. Arithmetic on the user's own figures is allowed only when it is correct. A suggestion clearly marked as a suggestion, an example default labelled as one, a placeholder such as "[User to add: ...]", and naming which of its own reference notes it used (marked as something to confirm or test) are not invented facts. Restating what the user wrote in the request above is not invention.
- It recommends buying, adopting or switching to a named software product, tool or vendor. (Pointing the user to another plugin or skill by name for work outside this request is a hand off, not a software recommendation.)
- It names any real company or person as the user's client, prospect, buyer or customer.
- It is not plain English: hype or marketing words (for example "game changer", "supercharge", "unlock", "seamless", "robust"), exclamation marks, or jargon left unexplained for the reader named in the request.
- It uses a dash as punctuation: an em dash, an en dash, or a hyphen with a space on each side between words. Hyphens inside compound words, hyphens that start a list item and hyphens in table borders are fine.
