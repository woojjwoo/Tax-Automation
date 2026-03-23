# BLOCKER 9 FIX: Bank Feed Reconnection Guide

**When QBO bank feeds disconnect (and they will), follow these steps.**

---

## How to Know the Feed is Down

- QBO Banking tab shows "Needs attention" or "Disconnected"
- Last transaction date is more than 2 business days old
- Weekly Monday check shows gap in transactions

---

## Reconnection Steps by Bank

### Desjardins (AccèsD)

1. QBO → Banking → click the disconnected account
2. Click "Update" or "Reconnect"
3. You'll be redirected to Desjardins login
4. Enter your AccèsD credentials
5. Complete 2FA (SMS or SecureKey)
6. Authorize QBO access
7. Wait 5–10 minutes for transactions to sync
8. **Common issue:** Desjardins blocks third-party access after password change.
   Fix: log into AccèsD first, then reconnect QBO.

### TD Canada Trust (EasyWeb)

1. QBO → Banking → click the disconnected account
2. Click "Reconnect"
3. Enter EasyWeb credentials
4. Complete 2FA
5. **Common issue:** TD requires you to accept updated terms in EasyWeb
   before third-party connections work. Log into EasyWeb directly first.

### RBC Royal Bank

1. QBO → Banking → Reconnect
2. Enter RBC online banking credentials
3. Complete 2FA (Verified.Me or SMS)
4. **Common issue:** RBC feeds break monthly due to security rotations.
   If reconnect fails, wait 24 hours and try again.

### National Bank (Banque Nationale)

1. QBO → Banking → Reconnect
2. Enter credentials + 2FA
3. **Common issue:** National Bank uses Plaid for connections.
   If Plaid is down, feeds won't reconnect. Check status.plaid.com.

---

## If Reconnection Fails

### Option A: Wait 24 Hours
Some disconnections are temporary (bank maintenance, Plaid outage).

### Option B: Manual CSV Import
1. Log into bank website
2. Download transactions as CSV (last 30 days)
3. QBO → Banking → Upload transactions
4. Select the bank account
5. Map CSV columns to QBO fields
6. Import and categorize manually

### Option C: Contact QBO Support
Call: **1-888-829-8589**
Have ready: QBO company ID, bank name, error message

---

## Prevention

- [ ] Check bank feeds every Monday (Section A of monthly SOP)
- [ ] Don't change bank passwords without reconnecting QBO immediately after
- [ ] Keep bank login credentials in a secure password manager
- [ ] Set QBO to send email alerts when feeds inactive > 3 days
  (QBO → Settings → Notifications → Bank feeds)
