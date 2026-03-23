"""
Bridge between the Flask web dashboard and the existing automation modules.

In production, this module replaces the mock data in app.py with real data
from the automation scripts. Import and call these functions from app.py
once the integrations are configured with real credentials.
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add parent directory so we can import existing modules
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def run_sync_health_check(check_date=None):
    """
    Run the daily sync health check and return structured results.
    Wraps: fixes/scripts/sync_health_check.py
    """
    try:
        from fixes.scripts.sync_health_check import SyncHealthChecker
        checker = SyncHealthChecker()
        date_str = check_date or datetime.now().strftime('%Y-%m-%d')
        result = checker.check_date(date_str)
        return {
            'status': 'healthy' if result.get('passed') else 'unhealthy',
            'date': date_str,
            'details': result,
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}


def run_missing_receipt_detection():
    """
    Detect missing receipts and return structured results.
    Wraps: fixes/scripts/missing_receipt_detector.py
    """
    try:
        from fixes.scripts.missing_receipt_detector import MissingReceiptDetector
        detector = MissingReceiptDetector()
        results = detector.detect_missing()
        return {
            'count': len(results.get('missing', [])),
            'total_amount': results.get('total_unmatched', 0),
            'items': results.get('missing', []),
        }
    except Exception as e:
        return {'count': 0, 'error': str(e)}


def run_delivery_reconciliation():
    """
    Reconcile delivery platform payouts.
    Wraps: fixes/scripts/delivery_platform_reconciler.py
    """
    try:
        from fixes.scripts.delivery_platform_reconciler import DeliveryReconciler
        reconciler = DeliveryReconciler()
        results = reconciler.reconcile_all()
        return {
            'platforms': results.get('platforms', {}),
            'total_variance': results.get('total_variance', 0),
            'journal_entries': results.get('entries', []),
        }
    except Exception as e:
        return {'platforms': {}, 'error': str(e)}


def run_tip_attribution_summary():
    """
    Get tip attribution and PME-6.1 credit data.
    Wraps: fixes/scripts/tip_declaration_system.py
    """
    try:
        from fixes.scripts.tip_declaration_system import TipDeclarationSystem
        system = TipDeclarationSystem()
        summary = system.get_daily_summary()
        return {
            'total_declared': summary.get('total_declared', 0),
            'declaration_rate': summary.get('avg_rate', 0),
            'meets_minimum': summary.get('avg_rate', 0) >= 8.0,
            'employees': summary.get('employees', []),
        }
    except Exception as e:
        return {'total_declared': 0, 'error': str(e)}


def run_payroll_validation(year=None):
    """
    Validate payroll rates for the given year.
    Wraps: fixes/scripts/payroll_rate_validator.py
    """
    try:
        from fixes.scripts.payroll_rate_validator import PayrollRateValidator
        year = year or datetime.now().year
        validator = PayrollRateValidator()
        results = validator.validate(year)
        return {
            'year': year,
            'passed': results.get('all_passed', False),
            'checks': results.get('checks', []),
        }
    except Exception as e:
        return {'year': year, 'passed': False, 'error': str(e)}


def run_validation_suite():
    """
    Run the full reconciliation validation suite.
    Wraps: testing/validate_reconciliation.py
    """
    try:
        from testing.validate_reconciliation import run_all_validations
        results = run_all_validations()
        passed = sum(1 for r in results if r.get('passed'))
        total = len(results)
        return {
            'passed': passed,
            'total': total,
            'all_passed': passed == total,
            'checks': results,
        }
    except Exception as e:
        return {'passed': 0, 'total': 0, 'error': str(e)}


def get_qbo_revenue_summary(start_date, end_date):
    """
    Pull revenue summary from QuickBooks Online.
    Wraps: integrations/qbo_client.py
    """
    try:
        from integrations.qbo_client import QBOClient
        client = QBOClient()
        return client.get_revenue_by_date(start_date, end_date)
    except Exception as e:
        return {'error': str(e)}


def get_qbo_tax_summary(start_date, end_date):
    """
    Pull GST/QST summary from QuickBooks Online.
    Wraps: integrations/qbo_client.py
    """
    try:
        from integrations.qbo_client import QBOClient
        client = QBOClient()
        return client.get_sales_tax_summary(start_date, end_date)
    except Exception as e:
        return {'error': str(e)}


# ---------------------------------------------------------------------------
# Aggregated dashboard data (call from app.py routes)
# ---------------------------------------------------------------------------

def get_live_kpi_data():
    """Aggregate KPIs from all automation modules."""
    sync = run_sync_health_check()
    receipts = run_missing_receipt_detection()

    return {
        'sync_health': 'Healthy' if sync.get('status') == 'healthy' else 'Unhealthy',
        'sync_streak': 0,
        'missing_receipts': receipts.get('count', 0),
        'receipt_trend': 'down',
        'receipt_change': 'N/A',
        'srm_variance': 'N/A',
        'next_filing_type': 'QST Q1',
        'next_filing_date': 'Apr 30',
    }


def get_live_alerts():
    """Pull real alerts from the alerter log."""
    log_path = os.path.join(ROOT, 'logs', 'alerts.json')
    if not os.path.exists(log_path):
        return []

    try:
        with open(log_path) as f:
            entries = json.load(f)

        alerts = []
        for entry in entries[-10:]:
            level_map = {'CRITICAL': 'critical', 'HIGH': 'critical', 'WARNING': 'warning', 'INFO': 'info'}
            alerts.append({
                'level': level_map.get(entry.get('level', 'INFO'), 'info'),
                'title': entry.get('message', ''),
                'time': entry.get('timestamp', ''),
            })
        return list(reversed(alerts))
    except Exception:
        return []
