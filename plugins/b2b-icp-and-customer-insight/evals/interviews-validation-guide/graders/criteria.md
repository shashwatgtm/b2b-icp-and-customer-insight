---
type: llm
---

The user's request, word for word:
<request>
Write a customer interview guide for validation interviews with heads of finance at mid sized manufacturing companies. We sell a reconciliation automation product. The people we will interview are prospects, not customers.

Our hypotheses:
1. Their month end close takes more than a week because of manual reconciliations.
2. They would switch tools only if the change needs no new headcount.
3. The CFO, not the head of finance, signs for tools like ours.
</request>

The user gave: validation interviews; heads of finance at mid sized manufacturing companies; the interviewees are prospects, not customers; three hypotheses (month end close takes more than a week because of manual reconciliations; they would switch only if no new headcount is needed; the CFO, not the head of finance, signs for tools like this).

PASS only if all of these hold:
1. The guide has a clear flow: an opening, context questions, core questions, probes and a close.
2. Each of the three hypotheses is tested by at least one question, and the guide shows which question tests which hypothesis.
3. Questions do not lead or presume the answer (for example "How painful is your week long close?" or "Wouldn't automation help?" are leading) and do not pitch the product.
4. It includes at least one question that could produce evidence against a hypothesis.
5. It treats the interviewees as prospects: no questions that assume they already use the product.

FAIL if any of these happen, whatever else the reply does well:
- It invents a fact or figure the user did not give: a named person or company, a customer, a competitor, a result, a statistic, a benchmark, a typical or industry value, a deadline or a money amount. Arithmetic on the user's own figures is allowed only when it is correct. A suggestion clearly marked as a suggestion, an example default labelled as one, a placeholder such as "[User to add: ...]", and naming which of its own reference notes it used (marked as something to confirm or test) are not invented facts. Restating what the user wrote in the request above is not invention.
- It recommends buying, adopting or switching to a named software product, tool or vendor. (Pointing the user to another plugin or skill by name for work outside this request is a hand off, not a software recommendation.)
- It names any real company or person as the user's client, prospect, buyer or customer.
- It is not plain English: hype or marketing words (for example "game changer", "supercharge", "unlock", "seamless", "robust"), exclamation marks, or jargon left unexplained for the reader named in the request.
- It uses a dash as punctuation: an em dash, an en dash, or a hyphen with a space on each side between words. Hyphens inside compound words, hyphens that start a list item and hyphens in table borders are fine.
