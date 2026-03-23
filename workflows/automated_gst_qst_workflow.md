# Automated GST/QST Workflow — Giwa Restaurant

**Objective:** End-to-end automation from source documents to filed GST/QST returns,
T2/CO-17 preparation, and payroll compliance using Canadian-compliant software.

---

## Technology Stack

| Layer | Tool | Role |
|-------|------|------|
| Cloud Accounting | **QuickBooks Online (Canada)** or **Sage Business Cloud** | GL, financial statements, GST/QST tracking |
| Document Capture | **Dext (formerly Receipt Bank)** | AP invoice capture, OCR, GST/QST extraction |
| Payroll | **Wagepoint** or **Ceridian Powerpay** | Payroll, QPP/EI/QPIP/CNESST, RL-1/T4 |
| POS System | **Lightspeed Restaurant** (Montreal-based) | SRM/MEV-certified, sales recording |
| Tax Filing | **TaxCycle** or **Profile (Wolters Kluwer)** | T2, CO-17, GST/QST return preparation |
| Bank Feeds | **Direct bank feeds** via Plaid/Flinks | Automated bank reconciliation |
| Integration | **Zapier** or **Make (Integromat)** | Connecting systems where native integrations lack |

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    REVENUE PIPELINE                          │
│                                                              │
│  POS (Lightspeed)  ──→  SRM/MEV  ──→  Revenu Québec        │
│       │                    │                                 │
│       │                    └──→ Tip Data ──→ Payroll System  │
│       │                                                      │
│       └──→ Daily Sales Journal ──→ Cloud Accounting (QBO)   │
│                                          │                   │
│                                          ▼                   │
│                                   Revenue Accounts           │
│                                   GST Collected              │
│                                   QST Collected              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    EXPENSE PIPELINE                           │
│                                                              │
│  Supplier Invoices ──→ Dext (OCR/Capture) ──→ QBO           │
│       │                      │                               │
│       │                      ├──→ GST # Validated            │
│       │                      ├──→ QST # Validated            │
│       │                      └──→ Expense Categorized        │
│       │                                   │                  │
│  Credit Card Feeds ──→ Bank Rules ──→ QBO ▼                 │
│  Bank Feeds ─────────→ Bank Rules ──→ Reconciliation        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    PAYROLL PIPELINE                           │
│                                                              │
│  Time Tracking ──→ Payroll System (Wagepoint/Ceridian)      │
│  Tip Data (SRM) ──→     │                                    │
│                          ├──→ QPP / QPP2 calculated          │
│                          ├──→ EI calculated                  │
│                          ├──→ QPIP calculated                │
│                          ├──→ Federal/QC tax withheld        │
│                          ├──→ CNESST premium calculated      │
│                          │                                   │
│                          ▼                                   │
│                    Payroll Journal ──→ QBO                   │
│                    T4/RL-1 Slips (year-end)                  │
│                    PME-6.1 Data (tip credit)                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    TAX FILING PIPELINE                        │
│                                                              │
│  QBO Trial Balance ──→ TaxCycle / Profile                   │
│       │                      │                               │
│       │                      ├──→ T2 Federal Return          │
│       │                      ├──→ CO-17 Quebec Return        │
│       │                      ├──→ GST Return (RC7200)        │
│       │                      ├──→ QST Return (VDZ-471)       │
│       │                      └──→ CO-1029.8.33.13 (PME-6.1) │
│       │                                                      │
│       └──→ GIFI Mapping (automated in TaxCycle)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Workflow Steps

### W1: Daily Revenue Capture (Automated)

**Trigger:** End-of-day POS close (Lightspeed Z-report)

| Step | Action | System | Frequency |
|------|--------|--------|-----------|
| 1.1 | POS records all sales through SRM/MEV | Lightspeed → SRM | Real-time |
| 1.2 | Daily sales summary syncs to QBO | Lightspeed → QBO | Daily (auto) |
| 1.3 | Revenue coded to correct accounts | QBO mapping rules | Automatic |
| 1.4 | GST/QST automatically split from gross sales | QBO tax codes | Automatic |
| 1.5 | Tip data captured and stored | SRM → Payroll | Daily |
| 1.6 | Third-party delivery reconciliation | Uber Eats/DoorDash → QBO | Weekly |

**QBO Tax Code Configuration for Restaurant:**

| Tax Code | GST | QST | Use Case |
|----------|-----|-----|----------|
| GQ (5%+9.975%) | 5% | 9.975% | Standard dine-in/takeout meals |
| GQ (5%+9.975%) | 5% | 9.975% | Alcoholic beverages |
| GQ (5%+9.975%) | 5% | 9.975% | Non-alcoholic beverages |
| Exempt | 0% | 0% | Basic groceries (if sold separately) |
| Zero-rated | 0% | 0% | Exported catering (rare) |

