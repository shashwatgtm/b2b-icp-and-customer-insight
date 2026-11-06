---
type: llm
---

The user's request, word for word:
<request>
Review our ICP against what is actually happening and tell me what should change.

Our ICP: mid sized logistics companies (200 to 2,000 employees) in India that run their own fleet, with a head of operations who owns route planning.

Today we have 40 customers: 22 are logistics companies in that size band, 11 are retail chains with their own delivery fleets, and 7 are D2C brands that use third party couriers.

Last quarter against our targets: average contract value 18 lakh (target 25 lakh), sales cycle 95 days (target 70 days), win rate 22% (target 30%).

Last quarter we won 5 deals (3 retail chains, 2 logistics companies) and lost 5 (3 D2C brands, lost on price; 2 logistics companies, lost to an incumbent).
</request>

The user gave: the ICP (mid sized logistics companies, 200 to 2,000 employees, India, own fleet, a head of operations who owns route planning); 40 customers (22 logistics in the size band, 11 retail chains with own fleets, 7 D2C brands using third party couriers); metrics against targets (contract value 18 lakh vs 25 lakh; sales cycle 95 vs 70 days; win rate 22% vs 30%); 5 wins (3 retail chains, 2 logistics) and 5 losses (3 D2C on price, 2 logistics to an incumbent).

Correct arithmetic, any of which is acceptable when the base is clear: contract value is 7 lakh short, a 39% increase needed from 18 lakh or 28% below target; the sales cycle is 25 days long, a 26% reduction needed from 95 days or 36% above target; win rate is 8 percentage points short, a 36% increase needed from 22%.

PASS only if all of these hold:
1. It compares the customer groups with the ICP part by part: the 22 logistics customers match; the retail chains match on own fleet but not on industry; the D2C brands that use third party couriers do not match the own fleet part.
2. Every gap figure it gives is correct arithmetic on the user's figures, as above; it does not compare NPS or other metrics the user did not give.
3. Proposed ICP changes are stated as hypotheses or trials, each with a check on the user's own data (for example contract value or win rate of retail chains against logistics companies) that would confirm or disprove it; nothing is declared proven from 5 wins and 5 losses.
4. It keeps the loss reasons the user gave (price, incumbent) and does not invent other reasons or causes as facts.
5. It does not use industry benchmarks or typical values for contract value, cycle length or win rate.

FAIL if any of these happen, whatever else the reply does well:
- It invents a fact or figure the user did not give: a named person or company, a customer, a competitor, a result, a statistic, a benchmark, a typical or industry value, a deadline or a money amount. Arithmetic on the user's own figures is allowed only when it is correct. A suggestion clearly marked as a suggestion, an example default labelled as one, a placeholder such as "[User to add: ...]", and naming which of its own reference notes it used (marked as something to confirm or test) are not invented facts. Restating what the user wrote in the request above is not invention.
- It recommends buying, adopting or switching to a named software product, tool or vendor. (Pointing the user to another plugin or skill by name for work outside this request is a hand off, not a software recommendation.)
- It names any real company or person as the user's client, prospect, buyer or customer.
- It is not plain English: hype or marketing words (for example "game changer", "supercharge", "unlock", "seamless", "robust"), exclamation marks, or jargon left unexplained for the reader named in the request.
- It uses a dash as punctuation: an em dash, an en dash, or a hyphen with a space on each side between words. Hyphens inside compound words, hyphens that start a list item and hyphens in table borders are fine.
