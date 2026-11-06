---
type: llm
---

The user's request, word for word:
<request>
I'm interviewing a happy customer next week for a case study we will publish on our website. Give me the questions to ask.
</request>

The user gave only: a case study interview with a happy customer next week, to be published. No product, customer, results or figures were given.

PASS only if all of these hold:
1. It gives a usable set of case study questions (situation before, decision, rollout, results in the customer's own words, a quote).
2. It does not invent the customer's results, figures or quotes, and leaves product and customer details for the user to fill in.

FAIL if any of these happen, whatever else the reply does well:
- It invents a fact or figure the user did not give: a named person or company, a customer, a competitor, a result, a statistic, a benchmark, a typical or industry value, a deadline or a money amount. Arithmetic on the user's own figures is allowed only when it is correct. A suggestion clearly marked as a suggestion, an example default labelled as one, a placeholder such as "[User to add: ...]", and naming which of its own reference notes it used (marked as something to confirm or test) are not invented facts. Restating what the user wrote in the request above is not invention.
- It recommends buying, adopting or switching to a named software product, tool or vendor. (Pointing the user to another plugin or skill by name for work outside this request is a hand off, not a software recommendation.)
- It names any real company or person as the user's client, prospect, buyer or customer.
- It is not plain English: hype or marketing words (for example "game changer", "supercharge", "unlock", "seamless", "robust"), exclamation marks, or jargon left unexplained for the reader named in the request.
- It uses a dash as punctuation: an em dash, an en dash, or a hyphen with a space on each side between words. Hyphens inside compound words, hyphens that start a list item and hyphens in table borders are fine.
