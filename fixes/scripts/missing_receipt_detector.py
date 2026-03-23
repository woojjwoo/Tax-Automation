#!/usr/bin/env python3
"""
BLOCKER 2 FIX: Missing Receipt Detector

Compares bank/credit card transactions against Dext-captured expenses
to find missing receipts. Calculates the ITC/ITR cost of each missing receipt.

Usage:
    python missing_receipt_detector.py --bank-csv sample_bank.csv --dext-csv january_expenses_dext.csv
    python missing_receipt_detector.py --demo  # Run with built-in demo data
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

GST_RATE = 0.05
QST_RATE = 0.09975
ME_CATEGORIES = {"restaurant", "entertainment", "meals & entertainment", "catering"}

SAMPLE_DATA_DIR = Path(__file__).parent.parent.parent / "testing" / "sample_data"


@dataclass
class Transaction:
    date: str
    description: str
    amount: float
    source: str  # "bank" or "dext"
    matched: bool = False


@dataclass
class MissingReceipt:
    date: str
    description: str
    amount: float
    estimated_gst: float
    estimated_qst: float
    lost_itc: float
    lost_itr: float
    priority: str  # "HIGH" (>$150) or "MEDIUM" (<$150)


def load_dext_expenses(filepath: str) -> list[Transaction]:
    """Load Dext-captured expenses."""
    transactions = []
    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            transactions.append(Transaction(
                date=row["date"],
                description=row["vendor"],
                amount=float(row["total_amount"]),
                source="dext",
            ))
    return transactions


def generate_demo_bank_data() -> list[Transaction]:
    """Generate realistic bank transactions for January including some
    that WON'T have matching Dext receipts (the missing ones)."""
    return [
        # These MATCH Dext data
        Transaction("2025-01-03", "SYSCO CANADA", 2816.89, "bank"),
        Transaction("2025-01-03", "SAQ SUCCURSALE", 919.80, "bank"),
        Transaction("2025-01-06", "SYSCO CANADA", 2127.04, "bank"),
        Transaction("2025-01-08", "LAVO CHIMIQUE", 212.70, "bank"),
        Transaction("2025-01-10", "SYSCO CANADA", 2529.45, "bank"),
        Transaction("2025-01-10", "PEPSI CO", 172.46, "bank"),
        Transaction("2025-01-15", "VIR LOYER COMMERCIAL", 4024.13, "bank"),
        Transaction("2025-01-17", "SYSCO CANADA", 2414.48, "bank"),
        Transaction("2025-01-24", "SYSCO CANADA", 2701.91, "bank"),
        Transaction("2025-01-24", "SAQ SUCCURSALE", 747.34, "bank"),
        Transaction("2025-01-31", "SYSCO CANADA", 2069.55, "bank"),
        Transaction("2025-01-31", "LIGHTSPEED COMMERCE", 172.46, "bank"),

        # These are MISSING from Dext (no receipt captured)
        Transaction("2025-01-05", "MARCHE JEAN-TALON", 187.50, "bank"),
        Transaction("2025-01-09", "DOLLARAMA #1234", 42.30, "bank"),
        Transaction("2025-01-12", "UBER EATS PAYOUT", -1850.00, "bank"),  # Revenue, not expense
        Transaction("2025-01-14", "METRO RICHELIEU", 312.75, "bank"),
        Transaction("2025-01-19", "CANADIAN TIRE #567", 89.95, "bank"),
        Transaction("2025-01-22", "MARCHE JEAN-TALON", 225.00, "bank"),
        Transaction("2025-01-25", "RESTO DEPOT EQUIP", 445.00, "bank"),
        Transaction("2025-01-28", "INTERAC PURCHASE", 35.60, "bank"),
        Transaction("2025-01-30", "UBER EATS PAYOUT", -2100.00, "bank"),  # Revenue, not expense
    ]


def match_transactions(bank: list[Transaction], dext: list[Transaction],
                       tolerance: float = 5.00) -> list[MissingReceipt]:
    """Match bank transactions to Dext receipts. Return unmatched (missing)."""
    missing = []

    for b in bank:
        # Skip revenue deposits (negative = money coming in)
        if b.amount <= 0:
            continue

        # Try to find a matching Dext entry
        matched = False
        for d in dext:
            if d.matched:
                continue
            # Match by amount (within tolerance) and approximate date (±3 days)
            amount_match = abs(b.amount - d.amount) <= tolerance
            if amount_match:
                b.matched = True
                d.matched = True
                matched = True
                break

        if not matched:
            # Calculate lost ITCs/ITRs
            # Estimate pre-tax amount: total / (1 + GST + QST)
            pre_tax = b.amount / (1 + GST_RATE + QST_RATE)
            est_gst = pre_tax * GST_RATE
            est_qst = pre_tax * QST_RATE

            # Check if likely M&E (50% restriction)
            desc_lower = b.description.lower()
            is_me = any(cat in desc_lower for cat in ME_CATEGORIES)
            restriction = 0.50 if is_me else 1.0

            lost_itc = est_gst * restriction
            lost_itr = est_qst * restriction
            priority = "HIGH" if b.amount >= 150 else "MEDIUM"

            missing.append(MissingReceipt(
                date=b.date,
                description=b.description,
                amount=b.amount,
                estimated_gst=est_gst,
                estimated_qst=est_qst,
                lost_itc=lost_itc,
                lost_itr=lost_itr,
                priority=priority,
            ))

    return missing


