#!/usr/bin/env python3
"""
MerchantPulse Web Application
Flask-based web interface for generating store reports from CSV uploads.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

from parser import load_data, load_historical_data
from analyzer import analyze_day
from reporter import generate_terminal_report, format_currency

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

# Temporary directory for uploads
UPLOAD_FOLDER = tempfile.mkdtemp(prefix='merchantpulse_')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with file upload form."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle CSV file uploads."""
    # Check if files were uploaded
    if 'orders' not in request.files and 'inventory' not in request.files:
        flash('⚠️ Please upload at least one CSV file (orders.csv or inventory.csv)')
        return redirect(url_for('index'))

    # Create session folder
    session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_folder = Path(app.config['UPLOAD_FOLDER']) / session_id
    session_folder.mkdir(parents=True, exist_ok=True)

    orders_uploaded = False
    inventory_uploaded = False

    # Handle orders.csv
    if 'orders' in request.files:
        orders_file = request.files['orders']
        if orders_file and orders_file.filename and allowed_file(orders_file.filename):
            filename = secure_filename('orders.csv')
            orders_file.save(session_folder / filename)
            orders_uploaded = True
        elif orders_file.filename:
            flash('⚠️ Invalid orders file. Please upload a .csv file.')

    # Handle inventory.csv
    if 'inventory' in request.files:
        inventory_file = request.files['inventory']
        if inventory_file and inventory_file.filename and allowed_file(inventory_file.filename):
            filename = secure_filename('inventory.csv')
            inventory_file.save(session_folder / filename)
            inventory_uploaded = True
        elif inventory_file.filename:
            flash('⚠️ Invalid inventory file. Please upload a .csv file.')

    if not orders_uploaded and not inventory_uploaded:
        flash('⚠️ No valid CSV files uploaded.')
        return redirect(url_for('index'))

    # Store session info
    session_data = {
        'folder': str(session_folder),
        'orders': orders_uploaded,
        'inventory': inventory_uploaded,
    }

    # Redirect to date selection with session data
    return redirect(url_for('select_date', session_id=session_id))


@app.route('/select_date/<session_id>')
def select_date(session_id):
    """Date selection page."""
    session_folder = Path(app.config['UPLOAD_FOLDER']) / session_id

    if not session_folder.exists():
        flash('⚠️ Session expired. Please upload files again.')
        return redirect(url_for('index'))

    # Load data to get available dates
    data = load_data(session_folder)
    all_orders = data.get('all_orders', [])

    # Get unique dates from orders
    available_dates = set()
    for order in all_orders:
        if order.get('date'):
            available_dates.add(order['date'].strftime('%Y-%m-%d'))

    available_dates = sorted(list(available_dates), reverse=True)

    return render_template('select_date.html',
                         session_id=session_id,
                         available_dates=available_dates,
                         has_orders=data.get('orders', []),
                         has_inventory=data.get('inventory', []))


@app.route('/report/<session_id>')
def report(session_id):
    """Generate and display report."""
    session_folder = Path(app.config['UPLOAD_FOLDER']) / session_id

    if not session_folder.exists():
        flash('⚠️ Session expired. Please upload files again.')
        return redirect(url_for('index'))

    # Get selected date
    date_str = request.args.get('date')
    if not date_str:
        flash('⚠️ Please select a date.')
        return redirect(url_for('select_date', session_id=session_id))

    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        flash('⚠️ Invalid date format.')
        return redirect(url_for('select_date', session_id=session_id))

    # Load and analyze data
    data = load_data(session_folder, target_date)
    historical_data = load_historical_data(session_folder)

    orders = data.get('orders', [])
    inventory = data.get('inventory', [])

    if not orders:
        flash(f'⚠️ No orders found for {date_str}')
        return redirect(url_for('select_date', session_id=session_id))

    # Run analysis
    analysis = analyze_day(orders, inventory, historical_data, target_date)

    # Format data for template
    revenue = analysis['revenue_summary']
    top_products = analysis['top_products']
    inventory_alerts = analysis['inventory_alerts']
    anomalies = analysis['anomalies']
    recommendations = analysis['recommendations']

    return render_template('report.html',
                         analysis=analysis,
                         revenue=revenue,
                         top_products=top_products,
                         inventory_alerts=inventory_alerts,
                         anomalies=anomalies,
                         recommendations=recommendations,
                         format_currency=format_currency,
                         session_id=session_id)


@app.route('/cleanup/<session_id>')
def cleanup(session_id):
    """Clean up session files."""
    session_folder = Path(app.config['UPLOAD_FOLDER']) / session_id
    if session_folder.exists():
        import shutil
        shutil.rmtree(session_folder)
    flash('✅ Session cleaned up.')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("🚀 Starting MerchantPulse Web Application...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print("🌐 Open http://localhost:5000 in your browser")
    print()
    app.run(debug=True, host='0.0.0.0', port=5000)
