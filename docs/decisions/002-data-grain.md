# ADR 002: Transaction-level grain, with obligations attributed by fiscal year

- **Status:** Accepted
- **Date:** 2026-11-05

## Context
The question "how has VA cloud spending changed over 3 years?" sounds simple, but USASpending exposes two different dollar figures:

1. **Award Amount** on `spending_by_award`: the award's **lifetime** obligated total. A 5-year contract signed in FY2022 shows its full value whenever it matches a time filter, so summing award amounts by year double counts across years and assigns money to the wrong years.
2. **Transaction Amount** on `spending_by_transaction`: the obligation (`federal_action_obligation`) of a **single action** (the base award or a modification) on a specific `Action Date`.

Analysts briefing leadership almost always mean "money obligated in FY X," which is (2). Mixing the two is the most common reason two analysts get different numbers (see the engagement brief, discovery question 3).

There is a catch: transaction results don't include NAICS, PSC, or place of performance. Award results do.

## Decision
- The **fact table is `transactions`**: one row per contract action, with `obligation` and `fiscal_year` taken from `Action Date`.
- **`awards` is a dimension** holding NAICS, PSC, place-of-performance state, recipient, and description, joined on `generated_internal_id`.
- Both are pulled with the **same filters** (agency, award types A to D, NAICS/PSC scope, monthly time windows), so every transaction in scope has its award row.
- Every aggregate the agent reports is `SUM(transactions.obligation)`, labeled "obligations." Lifetime award value appears only in `get_award_details`, and is labeled that way.
- IDVs are excluded so we don't count the vehicle and the orders placed against it.

## Consequences
- Fiscal-year totals match how OAI briefs (pending confirmation in discovery).
- Totals can include **negative transactions** (deobligations). That's correct, and the system prompt tells the agent to say so when it matters.
- Twice as many API calls as an award-only pull. That's acceptable for a batch bootstrap.
- Award attributes such as NAICS are taken from the award's current record. If a modification reclassified an award, every year uses the latest code. This is documented as a known limitation.
- **Verify on first live run:** reconcile one agency-year total against USASpending's own `spending_over_time` for the same filters. A gap of more than 1% blocks the release.
