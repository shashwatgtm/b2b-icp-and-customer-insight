# B2B ICP and Customer Insight

ICP and customer insight skills for B2B teams, built by Shashwat Ghosh, Helix GTM Consulting. It reviews and revises an ICP you already have; it does not build account lists.

- **icp-review**: today's customers against your ICP, metric gaps by script with labelled example bands, and proposed ICP changes from wins, losses and market changes, each a hypothesis with its CRM check.
- **customer-interviews**: interview guides that test your own hypotheses, and synthesis across many interviews with each item counted once per interview.
- **lead-scoring-model**: a fit scoring model with points and tiers, your weights or labelled example defaults, and lead scores where a missing value is incomplete, never 0.
- **buying-role-hypotheses**: champion, signer and evaluator hypotheses with validation questions, by role.
- **pmf-check**: product market fit metrics compared only with your own targets; no benchmark and no stage label.

Version 1.0.0. More plugins by Helix GTM Consulting: https://tools.gtmhelix.com/plugins/

## Install

```bash
claude plugin marketplace add shashwatgtm/b2b-icp-and-customer-insight
claude plugin install b2b-icp-and-customer-insight@b2b-icp-and-customer-insight
```

## Quick start

"Here is our ICP and last quarter's wins and losses. How should our ICP change?"

"Synthesise these interview notes against our hypotheses."

"Build a fit scoring model from our ICP and score these accounts."

"Who champions and who signs for a product like ours?"

"How far are our churn, NPS and retention from our own targets?"

## Privacy

This plugin sends no data to Helix GTM Consulting and runs no server. It keeps no account, no log and no copy of your work. The Python scripts read only what you give them, use no network and write no files. One hook, in Claude Code only (hooks/delivery_check.py, a Stop hook), checks that a skill's final reply is the text its claim ledger checked; it reads the hook input and the session transcript on your computer, writes one small counter file in a folder of your own in the system temporary folder, and sends nothing. The plugin's own README gives the details.

## License

MIT. See [LICENSE](LICENSE).