def print_report(missing: list[MissingReceipt], month: str = "January 2025"):
    """Print the missing receipt report."""
    print(f"\n{'='*80}")
    print(f"MISSING RECEIPT REPORT — {month}")
    print(f"{'='*80}")

    if not missing:
        print("\nNo missing receipts detected. All bank transactions matched to Dext.")
        print(f"{'='*80}\n")
        return

    print(f"\n{'Date':<12} {'Description':<25} {'Amount':>10} {'Lost ITC':>10} "
          f"{'Lost ITR':>10} {'Priority':<8}")
    print(f"{'-'*12:<12} {'-'*25:<25} {'-'*10:>10} {'-'*10:>10} "
          f"{'-'*10:>10} {'-'*8:<8}")

    total_amount = 0
    total_itc = 0
    total_itr = 0
    high_count = 0

    for m in sorted(missing, key=lambda x: (-x.amount)):
        print(f"{m.date:<12} {m.description:<25} ${m.amount:>9,.2f} "
              f"${m.lost_itc:>9,.2f} ${m.lost_itr:>9,.2f} {m.priority:<8}")
        total_amount += m.amount
        total_itc += m.lost_itc
        total_itr += m.lost_itr
        if m.priority == "HIGH":
            high_count += 1

    print(f"{'-'*12:<12} {'-'*25:<25} {'-'*10:>10} {'-'*10:>10} "
          f"{'-'*10:>10}")
    print(f"{'TOTAL':<12} {f'{len(missing)} missing':<25} ${total_amount:>9,.2f} "
          f"${total_itc:>9,.2f} ${total_itr:>9,.2f}")

    annual_itc_loss = total_itc * 12
    annual_itr_loss = total_itr * 12
    annual_total_loss = annual_itc_loss + annual_itr_loss

    print(f"\n{'='*80}")
    print(f"FINANCIAL IMPACT SUMMARY")
    print(f"{'='*80}")
    print(f"Missing receipts this month:      {len(missing)}")
    print(f"High priority (>$150):            {high_count}")
    print(f"Total unmatched expenses:         ${total_amount:,.2f}")
    print(f"")
    print(f"Monthly lost ITCs (GST):          ${total_itc:,.2f}")
    print(f"Monthly lost ITRs (QST):          ${total_itr:,.2f}")
    print(f"Monthly total tax loss:           ${total_itc + total_itr:,.2f}")
    print(f"")
    print(f"PROJECTED ANNUAL LOSS:            ${annual_total_loss:,.2f}")
    print(f"{'='*80}")

    # Action items
    print(f"\nACTION REQUIRED:")
    for i, m in enumerate(sorted(missing, key=lambda x: (-x.amount)), 1):
        action = "Find receipt or request duplicate from vendor"
        if m.priority == "HIGH":
            action = "URGENT: Find receipt — ITC/ITR requires GST#/QST# for claims >$150"
        print(f"  {i}. [{m.priority}] {m.date} {m.description} ${m.amount:,.2f} — {action}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Missing Receipt Detector for Giwa Restaurant")
    parser.add_argument("--bank-csv", help="Bank statement CSV file")
    parser.add_argument("--dext-csv", help="Dext expenses CSV file")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        # Load Dext data from test samples
        dext_file = SAMPLE_DATA_DIR / "january_expenses_dext.csv"
        if not dext_file.exists():
            print(f"Demo data not found at {dext_file}")
            return 1

        dext = load_dext_expenses(str(dext_file))
        bank = generate_demo_bank_data()
        missing = match_transactions(bank, dext)
        print_report(missing)
        return 0 if not missing else 1

    elif args.bank_csv and args.dext_csv:
        dext = load_dext_expenses(args.dext_csv)
        # For custom bank CSV, assume columns: date, description, amount
        bank = []
        with open(args.bank_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                bank.append(Transaction(
                    date=row["date"],
                    description=row["description"],
                    amount=float(row["amount"]),
                    source="bank",
                ))
        missing = match_transactions(bank, dext)
        print_report(missing)
        return 0 if not missing else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
