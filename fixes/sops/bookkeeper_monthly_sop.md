# BLOCKER 8 FIX: Bookkeeper Monthly Standard Operating Procedures

**Purpose:** Step-by-step instructions any bookkeeper can follow, even if new
to Quebec restaurant accounting. Designed for turnover resilience.

---

## Monthly Close Calendar (Print and Post)

| Day | Task | Time | Instructions |
|-----|------|------|-------------|
| 1st | Check bank feeds are connected | 2 min | Section A below |
| 1st–3rd | Clear Dext inbox | 15 min | Section B below |
| 3rd | Download SRM monthly summary | 5 min | Section C below |
| 5th | Bank reconciliation | 30 min | Section D below |
| 5th | SRM-to-QBO revenue reconciliation | 20 min | Section E below |
| 7th | Payroll journal reconciliation | 15 min | Section F below |
| 10th | GST/QST monthly reconciliation | 20 min | Section G below |
| 10th | Send exception report to CPA | 5 min | Section H below |
| 15th | Verify source deduction remittance | 5 min | Section I below |
| 15th | Lock period (after CPA review) | 2 min | Section J below |

**Total monthly time: ~2 hours**

---

## Section A: Check Bank Feeds (Day 1)

1. Log into QBO → Banking tab
2. For EACH connected bank account, verify:
   - Last transaction date is within 2 days of today
   - Status shows "Connected" (green)
3. **If feed is disconnected:**
   - Click "Update" or "Reconnect"
   - Re-enter bank login credentials
   - If still failing: note it in exception report (Section H)
   - Temporary fix: download CSV from bank website, import manually

---

## Section B: Clear Dext Inbox (Days 1–3)

1. Log into Dext → Inbox
2. Review each item:
   - **Green checkmark** = auto-processed, verify category is correct
   - **Yellow warning** = needs attention (usually missing GST#/QST#)
   - **Red flag** = cannot process (blurry photo, unreadable)
3. For yellow warnings:
   - Check if vendor is GST/QST exempt (insurance, Hydro-QC)
   - If exempt: manually set tax code to "E" (exempt)
   - If registered vendor: find GST#/QST# on original invoice, enter manually
4. For red flags:
   - Ask owner for original receipt or a clearer photo
   - If lost: check if vendor can provide duplicate invoice
5. **Publish all cleared items to QBO**
6. Target: inbox should be empty (0 items) by day 3

---

## Section C: Download SRM Monthly Summary (Day 3)

1. Log into Lightspeed back-office OR Revenu Québec MEVweb portal
2. Select the prior month date range
3. Download the monthly summary report (CSV or PDF)
4. Save to: `[Year]/[Month]/SRM_monthly_summary_[YYYY-MM].csv`
5. Note these totals (you'll need them in Section E):
   - Gross sales: $__________
   - Net sales: $__________
   - GST collected: $__________
   - QST collected: $__________
   - Total tips: $__________
   - Total voids: $__________
   - Total refunds: $__________

---

## Section D: Bank Reconciliation (Day 5)

1. QBO → Banking → select first bank account
2. Match or categorize all downloaded transactions
3. **Matching rules:**
   - "LIGHTSPEED" or POS name → Sales Clearing
   - "SYSCO" / "GFS" → COGS-Food (5010) + tax code GQ
   - "SAQ" → COGS-Beverage (5020) + tax code GQ
   - "UBER EATS" / "DOORDASH" / "SKIP" → Delivery Revenue (4050/4060/4070)
   - Payroll provider name → Payroll Clearing
4. **For unmatched items:** investigate before categorizing. If unsure, flag in exception report.
5. When done: click "Reconcile" and match to bank statement balance
6. **Reconciled = statement balance matches QBO balance to $0.00**
7. Repeat for ALL bank accounts and credit cards

---

## Section E: SRM-to-QBO Revenue Reconciliation (Day 5)

1. Open QBO → Reports → Profit & Loss by Month (prior month)
2. Note total revenue from QBO: $__________
3. Compare to SRM net sales from Section C: $__________
4. Calculate variance: QBO revenue - SRM net sales = $__________

**Acceptable variance: ±$50 or ±0.5%, whichever is greater**

5. If variance exceeds threshold:
   - Check if any days are missing from QBO (sync failure)
   - Check if delivery platform revenue is included
   - Check for duplicate entries (void + re-ring)
   - Document the variance and add to exception report (Section H)

6. Also verify:
   - QBO GST collected (GL 2310) vs. SRM GST: $__________ vs. $__________
   - QBO QST collected (GL 2320) vs. SRM QST: $__________ vs. $__________

---

## Section F: Payroll Journal Reconciliation (Day 7)

1. Run payroll summary report from Wagepoint/Ceridian for the month
2. Compare to QBO payroll expense accounts:
   - Wages & salaries: $__________ (payroll) vs. $__________ (QBO)
   - Employer CPP/QPP: $__________ vs. $__________
   - Employer EI: $__________ vs. $__________
   - Employer QPIP: $__________ vs. $__________
3. All should match exactly (payroll journal auto-posts)
4. If mismatch: check if payroll sync ran for all pay periods

---

## Section G: GST/QST Monthly Reconciliation (Day 10)

1. QBO → Reports → "Tax Summary" or "Sales Tax Liability"
2. Note:
   - GST collected: $__________
   - GST ITCs: $__________
   - Net GST: $__________
   - QST collected: $__________
   - QST ITRs: $__________
   - Net QST: $__________
3. Cross-reference GST/QST collected to SRM data (Section E)
4. Cross-reference ITCs/ITRs to Dext published expenses
5. **Three numbers must agree: SRM tax = QBO tax = Return tax**

---

## Section H: Exception Report (Day 10)

Email to CPA with subject: "Giwa — [Month] Exceptions"

Include:
- [ ] Revenue variance (SRM vs. QBO): amount and explanation
- [ ] Unmatched bank transactions (list with amounts)
- [ ] Dext items that could not be processed (vendor, amount, reason)
- [ ] Bank feed disconnections (dates, accounts, status)
- [ ] Any unusual items (large voids, refunds, write-offs)

---

## Section I: Source Deduction Verification (Day 15)

1. Confirm payroll system shows "Remitted" status for prior month
2. CRA remittance (PD7A): due by 15th → status: __________
3. RQ remittance (TPZ-1015.R.14): due by 15th → status: __________
4. **If not remitted: ESCALATE TO CPA IMMEDIATELY**
   (Late remittance = penalties + director liability)

---

## Section J: Lock Period (Day 15)

1. Confirm CPA has reviewed exception report and approved close
2. QBO → Settings → Company → Advanced → Close the books
3. Set closing date to last day of prior month
4. Set password (provided by CPA)
5. Period is now locked — no further changes without CPA password

---

## Emergency Contacts

| Who | When to Contact | How |
|-----|----------------|-----|
| CPA (Preparer) | Variances > $50, unmatched items, payroll issues | Email + Slack |
| Senior Partner | Filing deadlines, audit notices, director liability | Phone |
| Lightspeed Support | POS/SRM integration issues | 1-866-932-1801 |
| Wagepoint Support | Payroll processing errors | In-app chat |
| Dext Support | Document capture failures | In-app chat |
| QBO Support | Bank feed issues, software errors | 1-888-829-8589 |

---

*This SOP is designed for a bookkeeper working on Giwa Restaurant's
$30K/month file. If Giwa's operations change significantly (new location,
major revenue increase, new delivery platforms), update this document.*
