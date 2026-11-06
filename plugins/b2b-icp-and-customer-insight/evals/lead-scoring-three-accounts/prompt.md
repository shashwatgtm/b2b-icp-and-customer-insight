---
description: "A team gives three criteria with importance and three accounts, one with a missing value and one with a value not on the list."
tags: [trigger, lead-scoring-model]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

Build a fit scoring model from our ICP and score these three accounts.

Criteria:
- Industry (critical): logistics best, then retail, then other.
- Company size (important): 500 to 2,000 employees best, then 200 to 499, then under 200.
- Own delivery fleet (nice to have): yes is better than no.

Accounts:
- Account 1: logistics, 500 to 2,000 employees, own fleet yes.
- Account 2: retail, 200 to 499 employees, own fleet not known.
- Account 3: manufacturing, 500 to 2,000 employees, own fleet no.
