#!/usr/bin/env python3
"""
MerchantPulse — Automated Daily Store Report Generator

Drop in your store's CSV exports. Get a clean, actionable daily report in seconds.

Usage:
    python pulse.py --date 2024-03-21
    python pulse.py --date 2024-03-21 --data-dir ./my-data
    python pulse.py  # Uses today's date by default
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from parser import load_data, load_historical_data
from analyzer import analyze_day
from reporter import print_report


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='MerchantPulse — Generate daily store reports from CSV exports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pulse.py                          # Generate report for today
  python pulse.py --date 2024-03-21        # Generate report for specific date
  python pulse.py --data-dir ./exports     # Use custom data directory
  python pulse.py --output ./reports       # Save HTML to custom location

CSV File Formats:
  orders.csv:     order_id, date, product, qty, price, customer_ip (optional)
  inventory.csv:  product, size, stock_level, reorder_point
        """
    )
    
    parser.add_argument(
        '--date', '-d',
        type=str,
        default=None,
        help='Report date in YYYY-MM-DD format (default: today)'
    )
    
    parser.add_argument(
        '--data-dir', '-D',
        type=Path,
        default=None,
        help='Path to data directory containing CSV files (default: ./data)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output path for HTML report (default: ./reports/report_YYYY-MM-DD.html)'
    )
    
    parser.add_argument(
        '--yesterday', '-y',
        action='store_true',
        help='Generate report for yesterday'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )
    
    return parser.parse_args()


def get_target_date(date_str: str | None, yesterday: bool) -> datetime:
    """Determine the target date for the report."""
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD format.")
            sys.exit(1)
    
    if yesterday:
        return datetime.now() - timedelta(days=1)
    
    return datetime.now()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Determine target date
    target_date = get_target_date(args.date, args.yesterday)
    
    # Determine data directory
    data_dir = args.data_dir
    if data_dir is None:
        # Check for data directory in current location
        data_dir = Path('./data')
        if not data_dir.exists():
            # Try relative to script location
            script_dir = Path(__file__).parent
            data_dir = script_dir / 'data'
    
    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        print("Please create a 'data' folder and add your CSV files.")
        sys.exit(1)
    
    # Determine output path
    output_path = args.output
    if output_path is None:
        reports_dir = Path('./reports')
        reports_dir.mkdir(exist_ok=True)
        output_path = reports_dir / f"report_{target_date.strftime('%Y-%m-%d')}.html"
    
    if args.verbose:
        print(f"📊 MerchantPulse Report Generator")
        print(f"   Target Date: {target_date.strftime('%Y-%m-%d')}")
        print(f"   Data Directory: {data_dir}")
        print(f"   Output: {output_path}")
        print()
    
    # Load data
    if args.verbose:
        print("Loading data...")
    
    data = load_data(data_dir, target_date)
    historical_data = load_historical_data(data_dir)
    
    orders = data['orders']
    inventory = data['inventory']
    
    if not orders:
        print(f"⚠️  No orders found for {target_date.strftime('%Y-%m-%d')}")
        print("   Check your orders.csv file and date format.")
        sys.exit(0)
    
    if args.verbose:
        print(f"   Found {len(orders)} orders")
        print(f"   Found {len(inventory)} inventory items")
        print()
    
    # Analyze data
    if args.verbose:
        print("Analyzing data...")
    
    analysis = analyze_day(orders, inventory, historical_data, target_date)
    
    # Generate and print report
    print()
    print_report(analysis, output_path)
    print()
    
    if args.verbose:
        print("✅ Report generation complete!")


if __name__ == '__main__':
    main()
