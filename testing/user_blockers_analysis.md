# User Blockers Analysis — Giwa Restaurant ($30K/Month)

**Question:** What prevents the restaurant owner, staff, and bookkeeper from
actually using this compliance system day-to-day?

---

## Severity Legend

| Level | Meaning |
|-------|---------|
| **CRITICAL** | Blocks the entire workflow; causes penalties or legal exposure |
| **HIGH** | Major friction; users will abandon the process without intervention |
| **MEDIUM** | Causes delays or data gaps; manageable with training |
| **LOW** | Annoyance; workaround exists |

---

## BLOCKER 1: Cash Tip Declaration (CRITICAL)

**Who it blocks:** Servers, bartender (3 tipped employees)
**What happens:** Staff must declare cash tips daily or per shift. If they don't,
the SRM records credit card tips automatically but cash tips are missing.

**Why it's a blocker:**
- Servers are busy — no natural pause to fill out a tip form
- No enforcement mechanism exists in the current workflow
- If declared tips < 8% of personal sales, the employer MUST attribute the difference
  (more payroll tax cost to Giwa, friction with employees)
- Revenu Québec uses SRM data to audit tip declarations — gaps are visible

**Impact if not addressed:**
- Inaccurate RL-1 Box S (tip income)
- PME-6.1 credit calculated on wrong base
- Potential RQ audit trigger

**Remediation:**
```
Option A: POS-based tip declaration
  → Configure Lightspeed to prompt cash tip entry at employee clock-out
  → Tips captured in POS → SRM automatically
  → No separate paper form needed

Option B: Daily tip sheet (paper fallback)
  → Printed form at POS station
  → Manager collects at end of shift
  → Entered into payroll weekly

Recommended: Option A — eliminates the manual step entirely
```

---

## BLOCKER 2: Receipt Capture Discipline (CRITICAL)

**Who it blocks:** Owner, kitchen manager (whoever handles purchases)
**What happens:** Every expense invoice/receipt must be photographed and sent to Dext.
A busy restaurant owner buying produce at 6 AM is not thinking about Dext.

**Why it's a blocker:**
- No receipt = no ITC/ITR claim = Giwa overpays GST/QST
- At $11,475/month in COGS alone, missing receipts could cost $800–$1,700/month
  in lost ITCs/ITRs
- Owner is a chef, not an accountant — workflow feels like extra work

**Impact if not addressed:**
- Lost ITCs: up to $574/month ($6,888/year)
- Lost ITRs: up to $1,145/month ($13,740/year)
- Total potential loss: **$20,628/year** — more than the restaurant's net income

**Remediation:**
```
1. Dext "Fetch" feature
   → Connect supplier email accounts (Sysco, SAQ, Bell, Hydro)
   → Dext auto-fetches emailed invoices — no human action needed
   → Covers ~70% of expenses by dollar value

2. Credit card auto-capture
   → Connect restaurant credit card to Dext
   → Transactions auto-matched; receipt photo only needed for verification
   → Reduces manual effort to ~5 receipts/week

3. "Receipt box" workflow
   → Physical box at POS station
   → Staff drops receipts in during shift
   → Bookkeeper photographs batch weekly (10-min task)
   → Catches the remaining cash/debit purchases

4. Monthly "missing receipt" report
   → Bank statement items without matching Dext entry
   → Owner reviews and provides missing documentation
   → Deadline: by month-end close (day 5)
```

---

## BLOCKER 3: Lightspeed → QBO Sync Reliability (HIGH)

**Who it blocks:** Bookkeeper, CPA
**What happens:** The daily POS-to-accounting sync breaks. Revenue stops posting
to the general ledger. Nobody notices for days or weeks.

**Why it's a blocker:**
- Lightspeed-QBO integration uses APIs that can silently disconnect
- No built-in alerting — if sync fails on a Tuesday, the bookkeeper may not
  notice until month-end
- Accumulated unsynced days create a large manual re-entry task
- Revenue accounts in QBO show stale data → misleading financial position

