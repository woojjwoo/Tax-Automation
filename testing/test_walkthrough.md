# Testing Walkthrough — Giwa Restaurant ($30K/Month)

**Purpose:** Step-by-step guide to validate the entire tax compliance workflow
using sample data before going live with real Giwa data.

---

## Pre-Test Setup Checklist

- [ ] Review `giwa_test_profile.md` — confirm all assumptions match Giwa's reality
- [ ] Adjust hourly rates to current Quebec minimums (tipped: verify current rate)
- [ ] Confirm actual employee count and positions
- [ ] Confirm actual revenue split (food vs. beverage vs. other)
- [ ] Get actual GST and QST registration numbers
- [ ] Get actual SRM/MEV certificate number

---

## Test 1: SRM/MEV-to-POS Revenue Reconciliation

**Data file:** `sample_data/january_srm_daily_sales.csv`

### What you are validating:
Every dollar that goes through the POS must appear in the SRM. No gaps, no overrides.

### Steps:

1. **Sum the SRM daily gross sales for January:**
   ```
   Expected: ~$24,000 (January is a slow month — 0.80 seasonality factor)
   ```

2. **Compare to the POS Z-tape total:**
   - In Lightspeed back-office, pull January sales summary
   - The two numbers must match within $50 or 0.5%

3. **Check the void/refund ratios:**
   ```
   Total voids: count them from the CSV
   Total transactions: sum transaction_count column
   Void ratio = total voids / total transactions
   Target: < 2%
   ```

4. **Verify GST/QST math on each line:**
   ```
   For each day:
     GST = net_sales × 5%      (tolerance: ±$0.05 rounding)
     QST = net_sales × 9.975%  (tolerance: ±$0.05 rounding)
   ```

5. **Verify tip percentages by day:**
   ```
   For each day:
     tip_rate = total_tips / net_sales
     Expected range: 12%–18%
     Flag if any day < 8% (audit risk)
   ```

### Pass criteria:
- [ ] SRM gross sales = POS gross sales (±$50)
- [ ] All daily GST/QST calculations are mathematically correct (±$0.05)
- [ ] Void ratio < 2%
- [ ] No days with tip rate < 8%
- [ ] No unexplained gaps in dates (restaurant was open)

---

## Test 2: Expense Capture (Dext → QBO)

**Data file:** `sample_data/january_expenses_dext.csv`

### What you are validating:
Dext correctly captures invoices, validates tax numbers, categorizes expenses,
and applies ITC/ITR restrictions.

### Steps:

1. **Verify GST number validation:**
   - Every line with a valid 9-digit GST# → ITC eligible
   - Lines with "N/A", "Exempt", or foreign vendors → ITC NOT eligible
   - Hydro-Québec: GST-exempt (QC Crown corp) — confirm no ITC claimed
   - Meta/Facebook: Foreign supplier — no GST/QST charged, no ITC/ITR

2. **Verify QST number validation:**
   - Every line with valid QST# starting with "1" → ITR eligible
   - Insurance: Exempt supply — no QST, no ITR
   - Hydro-Québec: Confirm exemption treatment

3. **Verify 50% M&E restriction:**
   ```
   Business meal (MEAL-0129): $95.00 before tax
   GST ITC eligible: $4.75 × 50% = $2.38
   QST ITR eligible: $9.48 × 50% = $4.74
   ```

4. **Calculate total ITCs and ITRs for January:**
   ```
   Sum all GST amounts where ITC eligible = Yes (minus 50% M&E restriction)
   Sum all QST amounts where ITR eligible = Yes (minus 50% M&E restriction)

   Cross-reference to QBO GST/QST reports
   ```

5. **Verify GL account coding:**
   - Food suppliers → 5010 (COGS-Food)
   - SAQ → 5020 (COGS-Beverage)
   - Rent → 6100
   - Confirm no miscategorizations

### Pass criteria:
- [ ] All valid GST#s produce ITC claims
- [ ] All valid QST#s produce ITR claims
- [ ] Exempt supplies (insurance, Hydro) have $0 ITC/ITR
- [ ] M&E restricted to 50%
- [ ] Foreign suppliers (Meta) have no ITC/ITR
- [ ] All expenses coded to correct GL accounts
- [ ] Total expenses reconcile to bank/credit card statements

---

## Test 3: Payroll & Tip Processing

**Data file:** `sample_data/january_payroll.csv`

### What you are validating:
Tips flow correctly from SRM → payroll, source deductions are accurate,
and PME-6.1 data is accumulating.

### Steps:

1. **Reconcile SRM tips to payroll tips:**
   ```
   SRM total tips (January): sum total_tips from SRM CSV
   Payroll total tips (January): sum total_tips from payroll CSV (tipped employees only)
   These must match.
   ```

