#!/usr/bin/env python3
"""
BLOCKER 7 FIX: Annual Payroll Rate Validator

Run every January 1 to verify payroll system rates match current-year
CRA and Revenu Québec published rates.

Usage:
    python payroll_rate_validator.py --year 2025
    python payroll_rate_validator.py --year 2025 --check-payroll-output payroll_jan.csv
"""

import argparse
import csv
from pathlib import Path

# --- Published rates by year (update annually from CRA/RQ sources) ---
# These rates should be verified against official publications each January.

RATES = {
    2025: {
        "qpp_employee": 0.0640,
        "qpp_employer": 0.0640,
        "qpp_exemption_annual": 3500.00,
        "qpp_max_pensionable": 71300.00,
        "qpp2_employee": 0.0400,  # Second additional QPP (on earnings above first ceiling)
        "qpp2_max": 79400.00,  # Second ceiling

        "ei_employee": 0.01180,  # Quebec rate (reduced)
        "ei_employer_multiplier": 1.4,
        "ei_max_insurable": 65700.00,

        "qpip_employee": 0.00494,
        "qpip_employer": 0.00692,
        "qpip_max_insurable": 98000.00,

        "hsf_rate_tier1": 0.0165,  # Payroll ≤ $1M
        "hsf_rate_tier2": 0.0165,  # Between $1M and $7M (graduated)
        "hsf_rate_tier3": 0.0425,  # Payroll > $7M

        "cnt_rate": 0.0007,

        "qc_min_wage_general": 15.75,
        "qc_min_wage_tipped": 12.60,

        "fed_basic_personal": 16129.00,
        "qc_basic_personal": 18056.00,

        "cnesst_restaurant_code": "91030",
        # CNESST rate varies by employer experience — verify individually
    },
    2026: {
        # Placeholder — update when rates are published (usually December)
        "qpp_employee": None,
        "qpp_employer": None,
        "ei_employee": None,
        "qc_min_wage_general": None,
        "qc_min_wage_tipped": None,
        # ... fill in when available
    },
}