**Impact if not addressed:**
- Month-end close delayed by days
- SRM-to-GL reconciliation fails
- GST/QST return preparation blocked

**Remediation:**
```
1. Daily automated check (via Make/Zapier)
   → Every morning at 8 AM, compare:
      Yesterday's Lightspeed daily total vs. QBO revenue posted
   → If difference > $50 or QBO entry missing → Slack/email alert

2. Weekly bookkeeper verification
   → Every Monday: confirm prior week's 7 days are synced
   → 5-minute task in QBO: check sales clearing account balance

3. Fallback: manual CSV import
   → If sync breaks, Lightspeed exports daily summary as CSV
   → Import to QBO via journal entry template (pre-built)
   → Temporary measure while integration is repaired
```

---

## BLOCKER 4: Third-Party Delivery Platform Reconciliation (HIGH)

**Who it blocks:** Bookkeeper
**What happens:** Uber Eats, DoorDash, and Skip pay Giwa net of commissions,
on different schedules than the sale date. SRM records the gross sale at
order time, but the bank deposit is different.

**Why it's a blocker:**
- Uber Eats commission is ~30% — a $100 order generates a $70 deposit
- Deposits arrive weekly, not daily — timing mismatch with SRM
- SRM records GST/QST on $100 (gross), but Giwa only receives $70
- Commission is a separate expense (with its own GST/QST implications)
- Three separate platforms × weekly reconciliation = complex, error-prone

**Impact if not addressed:**
- Revenue overstated if commissions not recorded
- Bank reconciliation shows unmatched deposits
- GST/QST collected per SRM ≠ cash received (confuses bookkeeper)

**Remediation:**
```
1. Separate GL accounts per platform
   → 4050 Uber Eats Revenue
   → 4060 DoorDash Revenue
   → 4070 Skip Revenue
   → 5300 Delivery Platform Commissions

2. Weekly reconciliation template
   → Download platform payout reports (Uber/DoorDash/Skip portals)
   → Template auto-splits: gross sale, commission, net deposit
   → Posts journal entry: DR Cash, DR Commission Expense, CR Revenue

3. Platform-specific Dext rules
   → Platform commission invoices auto-categorized
   → GST/QST on commissions captured for ITC/ITR

4. SRM handling
   → Verify POS records delivery orders through SRM at gross amount
   → Commission is an expense, not a revenue reduction
```

---

## BLOCKER 5: Owner Doesn't Understand the PME-6.1 Value (HIGH)

**Who it blocks:** Owner (decision-maker)
**What happens:** The owner doesn't see why they should invest time in tip
tracking, Dext receipts, and monthly closes. It feels like overhead for a
small restaurant barely breaking even.

**Why it's a blocker:**
- If the owner isn't bought in, they won't do their part (receipts, tip declarations)
- The entire workflow depends on source data quality — which the owner controls
- At $30K/month revenue, every hour spent on admin feels like an hour not cooking

**Impact if not addressed:**
- System produces garbage data → CPA can't rely on it → reverts to manual year-end
- PME-6.1 credit ($4,382) goes unclaimed
- ITCs/ITRs partially missed → overpaying GST/QST by thousands

**Remediation:**
```
"Show them the money" onboarding conversation:

1. PME-6.1 Credit:           $4,382/year  (refundable — cash in hand)
2. Full ITC/ITR recovery:    $2,000–$5,000/year  (vs. missing receipts)
3. Accurate COGS tracking:   Identifies food waste → 1-2% savings = $3,600–$7,200
4. Audit protection:         Avoid $5,000–$50,000+ in reassessments

Total annual value:           $10,000–$17,000+

vs. Owner's time investment:  ~15 minutes/day (receipt photos, tip verification)

ROI:  $10K+ return for 90 hours of effort = $111/hour effective rate
```

Frame it as: "You're getting paid $111/hour to take photos of receipts."

---

## BLOCKER 6: SRM Hardware Failure / Downtime (MEDIUM)

