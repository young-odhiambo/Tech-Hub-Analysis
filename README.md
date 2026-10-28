# Sales Analytics Without Pandas

A pure-Python analysis of September 2026 electronics sales across five Kenyan retail stores. Built for **Day 2 of the Squad Python Specialization (Data Science, AI & Analytics)**.

Tasks 1-7 use only the Python standard library (`csv`, `pathlib`). `pandas` is used only in Task 8 to independently verify the results.

## What it does

The script reads a messy sales CSV, cleans it, and produces a sales report covering:

| Task | Description |
|------|-------------|
| 1 | Read the CSV with `csv.DictReader` |
| 2 | Clean numeric fields; skip and log untrustworthy rows |
| 3 | Compute total revenue |
| 4 | Revenue breakdown by product, store, and payment method |
| 5 | Top 3 products by revenue |
| 6 | High-value transactions (>= KES 50,000) and counts per store |
| 7 | Mean, median, min, and max transaction revenue (hand-written) |
| 8 | Cross-check headline numbers against pandas |

## Project structure

```
.
├── data/
│   └── electronics_sales.csv   # Input data (50 rows)
├── sales_analysis.ipynb        # Notebook with all tasks
|__output
|      |__sales_report.txt
└── README.md
```

## Requirements

- Python 3.10+ (uses `float | None` and `list[dict]` type syntax)
- `pandas` and `numpy` (only needed for the Task 8 verification)


## Usage

1. Place `electronics_sales.csv` in a `data/` folder next to the notebook.
2. Open `sales_analysis.ipynb` in Jupyter and run all cells, **or** export the final `main()` logic to a `.py` script and run:


The final cell calls `main()`, which prints the full report.

## Input data

Columns in `electronics_sales.csv`:

`sale_id`, `sale_date`, `store`, `product`, `quantity`, `unit_price_kes`, `payment_method`

The data is deliberately dirty. Examples handled by `parse_number`:

- Thousands separators: `38,999` -> `38999.0`
- Currency prefixes: `KES 18999` -> `18999.0`
- Placeholders and blanks: `N/A`, `""` -> `None`
- Words instead of numbers: `two` -> `None`

## Key functions

- `read_sales(path)` - reads raw rows as dictionaries of strings.
- `parse_number(value)` - converts a messy string to `float`, or `None` if it cannot be trusted.
- `convert_rows(rows)` - returns `(clean_rows, skipped_rows)`; each skipped row records its `sale_id` and the reason.
- `row_revenue(row)` / `total_revenue(rows)` - quantity x unit price, and their sum.
- `revenue_by(rows, field)` - groups revenue by any column using a plain dict.
- `top_n(totals, n)` - highest `n` entries; ties broken alphabetically.
- `high_value(rows, threshold)` - transactions at or above the threshold.
- `mean`, `median`, `minimum_maximum` - statistics written from scratch.
- `verify_with_pandas(path, my_results)` - prints MATCH or MISMATCH per metric.

## Data quality

Of 50 rows, **46 were used** and **4 were skipped**:

| Sale ID | Reason |
|---------|--------|
| S-3006 | Quantity is `'two'` |
| S-3030 | Unit price is `'N/A'` |
| S-3035 | Quantity is empty |
| S-3039 | Unit price is empty |

Skipped rows are excluded from all totals rather than guessed at, so the figures below are a lower bound on true revenue.

## Results (September 2026)

- **Total revenue:** KES 1,310,812.00
- **Top 3 products:** HP 15 Laptop (KES 389,994), Hisense 43in Smart TV (KES 272,993), Lenovo Tab M10 (KES 199,992)
- **Top store:** Kisumu Mega Plaza (KES 449,678)
- **Top payment method:** M-Pesa (KES 738,568)
- **High-value transactions (>= KES 50,000):** 5
- **Transaction revenue:** mean KES 28,495.91, median KES 11,097.00, min KES 1,499.00, max KES 259,996.00

The mean is much higher than the median because a few large laptop and TV sales pull it up.

## Verification

Task 8 re-reads the CSV with pandas, applies equivalent cleaning, and compares total revenue, revenue by product, top 3 products, and mean/median. All four checks report **MATCH**.

## Notes

- Revenue is computed per row as `quantity * unit_price_kes`.
- `DATA_PATH` and `THRESHOLD` are constants near the top of the relevant cells, so they are easy to change.
- `parse_number` strips `SH` as a substring, which is fine for this dataset but could affect text containing those letters elsewhere.
