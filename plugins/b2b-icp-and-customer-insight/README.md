# B2B ICP and Customer Insight

Five skills for B2B founders, product marketers, RevOps and demand generation leads who need to decide who their best customers really are, what those customers say, and how their ideal customer profile (ICP) should change. You give them your ICP, customers, deals, interview notes or metrics; you get a reviewed ICP, interview guides and synthesis, a fit scoring model, buying role hypotheses or a metrics check against your own targets. Every skill works from your own customers, deals, interviews and figures, keeps every example number labelled as a default you can change, and states each proposed change as a hypothesis with the check that would confirm it. It reviews and revises an ICP you already have; it does not build account lists.

## Skills

**icp-review** compares today's customers with your ICP part by part (segment, size, buyer, problem, place), computes the metric gaps by script (contract value, sales cycle, win rate, churn, NPS), and turns recent wins, losses and market changes into proposed ICP changes with the CRM check for each, ending in a marked up draft of the revised ICP.
Example prompt: "Here is our ICP, our current customers and last quarter's wins and losses. Are we selling to the right customers, and how should the ICP change?"

**customer-interviews** writes interview guides that test your own hypotheses without leading the interviewee, and synthesises many interviews with each item counted once per interview, ties named, quotes word for word and interviewees by role.
Example prompt: "Synthesise these eight interview notes against our three hypotheses."

**lead-scoring-model** builds a lead or account fit scoring model with points and tiers A to D, using your weights or example default weights that are labelled as starting examples, and scores leads on it; a lead missing a value is reported incomplete, never scored as 0. Engagement scoring for event leads stays with the events plugin, which asks you to set every weight.
Example prompt: "Build a fit scoring model from these four criteria and score these six accounts."

**buying-role-hypotheses** sets product level hypotheses for who champions, who signs and who evaluates, each with a validation question and what would disprove it, by role and never by name.
Example prompt: "We sell alert triage to security teams at mid sized banks. Who is our champion and who signs?"

**pmf-check** compares your product market fit metrics (churn, NPS, LTV to CAC, retention, activation and your own measures) only with your own targets, ranks the dimensions furthest behind and uses no published range, benchmark or stage label.
Example prompt: "Here are our churn, NPS and retention figures and our board targets. How far are we from them?"

## Install

In Claude Code:

```
/plugin marketplace add shashwatgtm/b2b-icp-and-customer-insight
/plugin install b2b-icp-and-customer-insight@b2b-icp-and-customer-insight
```

## What it runs

The skills run inside Claude. Six small Python scripts (standard library only), each run on realistic, empty, wrong type and very large inputs before release, do the exact parts: icp_gap.py (metric gaps and bands), fit_count.py (how many customers can fit several ICP parts at once), interview_tally.py (counts once per interview and the hypothesis tally), lead_score.py (weights, points, tiers, a tier reading and lead scores), role_check.py (a text check on role drafts) and pmf_score.py (metrics against your own targets). They read only the JSON or text files Claude gives them, use no network and write no files. When web tools are available, a skill may open your own company's public pages to read your product in your words, with link and date. Nothing is published, sent or written to a CRM.

## What changed in 1.0.6

- Tested by behaviour: an eval suite in evals/ runs real prompts with and without the plugin (see "How this plugin is tested").
- Fixes from that testing: customer-interviews never asks a question that presumes a cost ("What, if anything, did that take from the team?") and keeps each hypothesis in its own words and numbers; icp-review never derives a figure you did not give from an assumed definition (such as deals decided from a win rate).
- The explicit "icon" field is removed from plugin.json; the icon in .claude-plugin/ is still picked up by default.

## What changed in 1.0.5

- Skill descriptions say in plain words which decision each skill helps with, what you give it and what you get back.
- lead_score.py: a weight with decimals (12.5) now gives the best value the full weight, never more or less, and tier starts are shown in hundredths when points have decimals; a tier that has no scores at a very small maximum says so.
- interview_tally.py refuses one hypothesis given two verdicts in the same interview, and counts "H1" and "h1" as one hypothesis when no list of ids is given.
- icp_gap.py, pmf_score.py and lead_score.py refuse a value too large or too small to compare with a clear message instead of stopping; pmf_score.py says why LTV to CAC was not scored when CAC is 0.
- role_check.py checks the same things with short, plain text patterns (no look ahead or look behind).

## What changed in 1.0.1

Removed the optional reply checker, its steps in each skill and its end of turn check; the other scripts and all other text are unchanged.

## Examples

The worked examples inside the skills use hypothetical, unnamed companies and hypothetical figures only; no real company or person is described.

## How this plugin is tested
evals/ holds 10 cases in the `claude plugin eval` layout: for each of the 5 skills, one realistic B2B request that should use the skill and one near miss that should not. Every case has a judged rubric (what the skill promises, plus no invented facts or figures, no software recommendations, no client names, plain English and no dashes used as punctuation), a regex check for dashes, and a check that the skill did or did not run. In the final run (6 November 2026, 2 runs per case with and without the plugin, Sonnet as agent and judge, no shell tools), the mean case score was 0.75 with the plugin and 0.36 without it; on the 5 cases the skills are built for it was 0.90 with and 0.15 without. Each skill ran on all 10 of its trigger runs and on none of the 20 near miss runs. Runs where every graded check passed: 10 of 20 with the plugin, 3 of 20 without. The cases were run by a headless runner that applies the same scoring to these files, because `claude plugin eval` could not sign in its child runs on the test machine.

## Privacy

This plugin sends no data to Helix GTM Consulting and runs no server. It keeps no account, no log and no copy of your work; any file Claude writes for you goes only to your own working folder, nowhere else. Interviewees and contacts are shown by role, not name, unless you ask. What you type into Claude is handled under your own Claude account terms.

## Security

To report a security problem, email shashwat@gtmhelix.com with the subject "Security report: b2b-icp-and-customer-insight". Please do not open a public issue for it.

## License

MIT. See LICENSE.