**Who it blocks:** All front-of-house staff, owner
**What happens:** The SRM unit fails. Giwa cannot legally process transactions
without a certified SRM. Options: shut down, or operate in violation.

**Why it's a blocker:**
- SRM hardware is a single point of failure
- Replacement/repair takes days
- Penalties: $300–$5,000/day for operating without certified SRM
- Most small restaurants have NO backup plan

**Remediation:**
```
1. Backup SRM unit
   → Purchase a second certified SRM (~$300–$500)
   → Pre-configured and ready to swap
   → Annual cost of insurance against $5,000/day penalty

2. Emergency procedures documented
   → If SRM fails: manual bill production with required elements
   → Notify Revenu Québec within 24 hours (document the notification)
   → Retain paper copies of all transactions during downtime
   → Re-enter into SRM when restored

3. SRM maintenance schedule
   → Firmware check quarterly
   → Certificate expiry tracked (calendar alert 90 days before)
```

---

## BLOCKER 7: Payroll Rate Updates (January 1 Every Year) (MEDIUM)

**Who it blocks:** Bookkeeper, payroll processor
**What happens:** QPP, EI, QPIP, CNESST, and minimum wage rates change every
January 1. If the payroll system isn't updated, source deductions are wrong
for the entire year.

**Why it's a blocker:**
- Wagepoint/Ceridian usually auto-update, but must be VERIFIED
- CNESST classification rate changes based on employer experience rating
- Quebec tipped minimum wage may change — affects Server A, B, Bartender
- If wrong rate used: CRA/RQ arrears at year-end, director liability

**Remediation:**
```
Annual January checklist (add to workflow_config.yaml):
  - [ ] Verify QPP/QPP2 rates updated in payroll system
  - [ ] Verify EI premium rate updated
  - [ ] Verify QPIP rate updated
  - [ ] Verify CNESST rate (check annual classification letter from CNESST)
  - [ ] Verify HSF rate tier (based on prior-year total payroll)
  - [ ] Verify Quebec tipped minimum wage
  - [ ] Verify Quebec general minimum wage
  - [ ] Verify federal/QC personal tax credit amounts (TD1/TP-1015.3-V)
  - [ ] Run test pay for one employee — compare to manual calculation
  - [ ] Document verification in working papers
```

---

## BLOCKER 8: Bookkeeper Turnover / Skill Gap (MEDIUM)

**Who it blocks:** Entire workflow
**What happens:** The bookkeeper leaves or doesn't understand SRM reconciliation,
Dext workflows, or Quebec payroll. The system runs on autopilot but nobody
reviews the exceptions.

**Why it's a blocker:**
- SRM reconciliation requires understanding of POS → SRM → GL data flow
- Quebec payroll has unique elements (QPP2, QPIP, CNESST, HSF) that Ontario
  bookkeepers may not know
- Dext requires ongoing rule maintenance as new suppliers are added
- Without competent review, automated exceptions accumulate unresolved

**Remediation:**
```
1. Standard operating procedures (SOPs)
   → Already built: test_walkthrough.md + srm_mev_reconciliation.md
   → Convert to step-by-step screencasts for each monthly task
   → Estimated: 6 videos × 10 minutes each

2. Cross-training
   → CPA preparer should be able to cover bookkeeper tasks
   → Document all Dext rules and QBO bank rules in a config sheet

3. Monthly review cadence
   → CPA reviews bookkeeper's work by day 10 (per monthly calendar)
   → Catches errors before period lock

4. Consider outsourced bookkeeping
   → At Giwa's size ($30K/month), outsourced bookkeeping is viable
   → Cost: $500–$800/month vs. in-house part-time bookkeeper
   → Eliminates turnover risk
```

---

## BLOCKER 9: Bank Feed Disconnection (MEDIUM)

**Who it blocks:** Bookkeeper
**What happens:** QBO bank feeds (via Plaid/Flinks) disconnect. This happens
regularly with Canadian banks — security updates, 2FA changes, or API issues.

