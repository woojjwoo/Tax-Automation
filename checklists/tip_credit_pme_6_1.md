# Quebec Tax Credit for Reporting of Tips (PME-6.1)

**Crédit d'impôt relatif à la déclaration des pourboires**
**Form:** CO-1029.8.33.13 (filed with CO-17)
**Legislation:** Taxation Act (Quebec), S.1029.8.33.13 et seq.
**Regulatory Authority:** Revenu Québec

---

## Overview

The **Tax Credit for the Reporting of Tips** is a **refundable** Quebec tax credit
available to employers in prescribed sectors (primarily restaurants and hotels) who
are required to report employee tip income. The credit offsets the employer's share
of payroll taxes attributable to reported tips.

**Why it matters for Giwa:** As a Montreal restaurant, Giwa is required to participate
in the tip reporting regime. This credit directly reduces the cost of employer payroll
contributions on declared tips — a material cash flow benefit.

---

## Eligibility Criteria

### Employer Requirements

- [ ] Giwa is a **prescribed employer** operating in a prescribed establishment
  (restaurant, bar, hotel — NAICS 7225 qualifies)
- [ ] Giwa holds a valid **registration with Revenu Québec** for the tip reporting regime
- [ ] Giwa uses a **certified SRM/MEV** to record sales and tips
- [ ] Giwa has **reported tip income** on employee RL-1 slips (Box S — Pourboires)
- [ ] Giwa has **remitted** all required source deductions on reported tips

### Employee Requirements (per employee)

- [ ] Employee works in a prescribed establishment
- [ ] Employee is in a **tipped position** (server, bartender, busser receiving tip-outs, etc.)
- [ ] Tips are **declared** by the employee or **attributed** by the employer
- [ ] Tip income is reported on the employee's RL-1 slip

---

## Eligible Payroll Contributions (Employer's Share on Tips)

The credit covers the **employer's portion** of the following contributions
calculated on **declared or attributed tip income**:

| Contribution | Rate (approximate, verify annually) |
|---|---|
| Quebec Pension Plan (QPP) — employer share | 6.40% (2025 base + QPP2) |
| Employment Insurance (EI) — employer share | 1.66 × employee rate |
| Quebec Parental Insurance Plan (QPIP) — employer | 0.692% |
| Health Services Fund (HSF) | 1.65%–4.26% (based on total payroll) |
| CNESST (workers' compensation) | Classification-specific rate |
| CNT (Labour standards — contribution) | 0.07% |
| Workforce Skills Development (1% law) | 1.0% if payroll > $2M |

**Note:** The credit is on contributions **attributable to tips only**, not total payroll.

---

## Calculation Methodology

### Step 1: Determine Total Declared/Attributed Tips per Employee

```
For each tipped employee:
  Total Tips = Direct Tips (declared by employee)
             + Controlled Tips (credit card tips allocated by employer)
             + Attributed Tips (deemed minimum if declaration < 8% of sales served)
```

- [ ] Extract tip data from SRM/MEV system (see `srm_mev_reconciliation.md`)
- [ ] Reconcile to payroll records (RL-1 Box S per employee)
- [ ] Identify any attributed tips (employer-deemed tips for under-reporting)

### Step 2: Calculate Employer Payroll Contributions on Tips

```
For each tipped employee:
  Eligible Amount = Sum of employer contributions on tip income:
    + QPP employer share on tips
    + EI employer premium on tips (1.4× or 1.66× employee premium on tips)
    + QPIP employer premium on tips
    + HSF contribution on tips
    + CNESST premium on tips
    + CNT contribution on tips
    + Workforce skills development (if applicable) on tips
```

- [ ] Calculate each component separately per employee
- [ ] Aggregate across all tipped employees for the fiscal year
- [ ] Verify calculations against payroll provider's year-end summary

### Step 3: Determine Credit Amount

```
Credit = Total eligible employer contributions on declared/attributed tips
       × Applicable percentage (currently 75% for qualifying employers)
```

**Important notes on the rate:**
- The credit rate has varied over the years — verify the rate for the current tax year
- Certain conditions may affect the applicable percentage
- The credit is **refundable** — it reduces tax payable and any excess is refunded

### Step 4: Prepare Form CO-1029.8.33.13

- [ ] Complete employee-by-employee schedule of tip income and employer contributions
- [ ] Calculate total credit claimed
- [ ] Attach to CO-17 filing
- [ ] Retain supporting documentation for 6 years

---

## Practical Calculation Example — Giwa Restaurant ($30K/Month Revenue)

**Giwa's actual profile:**

| Item | Amount |
|------|--------|
| Monthly revenue | $30,000 |
| Annual revenue | $360,000 |
| Number of tipped employees | 3 (2 servers + 1 bartender) |
| Total declared tips (all employees, annual) | $43,200 |
| Average tip per employee | $14,400 |
| Average tip rate (% of personal sales) | ~14.5% |

**Estimated employer payroll contributions on tips:**

| Contribution | Rate | Amount on $43,200 |
|---|---|---|
| QPP (employer) | ~6.40% | $2,765 |
| EI (employer) | ~2.21% | $955 |
| QPIP (employer) | ~0.692% | $299 |
| HSF | ~1.65% | $713 |
| CNESST | ~2.50% (illustrative) | $1,080 |
| CNT | ~0.07% | $30 |
| **Total eligible contributions** | | **$5,842** |

**Credit at 75%:** $5,842 × 75% = **$4,382**

> This is a **$4,382 refundable credit** — Giwa receives this even in a loss year.
> For a small restaurant near break-even, this is meaningful cash flow.
> Combined with the ~$15,800 non-capital loss carry-forward, Giwa's tax position
> is well-managed despite thin margins.

---

## SRM/MEV Integration for Tip Tracking

The SRM/MEV system is the **primary source of truth** for tip data:

### Data Flow

```
Customer Payment (POS)
    │
    ▼
SRM/MEV Records Transaction
    │
    ├─→ Credit Card Tips (automatically captured)
    │
    ├─→ Cash Tips (employee declaration forms — daily/per shift)
    │
    └─→ Attributed Tips (if declared < 8% of personal sales)
         │
         ▼
    Payroll System (tip income per employee per pay period)
         │
         ├─→ RL-1 Slip (Box S — Pourboires reçus)
         │
         └─→ T4 Slip (Box 14 — included in employment income)
              │
              ▼
    CO-17 / CO-1029.8.33.13 (Employer tip credit claim)
```

### Key Reconciliation Points

- [ ] SRM tip total = Payroll tip total (RL-1 Box S aggregate)
- [ ] Attributed tips are properly calculated for under-declaring employees
- [ ] Tip pool / tip-out allocations are documented and reconciled
- [ ] Credit card processing statements support credit card tip totals

---

## Tip Attribution Rules (8% Deemed Minimum)

If an employee's declared tips are **less than 8% of their personal sales**
(as recorded by the SRM), the employer must **attribute** the difference:

```
Attributed Tips = (Employee's Sales per SRM × 8%) - Declared Tips
```

**Important considerations:**
- Attribution applies **per pay period**, not annually
- Employer must remit source deductions on attributed tips
- Attributed tips are included in the PME-6.1 credit calculation
- Employee may dispute attribution via their personal tax return
- The 8% rate is the general default — verify current Revenu Québec guidance

---

## Documentation & Retention Requirements

For PME-6.1 audit defence, maintain:

- [ ] SRM/MEV transaction logs (daily, monthly, annual summaries)
- [ ] Employee tip declaration forms (daily or per-shift)
- [ ] Tip pool distribution records and policies
- [ ] Payroll register showing tip income per employee per period
- [ ] RL-1 slips with Box S completed for all tipped employees
- [ ] Calculation working papers for CO-1029.8.33.13
- [ ] Signed tip reporting policy acknowledged by all tipped employees
- [ ] SRM reconciliation binders (see `srm_mev_reconciliation.md`)

**Retention period:** Minimum 6 years from the end of the taxation year

---

## Common Pitfalls to Avoid

1. **Not claiming the credit at all** — Many smaller restaurants miss this entirely
2. **Under-reporting tips** — Triggers attribution AND potential penalties
3. **Inconsistent SRM data** — SRM tips must match payroll tips must match RL-1
4. **Missing tip declarations for cash tips** — System must capture daily declarations
5. **Incorrect payroll contribution rates** — Use current-year rates, not prior year
6. **Forgetting QPP2 (second additional QPP)** — Introduced 2024, adds to eligible base
7. **Not including CNESST** — Often overlooked in the credit calculation
8. **Tip pool documentation gaps** — Must support who received what and why

---

## Filing Checklist Summary

- [ ] SRM/MEV data extracted and reconciled for fiscal year
- [ ] All employee tip income reconciled (SRM → Payroll → RL-1)
- [ ] Tip attributions calculated for under-declaring employees
- [ ] Employer payroll contributions on tips calculated per component
- [ ] Credit amount calculated at applicable rate
- [ ] Form CO-1029.8.33.13 completed
- [ ] Form attached to CO-17 return
- [ ] Supporting documentation filed and retained
- [ ] Credit amount cross-referenced to CO-17 tax payable calculation

---

*This document is based on the Taxation Act (Quebec) S.1029.8.33.13 and
Revenu Québec's administrative guidance. Rates and thresholds should be
verified against current-year publications. The illustrative calculation
uses approximate rates — actual rates must be confirmed for the filing year.*