### W2: Expense Capture via Dext (Automated)

**Trigger:** Receipt/invoice received

| Step | Action | System | Frequency |
|------|--------|--------|-----------|
| 2.1 | Photograph/email receipt or invoice to Dext | Dext mobile/email | As incurred |
| 2.2 | Dext OCR extracts: vendor, date, amount, GST#, QST# | Dext AI engine | Automatic |
| 2.3 | Dext validates GST# against CRA registry | Dext validation | Automatic |
| 2.4 | Dext validates QST# against RQ registry | Dext validation | Automatic |
| 2.5 | Expense categorized per Dext supplier rules | Dext rules | Automatic |
| 2.6 | Published to QBO as bill or expense | Dext → QBO sync | Automatic |
| 2.7 | GST ITC and QST ITR amounts captured | QBO tax codes | Automatic |

**Dext Configuration for Restaurant Expenses:**

| Supplier Category | GL Account | Tax Code | ITC/ITR Eligible |
|---|---|---|---|
| Food suppliers (Sysco, GFS) | 5010 COGS-Food | GQ | Yes (100%) |
| Beverage suppliers (SAQ, distributors) | 5020 COGS-Beverage | GQ | Yes (100%) |
| Kitchen supplies | 5030 Supplies | GQ | Yes (100%) |
| Utilities (Hydro-QC, Énergir) | 6200 Utilities | GQ | Yes (100%) |
| Rent | 6100 Rent | GQ or Exempt | Depends on lease |
| Insurance | 6300 Insurance | Exempt | No |
| Meals & entertainment (business) | 6500 M&E | GQ | 50% ITC/ITR |
| Professional fees (CPA, legal) | 6400 Professional | GQ | Yes (100%) |
| Marketing / advertising | 6600 Marketing | GQ | Yes (100%) |

**Key Dext Rules:**
- [ ] Reject invoices without valid GST# (9 digits, validated against CRA)
- [ ] Reject invoices without valid QST# (10 digits starting with 1, validated against RQ)
- [ ] Flag invoices over $150 missing GST/QST registration numbers
- [ ] Auto-apply 50% ITC/ITR restriction for meals & entertainment vendors
- [ ] Route invoices over $5,000 for manager approval before publishing

### W3: Payroll Processing (Semi-Monthly)

**Trigger:** Pay period end

| Step | Action | System | Frequency |
|------|--------|--------|-----------|
| 3.1 | Import hours from time-tracking system | Time system → Payroll | Per pay period |
| 3.2 | Import tip data from SRM/POS | SRM → Payroll | Per pay period |
| 3.3 | Calculate gross pay (wages + tips) | Payroll system | Automatic |
| 3.4 | Calculate and withhold: Federal tax, QC tax, QPP/QPP2, EI, QPIP | Payroll system | Automatic |
| 3.5 | Calculate employer premiums: QPP, EI, QPIP, HSF, CNESST, CNT | Payroll system | Automatic |
| 3.6 | Process direct deposits | Payroll → Bank | Pay date |
| 3.7 | Remit source deductions to CRA (PD7A) | Payroll system | Monthly (by 15th) |
| 3.8 | Remit source deductions to RQ (TPZ-1015.R.14) | Payroll system | Monthly (by 15th) |
| 3.9 | Sync payroll journal to QBO | Payroll → QBO | Per pay period |
| 3.10 | Track tip data for PME-6.1 credit | Payroll system | Cumulative |

**Tip Attribution Automation:**

```
IF employee_declared_tips < (employee_sales_per_SRM × 0.08) THEN
    attributed_tips = (employee_sales_per_SRM × 0.08) - employee_declared_tips
    Add attributed_tips to employee gross income
    Calculate and remit source deductions on attributed_tips
    Flag for PME-6.1 credit calculation
END IF
```

### W4: Monthly GST/QST Reconciliation (Automated Reports)

**Trigger:** Month-end close

| Step | Action | System | Frequency |
|------|--------|--------|-----------|
| 4.1 | Run QBO GST/QST summary report | QBO | Monthly |
| 4.2 | Compare QBO GST collected to SRM GST total | QBO vs. SRM | Monthly |
| 4.3 | Compare QBO QST collected to SRM QST total | QBO vs. SRM | Monthly |
| 4.4 | Reconcile ITCs claimed to Dext-captured invoices | QBO + Dext | Monthly |
| 4.5 | Reconcile ITRs claimed to Dext-captured invoices | QBO + Dext | Monthly |
| 4.6 | Generate variance report — investigate items > $100 | QBO | Monthly |
| 4.7 | Prepare GST/QST return draft if filing period ends | TaxCycle | Quarterly/Annual |