**Why it's a blocker:**
- When feed disconnects, new transactions stop importing
- Bookkeeper may not notice for days
- Manual import via CSV is tedious and error-prone
- Bank reconciliation becomes impossible until feed restored

**Remediation:**
```
1. Weekly bank feed health check
   → Every Monday: verify QBO shows transactions through Friday
   → 2-minute visual check

2. Alert configuration
   → QBO sends email if bank feed inactive > 3 days
   → Add to Slack #giwa-finance channel

3. Reconnection SOP
   → Document bank-specific reconnection steps (Desjardins, TD, RBC, etc.)
   → Keep bank login credentials accessible to bookkeeper
   → Typical fix: re-authenticate in QBO → bank → approve connection
```

---

## BLOCKER 10: Language / Loi 101 Compliance (LOW)

**Who it blocks:** Owner, staff
**What happens:** Software interfaces, Dext prompts, or CPA communications
are in English only. Under Loi 101, Quebec employees have the right to work
in French.

**Why it's a blocker:**
- Lightspeed supports French (Montreal-based company)
- QBO supports French (Canada version)
- Dext has limited French support
- TaxCycle supports French
- Staff may struggle with English-only Dext mobile app

**Remediation:**
```
1. Configure all software in French where available
2. Create French-language SOPs for staff-facing procedures
3. Dext: mobile app screenshots in French (if available) or create visual guides
4. Tip declaration forms must be in French
```

---

## Summary: Blocker Priority Matrix

| # | Blocker | Severity | User | Effort to Fix | Cost to Ignore |
|---|---------|----------|------|---------------|----------------|
| 1 | Cash tip declaration | CRITICAL | Staff | Medium (POS config) | RQ audit, attribution |
| 2 | Receipt capture discipline | CRITICAL | Owner | Medium (Dext fetch + training) | $20K+/yr lost ITCs |
| 3 | Lightspeed → QBO sync | HIGH | Bookkeeper | Low (daily alert) | Delayed closes |
| 4 | Delivery platform reconciliation | HIGH | Bookkeeper | Medium (templates) | Revenue misstatement |
| 5 | Owner buy-in / PME value | HIGH | Owner | Low (one conversation) | $4,382 credit lost |
| 6 | SRM hardware failure | MEDIUM | Owner | Low (backup unit) | $300–$5K/day penalty |
| 7 | Payroll rate updates (Jan 1) | MEDIUM | Bookkeeper | Low (annual checklist) | CRA/RQ arrears |
| 8 | Bookkeeper turnover | MEDIUM | Firm | Medium (SOPs + videos) | Workflow collapse |
| 9 | Bank feed disconnection | MEDIUM | Bookkeeper | Low (weekly check) | Delayed reconciliation |
| 10 | Loi 101 language | LOW | Staff | Low (config change) | Employee complaint |

---

## Recommended Implementation Order

**Week 1 — Address CRITICAL blockers before go-live:**
1. Configure POS cash tip declaration prompt (Blocker 1)
2. Set up Dext Fetch for top 5 suppliers by email (Blocker 2)
3. Create "receipt box" at POS station (Blocker 2)
4. Have the "show them the money" conversation with owner (Blocker 5)

**Week 2 — Address HIGH blockers:**
5. Build daily Lightspeed → QBO sync check (Blocker 3)
6. Create delivery platform reconciliation templates (Blocker 4)
7. Configure alert channels (Slack + email)

**Week 3 — Address MEDIUM blockers:**
8. Purchase backup SRM unit (Blocker 6)
9. Build January 1 payroll rate checklist (Blocker 7)
10. Record SOP screencasts for bookkeeper (Blocker 8)
11. Document bank feed reconnection steps (Blocker 9)

**Week 4 — Polish:**
12. Configure French language settings (Blocker 10)
13. Run Test 6 (live data smoke test) from test_walkthrough.md
14. Go-live with full monitoring

---

*This analysis is based on the specific workflow designed for Giwa Restaurant at
$30K/month revenue with 7 employees. Blockers may differ for larger operations
or different restaurant formats.*
