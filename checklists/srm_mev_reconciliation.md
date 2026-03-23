# SRM/MEV Reconciliation Checklist — Giwa Restaurant

**Module d'enregistrement des ventes (MEV) / Sales Recording Module (SRM)**
**Regulatory Authority:** Revenu Québec
**Legislation:** Act respecting the Québec sales tax (AQST), Division VI.0.1

---

## Background

Since 2010, all Quebec restaurants (and other prescribed establishments) must use a
**Sales Recording Module (SRM/MEV)** certified by Revenu Québec. The SRM records every
transaction, calculates GST/QST, and produces a digitally signed receipt (bill) that
customers can verify via Revenu Québec's MEVweb portal.

**Non-compliance penalties:**
- $300–$5,000 per day for operating without a certified SRM
- Additional penalties for tampering, zapping, or phantomware
- Potential criminal prosecution under AQST S.350.62

---

## Pre-Reconciliation Setup

### Hardware & Certification

- [ ] Confirm SRM unit is certified by Revenu Québec (check MEV certificate number)
- [ ] Verify SRM firmware is current — check Revenu Québec's certified devices list
- [ ] Confirm SRM certificate has not expired (certificates are time-limited)
- [ ] Verify SRM is connected to the POS system and producing signed receipts
- [ ] Confirm backup SRM procedures are in place for hardware failure
- [ ] Document SRM serial number(s) and location(s) within the establishment

### POS System Integration

- [ ] Verify POS system is on Revenu Québec's list of compatible systems
- [ ] Confirm every revenue stream flows through the POS → SRM pipeline:
  - Dine-in sales
  - Takeout / counter sales
  - Bar / lounge sales
  - Catering invoices
  - Third-party delivery platform orders (Uber Eats, DoorDash, Skip)
  - Gift card sales and redemptions
  - Event / private dining bookings
- [ ] Verify no manual overrides or voids bypass the SRM recording

---

## Monthly Reconciliation Procedures

### Step 1: Extract SRM Data

- [ ] Download monthly SRM transaction summary from MEV portal or POS back-office
- [ ] Obtain the following SRM totals:
  - Gross sales (before tax)
  - GST collected
  - QST collected
  - Net sales (after discounts, before tax)
  - Number of transactions
  - Number of voids / refunds
  - Tip amounts recorded

### Step 2: Reconcile SRM to POS

- [ ] Compare SRM gross sales total to POS daily Z-tape summaries
- [ ] Investigate and document any variances exceeding $50 or 0.5% of daily sales
- [ ] Common variance causes:
  - Training mode transactions (should not flow to SRM)
  - Manual voids not processed through SRM
  - Time-zone or day-cutoff differences between POS and SRM
  - Third-party delivery platform timing differences
- [ ] Reconcile SRM void/refund count to POS void/refund log
- [ ] Verify manager authorization exists for all voids over $25

### Step 3: Reconcile SRM to General Ledger

- [ ] Compare SRM net sales to GL revenue accounts (by category if possible):
  - Food revenue
  - Beverage revenue (alcoholic)
  - Beverage revenue (non-alcoholic)
  - Other revenue (merchandise, events)
- [ ] Reconcile SRM GST collected to GL GST payable account
- [ ] Reconcile SRM QST collected to GL QST payable account
- [ ] Document adjustments for:
  - Gift card breakage revenue (not subject to GST/QST until redemption)
  - Loyalty program point accruals
  - Staff meals (taxable benefit vs. deductible expense)

### Step 4: Reconcile SRM to GST/QST Returns

- [ ] Compare SRM total GST collected to GST return (line 105) for the period
- [ ] Compare SRM total QST collected to QST return (line 205) for the period
- [ ] Identify and explain any differences:
  - Timing differences (SRM daily vs. return period)
  - Adjustments for bad debts (S.231 ETA for GST, S.444 AQST for QST)
  - Prior period corrections
- [ ] Maintain reconciliation working paper for each filing period

### Step 5: Tip Reconciliation via SRM

- [ ] Extract total tips recorded by SRM (credit card tips + declared cash tips)
- [ ] Compare SRM tip data to payroll tip income reported
- [ ] Verify allocated tips per employee match SRM attribution
- [ ] Cross-reference to PME-6.1 tip credit calculation (see `tip_credit_pme_6_1.md`)
- [ ] Identify employees whose declared tips fall below 8% of individual sales
  (Revenu Québec's deemed minimum — "attribution" may apply)
- [ ] Document tip pooling arrangements and tip-out percentages

---

## Year-End SRM Reconciliation (For T2/CO-17 Filing)

### Annual Totals Verification

- [ ] Aggregate 12 months of monthly SRM reconciliations
- [ ] Verify annual SRM gross sales = sum of monthly SRM gross sales
- [ ] Reconcile annual SRM revenue to T2/CO-17 reported revenue (Schedule 125 GIFI)
- [ ] Prepare variance analysis if SRM revenue differs from reported revenue
- [ ] Document legitimate reasons for any variance:
  - Accounting adjustments (ASPE revenue recognition timing)
  - Intercompany eliminations
  - Non-SRM revenue streams (e.g., management fees)

### Revenu Québec Reporting

- [ ] Ensure SRM annual summary data is available for CO-17 filing
- [ ] Prepare supporting schedules linking SRM data to CO-17 revenue line
- [ ] Retain SRM data files for minimum 6 years (per AQST record-keeping requirements)
- [ ] Confirm SRM data backup is stored securely (cloud + local)

### Audit Preparedness

- [ ] Maintain monthly reconciliation binder (digital or physical)
- [ ] Document all void/refund policies and manager approval thresholds
- [ ] Keep a log of SRM hardware incidents (downtime, replacements, repairs)
- [ ] Prepare a narrative memo explaining the reconciliation process for auditors
- [ ] Ensure all staff are trained on proper SRM/POS transaction procedures
- [ ] Document any communication with Revenu Québec regarding SRM compliance

---

## Red Flags — What Triggers a Revenu Québec SRM Audit

Be aware of patterns that may trigger scrutiny:

1. **High void/refund ratios** — Industry norm: < 2% of transactions
2. **SRM downtime gaps** — Extended periods with no recorded transactions
3. **Revenue inconsistency** — SRM data vs. reported revenue divergence
4. **Cash-to-card ratio anomalies** — Unusual percentage of cash vs. credit
5. **Tip reporting below deemed thresholds** — Below 8% consistently
6. **Third-party data mismatch** — Uber Eats/DoorDash reported to CRA vs. SRM
7. **Supplier ratio analysis** — COGS-to-revenue ratios outside norms

---

## SRM Reconciliation Sign-Off

| Month | Prepared By | Reviewed By | Date | Variances Noted |
|-------|-------------|-------------|------|-----------------|
| Jan   |             |             |      |                 |
| Feb   |             |             |      |                 |
| Mar   |             |             |      |                 |
| Apr   |             |             |      |                 |
| May   |             |             |      |                 |
| Jun   |             |             |      |                 |
| Jul   |             |             |      |                 |
| Aug   |             |             |      |                 |
| Sep   |             |             |      |                 |
| Oct   |             |             |      |                 |
| Nov   |             |             |      |                 |
| Dec   |             |             |      |                 |

---

*Based on Revenu Québec's mandatory SRM requirements under AQST Division VI.0.1.
Refer to Revenu Québec's current SRM technical documentation for certified device lists
and software specifications.*
