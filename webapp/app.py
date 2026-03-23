"""
RestoTax Web Application
Flask-based landing page + client dashboard for Quebec restaurant tax automation.
"""

import os
import sys
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)

# Add parent directory to path so we can import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# ---------------------------------------------------------------------------
# Demo client database (replace with real DB in production)
# ---------------------------------------------------------------------------
DEMO_CLIENTS = {
    'demo@giwa.ca': {
        'password_hash': hashlib.sha256('demo123'.encode()).hexdigest(),
        'name': 'Giwa Restaurant Inc.',
        'initials': 'GR',
        'plan': 'Professional',
        'restaurant_id': 'giwa-001',
        'integrations': {
            'qbo': True,
            'lightspeed': True,
            'wagepoint': True,
            'dext': True,
            'uber_eats': True,
        },
    },
    'admin@restotax.ca': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'name': 'RestoTax Admin',
        'initials': 'RA',
        'plan': 'Enterprise',
        'restaurant_id': 'admin',
        'integrations': {
            'qbo': True,
            'lightspeed': True,
            'wagepoint': True,
            'dext': True,
            'uber_eats': True,
        },
    },
}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_current_client():
    email = session.get('email')
    if email and email in DEMO_CLIENTS:
        client = DEMO_CLIENTS[email].copy()
        client['email'] = email
        return client
    return None


# ---------------------------------------------------------------------------
# Mock data generators (pull from real modules in production)
# ---------------------------------------------------------------------------

def get_kpi_data():
    return {
        'sync_health': 'Healthy',
        'sync_streak': 14,
        'missing_receipts': 3,
        'receipt_trend': 'down',
        'receipt_change': '-5',
        'srm_variance': '$12.40',
        'next_filing_type': 'QST Q1',
        'next_filing_date': 'Apr 30',
    }


def get_alerts():
    return [
        {'level': 'warning', 'title': '2 missing receipts detected for March 18-20', 'time': '2 hours ago'},
        {'level': 'info', 'title': 'QBO sync completed successfully', 'time': '8 hours ago'},
        {'level': 'info', 'title': 'Uber Eats payout reconciled: $2,341.50', 'time': '1 day ago'},
        {'level': 'critical', 'title': 'SRM variance exceeded $50 threshold on March 15', 'time': '3 days ago'},
    ]


def get_integrations():
    return [
        {'name': 'QuickBooks Online', 'status': 'Connected', 'badge': 'success', 'last_sync': 'Today 8:00 AM'},
        {'name': 'Lightspeed Restaurant', 'status': 'Connected', 'badge': 'success', 'last_sync': 'Today 8:00 AM'},
        {'name': 'Wagepoint', 'status': 'Connected', 'badge': 'success', 'last_sync': 'Mar 15'},
        {'name': 'Dext', 'status': 'Connected', 'badge': 'success', 'last_sync': 'Today 7:30 AM'},
        {'name': 'Uber Eats', 'status': 'Token Expiring', 'badge': 'warning', 'last_sync': 'Mar 20'},
        {'name': 'DoorDash (Email)', 'status': 'Active', 'badge': 'success', 'last_sync': 'Mar 19'},
    ]


def get_deadlines():
    return [
        {'name': 'GST/HST Return', 'period': 'Q1 2026', 'due': 'Apr 30, 2026', 'status': 'In Progress', 'badge': 'info'},
        {'name': 'QST Return', 'period': 'Q1 2026', 'due': 'Apr 30, 2026', 'status': 'In Progress', 'badge': 'info'},
        {'name': 'Payroll Remittance', 'period': 'March 2026', 'due': 'Apr 15, 2026', 'status': 'Pending', 'badge': 'warning'},
        {'name': 'T4/RL-1 Slips', 'period': 'FY 2025', 'due': 'Feb 28, 2026', 'status': 'Filed', 'badge': 'success'},
        {'name': 'T2 Corporate Return', 'period': 'FY 2025', 'due': 'Jun 30, 2026', 'status': 'Not Started', 'badge': 'warning'},
    ]


def get_reconciliation():
    return {
        'month': 'February 2026',
        'checks': [
            {'name': 'SRM vs POS Revenue', 'result': 'Pass', 'badge': 'success', 'details': 'Variance: $8.20 (within $50 tolerance)'},
            {'name': 'GST Collected vs Filed', 'result': 'Pass', 'badge': 'success', 'details': '$4,231.50 collected, $4,228.90 filed'},
            {'name': 'QST Collected vs Filed', 'result': 'Pass', 'badge': 'success', 'details': '$8,452.10 collected, $8,449.30 filed'},
            {'name': 'Bank vs Dext Receipts', 'result': 'Warning', 'badge': 'warning', 'details': '3 unmatched transactions totalling $245.80'},
            {'name': 'Tip Declaration Rate', 'result': 'Pass', 'badge': 'success', 'details': '9.2% declared (above 8% minimum)'},
            {'name': 'Delivery Payout Match', 'result': 'Pass', 'badge': 'success', 'details': 'All 3 platforms reconciled'},
        ],
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        client = DEMO_CLIENTS.get(email)
        if client and client['password_hash'] == password_hash:
            session['email'] = email
            session.permanent = bool(request.form.get('remember'))
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html', error=None)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))


@app.route('/dashboard')
@login_required
def dashboard():
    client = get_current_client()
    today = datetime.now().strftime('%A, %B %d, %Y')

    return render_template(
        'dashboard.html',
        client=client,
        today=today,
        kpi=get_kpi_data(),
        alerts=get_alerts(),
        integrations=get_integrations(),
        deadlines=get_deadlines(),
        recon=get_reconciliation(),
    )


# Sub-pages (placeholder routes — extend as needed)
@app.route('/dashboard/sync')
@login_required
def sync_status():
    return redirect(url_for('dashboard'))


@app.route('/dashboard/receipts')
@login_required
def receipts():
    return redirect(url_for('dashboard'))


@app.route('/dashboard/filings')
@login_required
def filings():
    return redirect(url_for('dashboard'))


@app.route('/dashboard/delivery')
@login_required
def delivery():
    return redirect(url_for('dashboard'))


@app.route('/dashboard/tips')
@login_required
def tips():
    return redirect(url_for('dashboard'))


@app.route('/dashboard/settings')
@login_required
def settings():
    return redirect(url_for('dashboard'))


# ---------------------------------------------------------------------------
# API endpoints (for future AJAX/SPA use)
# ---------------------------------------------------------------------------

@app.route('/api/status')
@login_required
def api_status():
    return jsonify({
        'kpi': get_kpi_data(),
        'integrations': get_integrations(),
    })


@app.route('/api/alerts')
@login_required
def api_alerts():
    return jsonify({'alerts': get_alerts()})


@app.route('/api/deadlines')
@login_required
def api_deadlines():
    return jsonify({'deadlines': get_deadlines()})


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    print(f'\n  RestoTax running at http://localhost:{port}\n')
    print(f'  Demo login: demo@giwa.ca / demo123\n')
    app.run(host='0.0.0.0', port=port, debug=debug)
