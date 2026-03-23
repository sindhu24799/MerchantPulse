"""
Parser module for MerchantPulse.
Reads CSV files, cleans data, and returns structured dictionaries.
"""

import csv
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


def parse_orders(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse orders CSV file.
    Expected columns: order_id, date, product, qty, price, customer_ip (optional)
    
    Returns list of order dictionaries with cleaned/normalized data.
    """
    orders = []
    
    if not filepath.exists():
        return orders
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                order = {
                    'order_id': row.get('order_id', '').strip(),
                    'date': parse_date(row.get('date', '')),
                    'product': row.get('product', '').strip(),
                    'qty': int(row.get('qty', 0) or 0),
                    'price': float(row.get('price', 0) or 0),
                    'customer_ip': row.get('customer_ip', '').strip(),
                }
                # Calculate line total
                order['total'] = order['qty'] * order['price']
                
                # Only include valid orders
                if order['order_id'] and order['date'] and order['product']:
                    orders.append(order)
            except (ValueError, TypeError):
                # Skip malformed rows
                continue
    
    return orders


def parse_inventory(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse inventory CSV file.
    Expected columns: product, size, stock_level, reorder_point
    
    Returns list of inventory dictionaries with cleaned data.
    """
    inventory = []
    
    if not filepath.exists():
        return inventory
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                item = {
                    'product': row.get('product', '').strip(),
                    'size': row.get('size', '').strip(),
                    'stock_level': int(row.get('stock_level', 0) or 0),
                    'reorder_point': int(row.get('reorder_point', 10) or 10),
                }
                
                if item['product']:
                    inventory.append(item)
            except (ValueError, TypeError):
                continue
    
    return inventory


def parse_products(filepath: Path) -> List[Dict[str, Any]]:
    """
    Parse products CSV file (if available).
    Expected columns: product_name, category, price, cost
    
    Returns list of product dictionaries.
    """
    products = []
    
    if not filepath.exists():
        return products
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                product = {
                    'name': row.get('product_name', row.get('name', '')).strip(),
                    'category': row.get('category', '').strip(),
                    'price': float(row.get('price', 0) or 0),
                    'cost': float(row.get('cost', 0) or 0),
                }
                
                if product['name']:
                    products.append(product)
            except (ValueError, TypeError):
                continue
    
    return products


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats.
    Supports: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, ISO format
    """
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%m-%d-%Y',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def load_data(data_dir: Path, target_date: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Load all CSV files from the data directory.
    
    Args:
        data_dir: Path to the data directory
        target_date: Optional date to filter orders (if None, loads all)
    
    Returns:
        Dictionary with 'orders', 'inventory', 'products' keys
    """
    orders_file = data_dir / 'orders.csv'
    inventory_file = data_dir / 'inventory.csv'
    products_file = data_dir / 'products.csv'
    
    all_orders = parse_orders(orders_file)
    
    # Filter by target date if specified
    if target_date:
        orders = [
            o for o in all_orders 
            if o['date'] and o['date'].date() == target_date.date()
        ]
    else:
        orders = all_orders
    
    return {
        'orders': orders,
        'all_orders': all_orders,  # Keep all orders for historical comparison
        'inventory': parse_inventory(inventory_file),
        'products': parse_products(products_file),
    }


def load_historical_data(data_dir: Path, days_back: int = 7) -> Dict[datetime, List[Dict]]:
    """
    Load historical order data from the history folder.
    Groups orders by date for comparison.
    
    Args:
        data_dir: Path to the data directory
        days_back: Number of days to look back
    
    Returns:
        Dictionary mapping dates to list of orders for that date
    """
    history_dir = data_dir / 'history'
    historical = {}
    
    # Also include current data folder orders
    all_orders = parse_orders(data_dir / 'orders.csv')
    
    for order in all_orders:
        if order['date']:
            date_key = order['date'].date()
            if date_key not in historical:
                historical[date_key] = []
            historical[date_key].append(order)
    
    # Load from history subfolder
    if history_dir.exists():
        for csv_file in history_dir.glob('*.csv'):
            orders = parse_orders(csv_file)
            for order in orders:
                if order['date']:
                    date_key = order['date'].date()
                    if date_key not in historical:
                        historical[date_key] = []
                    historical[date_key].append(order)
    
    return historical