2. **Verify tip attribution (8% test):**
   ```
   For each tipped employee per pay period:
     Employee sales = their portion of SRM sales
     Minimum tips = employee_sales × 8%
     If declared tips < minimum → attribution triggered

   For Giwa at $24K/month:
     Server A: ~$9,000 sales, ~$1,440 tips = 16% → OK
     Server B: ~$9,000 sales, ~$1,350 tips = 15% → OK
     Bartender: ~$6,750 sales, ~$810 tips = 12% → OK
     No attribution needed (all > 8%)
   ```

3. **Verify source deduction calculations:**
   ```
   For each employee, verify:
     QPP = (gross_pay - $3,500 annual exemption prorated) × 6.40%
     EI  = gross_pay × employee rate
     QPIP = gross_pay × 0.494%
     Federal tax = per CRA tax tables (TD1 basic personal amount)
     QC tax = per RQ tax tables (TP-1015.3-V basic personal amount)
   ```

4. **Verify employer premium calculations:**
   ```
   QPP employer = QPP employee (matched)
   EI employer = EI employee × 1.4
   QPIP employer = gross_pay × 0.692%
   HSF = gross_pay × 1.65% (payroll < $1M)
   CNESST = gross_pay × classification rate
   CNT = gross_pay × 0.07%
   ```

5. **Isolate employer premiums ON TIPS ONLY (for PME-6.1):**
   ```
   For each tipped employee, calculate employer premiums
   on the tip_income portion only:

   Server A January tips: $1,975
   Server B January tips: $1,855
   Bartender January tips: $1,180
   Total January tips: $5,010

   Employer premiums on $5,010:
     QPP: $5,010 × 6.40% = $320.64
     EI:  $5,010 × 2.21% = $110.72
     QPIP: $5,010 × 0.692% = $34.67
     HSF: $5,010 × 1.65% = $82.67
     CNESST: $5,010 × 2.50% = $125.25
     CNT: $5,010 × 0.07% = $3.51
     Total: $677.46

   Monthly PME-6.1 accrual: $677.46 × 75% = $508.10
   Annualized estimate: $508.10 × 12 = ~$6,097
   ```
   > Note: Actual annual will vary with seasonality and employee hours.

### Pass criteria:
- [ ] SRM tip total = Payroll tip total for January
- [ ] No tip attribution triggered (all employees > 8%)
- [ ] Source deductions within $2 of CRA/RQ payroll tables
- [ ] Employer premiums correctly calculated
- [ ] PME-6.1 tip data isolated and accumulating correctly

---

## Test 4: Monthly GST/QST Reconciliation

### What you are validating:
The three data sources (SRM, QBO revenue, QBO expenses) produce a correct
GST/QST return.

### Steps:

1. **Build the January GST reconciliation:**
   ```
   GST COLLECTED (Line 105):
     SRM total GST collected: sum gst_collected from SRM CSV
     QBO GST collected account (2310): should match SRM

   GST ITCs (Line 108):
     Dext/QBO total ITCs: sum from expenses CSV
     Less: 50% M&E restriction
     Less: Exempt/foreign supplier exclusions

   NET GST = GST Collected - ITCs
   ```

2. **Build the January QST reconciliation:**
   ```
   QST COLLECTED (Line 205):
     SRM total QST collected: sum qst_collected from SRM CSV
     QBO QST collected account (2320): should match SRM

   QST ITRs (Line 208):
     Dext/QBO total ITRs: sum from expenses CSV
     Less: 50% M&E restriction
     Less: Exempt/foreign supplier exclusions

   NET QST = QST Collected - ITRs
   ```

3. **Three-way match:**
   ```
   SRM GST collected = QBO GL 2310 = GST return Line 105
   SRM QST collected = QBO GL 2320 = QST return Line 205

   All three must agree within $5.
   ```

### Pass criteria:
- [ ] Three-way GST match (SRM = QBO = Return) within $5
- [ ] Three-way QST match (SRM = QBO = Return) within $5
- [ ] ITC/ITR restrictions properly applied
- [ ] Net GST/QST payable is reasonable (~$2,084/month per test profile)

---

## Test 5: Year-End T2/CO-17 Assembly

### What you are validating:
12 months of data aggregate correctly into tax return figures.

### Steps (use January × 12 with seasonality as proxy):

1. **Revenue verification:**
   ```
   Annual revenue per SRM: ~$360,000
   Annual revenue per QBO: must match SRM
   T2 Schedule 125 (GIFI 8000): must match QBO
   CO-17 revenue line: must match T2
   ```