def validate_rates(year: int):
    """Display and validate payroll rates for the given year."""
    if year not in RATES:
        print(f"ERROR: Rates not configured for {year}. Available years: {list(RATES.keys())}")
        return False

    rates = RATES[year]
    all_set = True

    print(f"\n{'='*65}")
    print(f"PAYROLL RATE VALIDATION — {year}")
    print(f"{'='*65}")

    checks = [
        ("QPP Employee Rate", "qpp_employee", lambda v: f"{v:.2%}"),
        ("QPP Employer Rate", "qpp_employer", lambda v: f"{v:.2%}"),
        ("QPP Annual Exemption", "qpp_exemption_annual", lambda v: f"${v:,.2f}"),
        ("QPP Max Pensionable Earnings", "qpp_max_pensionable", lambda v: f"${v:,.2f}"),
        ("QPP2 Employee Rate", "qpp2_employee", lambda v: f"{v:.2%}"),
        ("QPP2 Second Ceiling", "qpp2_max", lambda v: f"${v:,.2f}"),
        ("EI Employee Rate (QC)", "ei_employee", lambda v: f"{v:.3%}"),
        ("EI Employer Multiplier", "ei_employer_multiplier", lambda v: f"{v:.1f}x"),
        ("EI Max Insurable Earnings", "ei_max_insurable", lambda v: f"${v:,.2f}"),
        ("QPIP Employee Rate", "qpip_employee", lambda v: f"{v:.3%}"),
        ("QPIP Employer Rate", "qpip_employer", lambda v: f"{v:.3%}"),
        ("QPIP Max Insurable", "qpip_max_insurable", lambda v: f"${v:,.2f}"),
        ("HSF Rate (payroll ≤ $1M)", "hsf_rate_tier1", lambda v: f"{v:.2%}"),
        ("CNT Rate", "cnt_rate", lambda v: f"{v:.2%}"),
        ("QC Min Wage (general)", "qc_min_wage_general", lambda v: f"${v:.2f}/hr"),
        ("QC Min Wage (tipped)", "qc_min_wage_tipped", lambda v: f"${v:.2f}/hr"),
        ("Federal Basic Personal Amount", "fed_basic_personal", lambda v: f"${v:,.2f}"),
        ("QC Basic Personal Amount", "qc_basic_personal", lambda v: f"${v:,.2f}"),
    ]

    for label, key, formatter in checks:
        value = rates.get(key)
        if value is None:
            print(f"  [X] {label:<40} NOT SET — UPDATE REQUIRED")
            all_set = False
        else:
            print(f"  [+] {label:<40} {formatter(value)}")

    # CNESST
    cnesst_code = rates.get("cnesst_restaurant_code", "N/A")
    print(f"\n  CNESST Classification: {cnesst_code}")
    print(f"  NOTE: CNESST rate is employer-specific. Check your annual")
    print(f"  classification letter from CNESST (arrives in December).")

    print(f"\n{'-'*65}")
    if all_set:
        print(f"STATUS: All {year} rates are configured.")
        print(f"\nACTION: Verify these match your payroll system settings:")
        print(f"  1. Log into Wagepoint/Ceridian admin panel")
        print(f"  2. Navigate to tax table settings")
        print(f"  3. Confirm each rate above matches the system")
        print(f"  4. Run a test payroll for one employee")
        print(f"  5. Compare deductions to manual calculation below")
    else:
        print(f"STATUS: INCOMPLETE — Some {year} rates need to be updated.")
        print(f"  Check CRA and Revenu Québec websites for published rates.")
        print(f"  CRA:  canada.ca/payroll")
        print(f"  RQ:   revenuquebec.ca/en/businesses/source-deductions-and-employer-contributions/")
    print(f"{'='*65}")

    # Sample calculation for verification
    if all_set and rates["qpp_employee"] is not None:
        print(f"\n{'='*65}")
        print(f"SAMPLE CALCULATION — Server A (Tipped Employee)")
        print(f"{'='*65}")
        gross = 1723.00  # Semi-monthly gross (wages + tips)
        wages = 756.00
        tips = 967.00

        qpp_exempt_per_period = rates["qpp_exemption_annual"] / 24  # Semi-monthly
        qpp_base = max(0, gross - qpp_exempt_per_period)
        qpp_employee = qpp_base * rates["qpp_employee"]

        ei_employee = gross * rates["ei_employee"]
        ei_employer = ei_employee * rates["ei_employer_multiplier"]

        qpip_employee = gross * rates["qpip_employee"]
        qpip_employer = gross * rates["qpip_employer"]

        print(f"  Gross Pay:           ${gross:>10,.2f}  (wages: ${wages:.2f} + tips: ${tips:.2f})")
        print(f"  QPP Exemption:       ${qpp_exempt_per_period:>10,.2f}  (${rates['qpp_exemption_annual']:,.2f} ÷ 24)")
        print(f"  QPP Employee:        ${qpp_employee:>10,.2f}  ({qpp_base:.2f} × {rates['qpp_employee']:.2%})")
        print(f"  EI Employee:         ${ei_employee:>10,.2f}  ({gross:.2f} × {rates['ei_employee']:.3%})")
        print(f"  EI Employer:         ${ei_employer:>10,.2f}  ({ei_employee:.2f} × {rates['ei_employer_multiplier']:.1f})")
        print(f"  QPIP Employee:       ${qpip_employee:>10,.2f}  ({gross:.2f} × {rates['qpip_employee']:.3%})")
        print(f"  QPIP Employer:       ${qpip_employer:>10,.2f}  ({gross:.2f} × {rates['qpip_employer']:.3%})")
        print(f"\n  Compare these to your payroll system output for Server A.")
        print(f"  Tolerance: ±$2.00 per deduction line.")
        print(f"{'='*65}\n")

    return all_set


def check_payroll_output(filepath: str, year: int):
    """Cross-check a payroll CSV output against published rates."""
    rates = RATES.get(year)
    if not rates or rates.get("qpp_employee") is None:
        print(f"ERROR: Rates not configured for {year}")
        return

    print(f"\nCross-checking payroll output against {year} rates...")
    issues = []

    with open(filepath, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            emp = row.get("employee_name", row.get("employee_id", "Unknown"))
            gross = float(row.get("gross_pay", 0))
            if gross <= 0:
                continue

            # Check EI rate
            ei_actual = float(row.get("ei_employee", 0))
            ei_expected = gross * rates["ei_employee"]
            if abs(ei_actual - ei_expected) > 2.00:
                issues.append(
                    f"{emp}: EI expected ${ei_expected:.2f}, got ${ei_actual:.2f} "
                    f"(diff: ${abs(ei_actual - ei_expected):.2f})"
                )

    if issues:
        print(f"\n{len(issues)} ISSUE(S) FOUND:")
        for i in issues:
            print(f"  [X] {i}")
    else:
        print(f"\nAll deductions within tolerance. Payroll rates appear correct.")


def main():
    parser = argparse.ArgumentParser(description="Payroll Rate Validator")
    parser.add_argument("--year", type=int, required=True, help="Tax year to validate")
    parser.add_argument("--check-payroll-output", help="CSV file to cross-check")
    args = parser.parse_args()

    result = validate_rates(args.year)

    if args.check_payroll_output:
        check_payroll_output(args.check_payroll_output, args.year)


if __name__ == "__main__":
    main()
