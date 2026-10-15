# Fit scoring method

## Fit, not engagement
This model scores who a lead or account is (fit with the ICP): size, segment, region, the systems they run, the situation they are in. It does not score what they did (opens, clicks, visits, event attendance). Engagement scoring for event leads belongs to event-follow-up-engine in the events plugin, which asks the user to set every weight and threshold itself. The two can sit side by side: fit says whether the account is worth pursuing; engagement says whether now is the moment.

## Choosing criteria
- Start from the user's ICP: each must have becomes a candidate critical criterion; each nice to have becomes important or nice to have; each disqualifier becomes a value worth 0 (or a rule that removes the lead before scoring, which the user decides).
- Three to six criteria are easier to keep honest than fifteen; this is a suggestion, not a rule.
- Each criterion must be something the team can find out before or in the first call (from the account's own pages, the CRM, the lead form). A criterion nobody can fill makes every lead incomplete.
- Name criteria in the vertical's words (references/sector-notes.md): monthly shipments for a shipping platform, endpoints or audit scope for security, engagement size for services.

## Listing values
- List values best first. The script grades them evenly from the full weight down to 0 (a value list of three gives full, about half, 0).
- Where values are names, not a scale (regions, industries), set "graded": false so each scores the full weight, or give explicit points per value.
- Values must be exact and exclusive: "100 to 499", not "about 100"; "Yes" and "No", not "Yes" and "Probably".

## Weights
- The user's weights win. Without them, the script uses example defaults by importance (critical 25, important 15, nice to have 10) and says so on every line. These are starting examples, not a benchmark and not an industry standard.
- A criterion with no importance is scored as nice to have and labelled so; ask the user to set it.

## Tiers
A from 80% of the maximum, B from 60%, C from 40%, D below, rounded up (example default bands; the user's own bands go in as "tier_percents" and the script labels them as the user's). What each tier triggers (who calls, how fast) is the user's own rule; the skill writes "[User to set: action for tier A]" unless the user gave one. No response time is presented as a norm.

## Validating the model on the user's own deals
1. Score the last closed won and closed lost deals with the model (as many as the user can export).
2. Compare: where do the won deals land, and where do the lost deals land? Count each tier. Where won deals land low or lost deals land high, which criterion misled?
3. Change one weight or value at a time and re-score; keep a change log.
4. Re-check each quarter or after an ICP change (icp-review in this plugin).
The skill never claims a model is accurate before this check is done on the user's data.

## Rolling out in a CRM (general steps; the user's admin decides the build)
One field per criterion with the exact values; a formula or workflow that adds the points; a tier field from the bands; a report of tier against outcome. The skill never writes to a CRM.

## Red flags to review by hand even with a high score
A disqualifier the model does not hold (the user's own list); data filled by guesswork; a lead that matches on size only. These are prompts to look, not scores.