2. **COGS verification:**
   ```
   Food costs: ~$115,200 (32% of revenue — within 28-35% norm ✓)
   Beverage costs: ~$22,500 (alcohol + non-alc)
   Total COGS: ~$137,700
   COGS ratio: 38.25% (reasonable for full-service restaurant)
   ```

3. **CCA calculation:**
   ```
   Per test profile capital assets:
   Class 8: $37,000 (equipment + furniture + signage) × 20% × 50% = $3,700
   Class 10: $4,000 (scooter) × 30% × 50% = $600
   Class 12: $3,000 (smallwares) × 100% = $3,000
   Class 13: $15,000 (leaseholds) ÷ lease term = ~$1,500
   Class 50: $5,000 (POS) × 55% × 50% = $1,375
   Total CCA: ~$10,175
   ```

4. **Tax payable calculation:**
   ```
   Net income before tax: (~$14,124) LOSS
   + accounting amortization: $8,000
   - CCA: ($10,175)
   + non-deductible (50% M&E): ~$500
   = Taxable income: (~$15,799) LOSS

   Federal tax: $0 (loss year)
   QC tax: $0 (loss year)
   PME-6.1 credit: ~$4,382 (refundable — received even in loss year)
   Non-capital loss carry-forward: $15,799
   ```

5. **PME-6.1 final calculation:**
   ```
   12-month tip total (3 employees): ~$43,200
   Employer premiums on tips: ~$5,842
   Credit at 75%: ~$4,382
   Filed on CO-1029.8.33.13 with CO-17
   ```

### Pass criteria:
- [ ] Annual SRM = Annual QBO = T2/CO-17 revenue
- [ ] Food cost ratio between 28–35%
- [ ] CCA calculations match asset register and prescribed rates
- [ ] Loss carry-forward correctly computed
- [ ] PME-6.1 credit correctly calculated and attached to CO-17
- [ ] T4/RL-1 tip income (Box S) matches SRM + payroll data

---

## Test 6: End-to-End Smoke Test (Live Data — One Month)

**When to run:** After all tests above pass with sample data.

### Steps:

1. **Set up QBO** with Giwa's actual chart of accounts
2. **Connect Lightspeed** POS and verify SRM/MEV daily sync
3. **Configure Dext** with Giwa's actual supplier rules
4. **Process one real pay period** through Wagepoint/Ceridian
5. **Run the full monthly reconciliation** (Test 4 steps with real data)
6. **Compare results to prior-period** actual returns (if available)
7. **Identify and document variances**
8. **Adjust automation rules** based on real-world exceptions

### Go-live criteria:
- [ ] One full month processed with zero unresolved variances
- [ ] SRM-to-QBO sync confirmed daily for 30 consecutive days
- [ ] Dext processing 100% of invoices without manual intervention
- [ ] Payroll tip reconciliation matches SRM for all pay periods
- [ ] Client (Giwa owner) trained on Dext mobile receipt capture
- [ ] Client trained on tip declaration process for cash tips

---

## Quick Reference: Expected January Numbers

| Metric | Expected | Tolerance |
|--------|----------|-----------|
| Gross revenue | ~$24,000 | ±$2,000 (seasonality) |
| GST collected | ~$1,165 | Calculated from net sales |
| QST collected | ~$2,325 | Calculated from net sales |
| Total tips (3 employees) | ~$5,010 | ±$500 |
| Total COGS | ~$9,580 | 38–40% of revenue |
| Net GST payable | ~$545 | After ITCs |
| Net QST payable | ~$1,085 | After ITRs |
| Total payroll (gross) | ~$15,081 | Based on test profile hours |
| PME-6.1 monthly accrual | ~$508 | 75% of employer premiums on tips |

---

## Troubleshooting Common Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| SRM total ≠ POS total | Training mode transactions in SRM | Exclude training transactions; verify POS day-cutoff time |
| Tips seem too low | Cash tip declarations not captured | Implement daily tip declaration forms; review SRM vs. payroll |
| Dext rejecting invoices | Missing or invalid GST#/QST# | Verify vendor registration; some small vendors may be under $30K threshold |
| GST/QST variance > $50 | Timing difference (accrual vs. cash) | Check if revenue recognition timing matches SRM recording date |
| Payroll deductions off | Using prior-year contribution rates | Update to current-year QPP/EI/QPIP rates (change every January 1) |
| ITC claimed on exempt supply | Dext miscategorization | Add supplier to exempt list in Dext rules; retrain OCR |
| Hydro-Québec showing GST | QBO tax code error | Hydro-QC is QST-exempt Crown corp — use Exempt tax code |

---

*Run Tests 1–5 with sample data first. Only proceed to Test 6 (live data) when
all sample tests pass. Document all variances and resolutions in a test log.*
