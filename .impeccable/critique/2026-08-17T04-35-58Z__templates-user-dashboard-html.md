---
target: user dashboard
total_score: 23
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-08-17T04-35-58Z
slug: templates-user-dashboard-html
---
# User Dashboard Design Critique

## Design Health Score

| # | Heuristic | Score | Key issue |
|---|---|---:|---|
| 1 | Visibility of system status | 2 | No credible freshness, comparison period, target, or page-level status |
| 2 | Match system / real world | 2.5 | Familiar terminology, but metrics do not connect to operational consequences |
| 3 | User control and freedom | 3 | Useful filters, but limited saved views, comparison, sharing, and direct drill-down |
| 4 | Consistency and standards | 3 | Cohesive styling, but unlike information receives identical card treatment |
| 5 | Error prevention | 2.5 | Controlled filters, but data-quality failures such as Unknown are not actionable |
| 6 | Recognition rather than recall | 2.5 | Labels are visible, but users must remember benchmarks and infer significance |
| 7 | Flexibility and efficiency | 2 | No saved views, compare mode, quick segments, or evident export/share workflow |
| 8 | Aesthetic and minimalist design | 2 | Clean shell, but zero-heavy tables and decorative motion consume attention |
| 9 | Error recovery | 2 | Empty/error states provide limited diagnosis and recovery |
| 10 | Help and documentation | 1.5 | No definitions, calculation tooltips, source provenance, or freshness details |
| **Total** | | **23/40** | **Acceptable; substantial product-design improvement needed** |

## Design Specificity Verdict

The page is visually competent but category-interchangeable. Navy navigation, blue/cyan gradients, glass cards, Font Awesome icon tiles, and uppercase labels could belong to almost any HR analytics portal. It does not yet express LAKSHYA as an apprenticeship and evaluation operating system.

The deterministic scan found one warning: the overused Inter font in `templates/user_dashboard.html:10`. This is real but strategically minor compared with the information architecture. Browser evidence found five tables containing 423 body rows, a 1,299px-wide branch matrix, nested scrolling, and delayed scroll-triggered reveals.

## Overall Impression

As a reporting page: **7/10**. As a modern operational dashboard: **5.8/10**. The user's “why not Excel or Power BI?” concern is valid. The page mostly presents consolidated pivots inside polished cards. It reports what exists, but rarely explains what changed, what matters, why it happened, or what the user should do next.

The largest opportunity is to turn it into an **apprentice-health command center**: status, delta, risk, explanation, and action first; detailed tables second.

## What’s Working

- The visual system is clean and consistent, with readable desktop spacing and familiar plant/batch terminology.
- The first row provides quick access to gender, plant headcount, and attrition lenses.
- Centralized filters and student/evaluation drill-down create a genuine advantage over a static exported workbook.

## Priority Issues

### [P1] No decision layer

**Why it matters:** The first viewport cannot answer “Are we on track?” KPI values have no prior-period delta, target, health state, or recommended response.

**Fix:** Create an executive status band for total trainees, active/on-track batches, evaluation completion, attrition versus target, overdue evaluations, and data freshness. Every KPI needs context and a drill-down.

**Suggested command:** `$impeccable shape`

### [P1] No exception or action surface

**Why it matters:** Panapakkam attrition at 3.2%, 324 Unknown branch records, and overdue evaluations are buried among normal values. Users must manually discover risk.

**Fix:** Add a “Needs attention” queue with severity, affected count, owner, explanation, and direct actions such as “Review students” or “Resolve missing branch.”

**Suggested command:** `$impeccable bolder`

### [P1] Spreadsheet-like matrices dominate

**Why it matters:** The branch matrix is 1,299px wide, dominated by zeros, and horizontally scrolls. It recreates the Excel experience instead of improving it.

**Fix:** Replace it with ranked horizontal bars or a focused heatmap; suppress zero-only categories; separate Unknown into a data-quality alert. Keep “View underlying table” and export as secondary evidence.

**Suggested command:** `$impeccable distill`

### [P2] Weak narrative and hierarchy

**Why it matters:** Three equal-weight first-row cards make gender composition as visually important as attrition risk. Users do not know where to look first.

**Fix:** Recompose the page as Overview → Needs attention → Progress and drivers → Cohorts → Student records. Give the primary risk or progress story dominant space.

**Suggested command:** `$impeccable layout`

### [P2] Decorative motion delays scanning

**Why it matters:** Lower dashboard content took roughly 1.5 seconds to become fully legible after scrolling. Infinite aurora movement and card lifts do not communicate state.

**Fix:** Remove scroll-reveal delays and continuous ambient motion. Keep only short feedback transitions on filters, drill-downs, and state changes.

**Suggested command:** `$impeccable animate`

## Persona Red Flags

**Alex — busy plant or HR leader:** Cannot get a 30-second answer to “where must I intervene?” Alex sees totals and pivots but lacks targets, prioritized exceptions, and one-click access to affected cohorts.

**Sam — analyst/coordinator:** Useful filters and detailed tables are present, but definitions, source freshness, data-quality workflows, saved views, comparisons, and shareable filtered URLs are missing. “Unknown 324” is displayed as a fact rather than a repair workflow.

## Minor Observations

- The total of 369 is stranded inside the gender donut instead of serving as a primary KPI.
- The donut consumes about one-third of the first viewport for a near-even split with little urgency.
- Attrition repeats mostly 0.0% rows at the same weight as the 3.2% exception.
- The large filter strip could hold active chips, comparison period, refresh status, export, and share.
- Browser evidence found one visible unnamed button and one visible native select without a reliable accessible name.
- “Live” is not credible without a source and “updated at” timestamp.

## Questions to Consider

- If a number changes tomorrow, which decision should change with it?
- Which three conditions should wake a plant manager up, and why are they not first?
- Is “Unknown = 324” a distribution fact or the largest operational failure on the page?
- What can a user do here in one click that they cannot do in a pivot table?
- Should leadership see gender composition first, or evaluation completion and cohort risk?
