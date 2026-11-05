# Engagement Brief: Office of Acquisition Insights

> **Fictional customer.** The Office of Acquisition Insights (OAI) is an invented organization used to frame this portfolio project. All data comes from the public [USASpending.gov](https://www.usaspending.gov) API. No employer code, data, or internal references are used.

## 1. The problem

OAI is a small federal contracting office. Its analysts field questions from contracting officers and leadership such as:

- "Which vendors received the most DoD IT contract dollars in Oklahoma last fiscal year?"
- "How has VA cloud spending changed over the last five years?"
- "What is PSC DA01, and who are the top recipients under it at DHS?"

Today an analyst answers each one by hand on USASpending.gov: build an Advanced Search, export a CSV, pivot it in Excel, then paste numbers into an email. A simple question takes 30 to 90 minutes. The steps are hard to repeat, and two analysts often get different numbers for the same question because they made different filter choices: fiscal or calendar year, awarding or funding agency, lifetime award value or obligations in the year.

OAI wants a **trustworthy assistant** that answers in plain English, **shows its numbers**, states the **filters it used**, and **cites the underlying award records** so any answer can be checked against USASpending.gov.

## 2. Stakeholders

| Stakeholder | What they care about | How they judge success |
|---|---|---|
| **Analysts** (primary users, about 6) | Speed, and not being embarrassed by a wrong number | Answer in under 30s, with numbers they can check in under a minute |
| **Contracting officers** (consumers of answers) | Vendor landscape, competition, market research | Answers come with award IDs they can open |
| **OAI Director** (sponsor) | Analyst throughput, defensible numbers in briefings | Fewer "where did this number come from?" escalations |
| **IT / ISSO** (gatekeeper) | Data handling, authorization path, model access | Public data only, no PII stored, clear path to an authorized environment |

## 3. Discovery questions I would ask

**About the questions themselves**
1. What are the 20 questions you were asked most often last quarter? (These become the eval set.)
2. When someone says "last year," do they mean the fiscal year or the calendar year? Does it differ by audience?
3. Do you report **obligations** (money committed in a period) or **award value** (the lifetime ceiling or total)? Do leadership briefings ever mix the two?
4. "DoD IT spending": do you define IT by NAICS, by PSC, or by a list you maintain? Which PSC revision do you use?
5. Do you attribute spending by **awarding** agency, **funding** agency, or both?
6. Is "in Oklahoma" based on the recipient's address or the place of performance?

**About trust and workflow**
7. What happens today when two analysts disagree on a number? Who decides?
8. What does a citation need to look like for you to paste the answer into a briefing?
9. How fresh does the data need to be? Is a weekly refresh acceptable?
10. Which questions should the assistant **refuse** or hand back to a human?

**About the environment**
11. Where would this run eventually: a laptop, an agency cloud tenant, or a FedRAMP-authorized SaaS?
12. Which LLM endpoints are already approved (for example, Claude on AWS Bedrock in GovCloud, or Google Vertex)?
13. Is there an existing data platform (such as Databricks or Snowflake) this should feed into or read from?

### Working assumptions (until discovery confirms them)

| Question | Assumption used in this build |
|---|---|
| Fiscal or calendar year | **Fiscal year** (Oct 1 to Sep 30). The assistant asks when a question is ambiguous. |
| Money measure | **Obligations** (`federal_action_obligation`), attributed to the fiscal year of the action date |
| Agency | **Awarding** toptier agency |
| Location | **Place of performance** state |
| "IT" | NAICS 5415xx and 518210 in the starter scope, configurable in `config/scope.yaml` |

## 4. Scope

### In scope (v1)
- Prime **contract** awards (types A, B, C, D) from USASpending.gov
- 4 agencies (DoD, VA, DHS, GSA) × 5 fiscal years (FY2022 to FY2026), IT-focused NAICS by default. All of this is configurable.
- Questions about totals, top-N rankings, period-over-period changes, single awards, and NAICS/PSC code meanings
- A chat UI for analysts, with an inspectable "How I got this answer" trail
- An evaluation harness with a scorecard

### Out of scope (v1)
- Grants, loans, and other assistance awards; subawards; IDV vehicle ceilings
- **USPS**: it is exempt from the FAR and does not report most of its contracting to FPDS, so USASpending coverage is too thin to support trustworthy answers. I would raise this with the sponsor rather than quietly return low numbers.
- Predictions, forecasts, or "will vendor X win" questions
- Any analysis of **specific individuals** (for example, sole-proprietor recipients or contracting officer names)
- Authentication, multi-tenancy, and an authorized deployment (covered in "What I'd do next")

### Known data limitations to tell users about
- **DoD procurement data is published with a 90-day delay**, so the most recent quarter of DoD spending will look low.
- USASpending reflects what agencies report to FPDS. Late or corrected reports change historical numbers. Every answer is "as of" the last refresh date.
- Award descriptions are free text and are often truncated or cryptic.
- Agency names and NAICS/PSC codes change over time (for example, the 2022 NAICS revision and the PSC manual updates).

## 5. Success criteria

| # | Criterion | Target | How it's measured |
|---|---|---|---|
| S1 | Correctness on answerable questions | ≥ 90% | Eval harness checks numbers against DuckDB ground truth |
| S2 | Every numeric claim is cited | 100% | Eval checks for an award ID or USASpending link plus a filter statement |
| S3 | Asks for clarification when a question is ambiguous | ≥ 80% of ambiguous evals | Eval checks clarification behavior |
| S4 | Declines unanswerable or out-of-scope questions without inventing numbers | 100% | Eval checks that no dollar figure appears in the reply |
| S5 | Latency | p50 < 15s, p95 < 30s | Eval harness timing |
| S6 | Cost | < $0.05 per question (median) | Token usage × published price |
| S7 | Time to answer for an analyst | from 30 to 90 min down to < 2 min | Pilot measurement (the real engagement, not this repo) |

## 6. Delivery plan

| Phase | Deliverable | Exit criteria |
|---|---|---|
| 1 | Scaffold, this brief, architecture, ADRs | Reviewed by sponsor |
| 2 | Ingestion → transform → DuckDB | Idempotent load of the starter scope, tests green |
| 3 | Agent tools, runner, system prompt | Answers sample questions with citations |
| 4 | Streamlit UI | Demo-ready on a laptop screen |
| 5 | Evals and scorecard | 25+ questions, scorecard in the README |
| 6 | Docker, CI, deployment docs | One-command run, CI green, hosted demo |
