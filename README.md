# MerchantPulse

**Automated Daily Store Report Generator**

Drop in your store's CSV exports. Get a clean, actionable daily report in seconds.

---

## The Real Problem It Solves

Small Shopify merchants export their orders, products, and inventory data as CSVs manually. Then they spend 30–45 minutes every morning copying numbers into a spreadsheet to understand how their store performed yesterday. 

MerchantPulse automates this entire process.

---

## Quick Start

```bash
# Generate report for today
python pulse.py

# Generate report for a specific date
python pulse.py --date 2024-03-21

# Generate report for yesterday
python pulse.py --yesterday

# Use a custom data directory
python pulse.py --data-dir ./my-exports
```

---

## Sample Output

```
====================================================
  MerchantPulse — Daily Report  21 Mar 2024
====================================================

REVENUE SUMMARY
  Total Orders     :  47
  Gross Revenue    :  ₹1,24,830
  Avg Order Value  :  ₹2,656
  vs Yesterday     :  +12.4%  ▲

TOP 5 PRODUCTS TODAY
  1. White Sneakers      — 18 units  — ₹32,400
  2. Black Hoodie        — 12 units  — ₹21,600
  3. Sports Socks (3pk)  —  9 units  — ₹4,050
  4. Slim Fit Jeans      —  7 units  — ₹19,600
  5. Cap — Olive Green   —  6 units  — ₹5,400

INVENTORY ALERTS
  🔴 White Sneakers (sz 9)  — 3 units left  — reorder now
  🟡 Black Hoodie (M)       — 8 units left  — reorder soon
  🟢 Slim Fit Jeans         — 42 units      — healthy

ANOMALIES DETECTED
  ⚡ Order #1082 — ₹18,400 — unusually high value (3.2x avg)
  ⚡ 6 orders from same IP — possible bulk/fraud pattern

RECOMMENDED ACTION
  → Bundle White Sneakers + Sports Socks (bought together 14x today)
  → Reorder White Sneakers sz 9 before tomorrow
====================================================
```

---

## File Structure

```
merchant-pulse/
│
├── data/
│   ├── orders.csv        # Your order exports
│   ├── inventory.csv     # Your inventory data
│   └── history/          # Previous days' CSVs for comparison
│
├── parser.py             # CSV reading and data cleaning
├── analyzer.py           # Business logic (rankings, alerts, anomalies)
├── reporter.py           # Terminal output + HTML generation
├── pulse.py              # Entry point CLI
└── README.md
```

---

## CSV File Formats

### orders.csv

| Column | Description | Example |
|--------|-------------|---------|
| `order_id` | Unique order identifier | `ORD-1001` |
| `date` | Order date (YYYY-MM-DD) | `2024-03-21` |
| `product` | Product name | `White Sneakers` |
| `qty` | Quantity ordered | `2` |
| `price` | Unit price | `1800` |
| `customer_ip` | Customer IP (optional, for fraud detection) | `192.168.1.1` |

```csv
order_id,date,product,qty,price,customer_ip
ORD-1001,2024-03-21,White Sneakers,2,1800,192.168.1.100
ORD-1002,2024-03-21,Black Hoodie,1,1800,192.168.1.101
ORD-1003,2024-03-21,Sports Socks (3pk),3,450,192.168.1.102
```

### inventory.csv

| Column | Description | Example |
|--------|-------------|---------|
| `product` | Product name | `White Sneakers` |
| `size` | Size/variant | `9` |
| `stock_level` | Current stock | `15` |
| `reorder_point` | Reorder when below this | `10` |

```csv
product,size,stock_level,reorder_point
White Sneakers,9,8,15
White Sneakers,10,25,15
Black Hoodie,M,12,20
Black Hoodie,L,35,20
```

---

## Features

### Revenue Summary
- Total orders count
- Gross revenue
- Average order value
- Comparison with yesterday (percentage change)

### Top Products
- Top 5 products by revenue
- Units sold and total revenue per product

### Inventory Alerts
- 🟴 **Red**: Critical stock (≤50% of reorder point)
- 🟡 **Yellow**: Low stock (≤ reorder point)
- 🟢 **Green**: Healthy stock levels

### Anomaly Detection
- **High-value orders**: Orders >2 standard deviations from mean
- **Bulk/fraud patterns**: Multiple orders from same IP

### Bundle Recommendations
- Products frequently bought together
- Based on co-occurrence frequency analysis

---

## Command Line Options

```
usage: pulse.py [-h] [--date DATE] [--data-dir DATA_DIR] [--output OUTPUT]
                [--yesterday] [--verbose]

MerchantPulse — Generate daily store reports from CSV exports

options:
  -h, --help            Show this help message and exit
  --date, -d DATE       Report date in YYYY-MM-DD format (default: today)
  --data-dir, -D PATH   Path to data directory (default: ./data)
  --output, -o PATH     Output path for HTML report
  --yesterday, -y       Generate report for yesterday
  --verbose, -v         Show verbose output
```

---

## Technical Highlights

| Feature | Implementation |
|---------|----------------|
| Revenue comparison | HashMap of date → aggregated totals |
| Top 5 products | Sorted frequency map |
| Inventory alerts | Threshold comparison + priority sorting |
| Anomaly detection | Statistical mean + standard deviation |
| Bundle recommendations | Co-occurrence frequency map |
| HTML report | Python string templating |

---

## Why It's Useful

1. **Save Time**: No more manual spreadsheet work every morning
2. **Actionable Insights**: Get clear recommendations, not just numbers
3. **Catch Issues**: Inventory alerts and anomaly detection
4. **Beautiful Reports**: Professional HTML reports you can share
5. **Simple Setup**: Just drop CSVs in a folder and run

---

## License

MIT License - Feel free to use and modify for your store.