### W5: Quarterly/Annual GST-QST Return Filing

**Trigger:** Filing period end

| Step | Action | System |
|------|--------|--------|
| 5.1 | Export QBO trial balance and tax summary to TaxCycle | QBO → TaxCycle |
| 5.2 | Populate GST return (RC7200) — Line 101 (sales), 105 (GST collected), 108 (ITCs) | TaxCycle |
| 5.3 | Populate QST return (VDZ-471) — Line 201 (sales), 205 (QST collected), 208 (ITRs) | TaxCycle |
| 5.4 | Cross-reference SRM data to return figures | Manual review |
| 5.5 | File GST return electronically (NETFILE / GST NETFILE) | TaxCycle → CRA |
| 5.6 | File QST return electronically (Clic Revenu) | TaxCycle → RQ |
| 5.7 | Process GST/QST payment or refund | Bank / CRA / RQ |

### W6: Year-End T2/CO-17 Preparation

**Trigger:** Fiscal year-end + all monthly closes completed

| Step | Action | System |
|------|--------|--------|
| 6.1 | Complete all monthly reconciliations (W4) | QBO |
| 6.2 | Post year-end adjusting entries | QBO |
| 6.3 | Generate GIFI-mapped trial balance | QBO → TaxCycle |
| 6.4 | Import payroll summaries for T4/RL-1 preparation | Payroll → TaxCycle |
| 6.5 | Calculate PME-6.1 tip credit (CO-1029.8.33.13) | Payroll data + TaxCycle |
| 6.6 | Complete T2 schedules (S1, S8, S50, S100, S125, S200) | TaxCycle |
| 6.7 | Complete CO-17 with Quebec adjustments | TaxCycle |
| 6.8 | Attach CO-1029.8.33.13 to CO-17 | TaxCycle |
| 6.9 | E-file T2 to CRA | TaxCycle → CRA |
| 6.10 | E-file CO-17 to Revenu Québec | TaxCycle → RQ |

---

## Automation Rules & Error Handling

### Bank Rules in QBO

| Pattern | Action |
|---------|--------|
| "LIGHTSPEED" or POS merchant | Auto-categorize as Sales Clearing |
| "SYSCO" or "GFS" or food suppliers | Auto-categorize as COGS-Food + GQ tax |
| "SAQ" | Auto-categorize as COGS-Beverage + GQ tax |
| "HYDRO-QUEBEC" | Auto-categorize as Utilities + GQ tax |
| Payroll provider name | Auto-categorize as Payroll Clearing |
| "UBER EATS" / "DOORDASH" / "SKIP" | Auto-categorize as Delivery Platform Revenue |

### Exception Handling

| Exception | Automated Response |
|---|---|
| Dext cannot read GST/QST number | Flag for manual entry — hold from publishing |
| SRM-to-QBO daily variance > 1% | Email alert to bookkeeper + preparer |
| ITC claimed on exempt supply | QBO tax code validation — block posting |
| Employee tips < 8% of sales | Payroll system auto-calculates attribution |
| Bank feed transaction unmatched > 7 days | Weekly exception report to accountant |
| GST/QST return variance vs. SRM > $500 | Block filing — require partner review |

---

## Monthly Close Calendar — Giwa Restaurant

| Day | Task | Owner |
|-----|------|-------|
| 1st | Prior month bank feeds finalized | Bookkeeper |
| 1st–3rd | Dext inbox cleared — all invoices published | Bookkeeper |
| 3rd | SRM/MEV monthly summary downloaded | Bookkeeper |
| 5th | Bank reconciliation completed | Bookkeeper |
| 5th | SRM-to-QBO revenue reconciliation | Bookkeeper |
| 7th | Payroll journal reconciliation | Bookkeeper |
| 10th | GST/QST monthly reconciliation report | Bookkeeper |
| 10th | Exception items reviewed and resolved | CPA (Preparer) |
| 15th | Source deduction remittance verified | Payroll system (auto) |
| 15th | Monthly close finalized — period locked | CPA (Preparer) |
| Quarterly | GST/QST return prepared and filed | CPA (Preparer) |
| Quarterly | Partner review of quarterly tax position | Senior Partner |

---

*This workflow is designed for Canadian-compliant software operating under CRA and
Revenu Québec requirements. Software versions and integrations should be verified
against current vendor documentation.*
