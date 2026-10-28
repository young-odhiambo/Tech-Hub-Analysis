"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
from pathlib import Path
import pandas as pd
import numpy as np

DATA_PATH = Path("data") / "electronics_sales.csv"


def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    # """Read the CSV with the csv module and return the raw rows."""
    with open(path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    print(f"Number of rows found: {len(rows)}")
    print(f"Column names found: {reader.fieldnames}")

    return rows
    # raise NotImplementedError
read_sales(DATA_PATH)


def parse_number(value: str) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted."""
    if value is None:
        return None

    # Clean up whitespace and common non-numeric fluff
    cleaned = value.strip().upper()

    # Drop currency signs and abbreviations (e.g., 'KES', 'KSH', '$')
    cleaned = (
        cleaned.replace("KES", "")
        .replace("KSH", "")
        .replace("SH", "")
        .replace("$", "")
        .strip()
    )

    # Remove commas used as thousands separators (e.g., "1,200.50" -> "1200.50")
    cleaned = cleaned.replace(",", "")

    # Handle explicit placeholders or empty fields
    if cleaned in ("", "N/A", "NONE", "NULL", "-"):
        return None

    try:
        return float(cleaned)
    except ValueError:
        # String contains untrustworthy characters (e.g., "twelve", "120A")
        return None


print(parse_number("  KES 1,200.50  "))  # Should return 1200.50
print(parse_number("N/A"))  # Should return None

def convert_rows(
    rows: list[dict[str, str]]
) -> tuple[list[dict], list[dict[str, str]]]:
    """Convert quantity and unit_price_kes in valid rows; log reasons for skipped rows."""
    converted_rows = []
    skipped_rows = []

    for idx, row in enumerate(rows):
        # Read target columns
        raw_qty = row.get("quantity")
        raw_price = row.get("unit_price_kes")

        qty = parse_number(raw_qty)
        price = parse_number(raw_price)

        # Validation checks
        if qty is None:
            skipped_rows.append(
                {
                    "row_index": idx,
                    "sale_id": row.get("sale_id", "Unknown"),
                    "reason": f"Invalid or missing 'quantity' value: {repr(raw_qty)}",
                }
            )
            continue

        if price is None:
            skipped_rows.append(
                {
                    "row_index": idx,
                    "sale_id": row.get("sale_id", "Unknown"),
                    "reason": f"Invalid or missing 'unit_price_kes' value: {repr(raw_price)}",
                }
            )
            continue

        # Prevent illogical values like negative numbers
        if qty < 0 or price < 0:
            skipped_rows.append(
                {
                    "row_index": idx,
                    "sale_id": row.get("sale_id", "Unknown"),
                    "reason": f"Negative numeric values are not allowed (qty: {qty}, price: {price})",
                }
            )
            continue

        # Build converted record
        new_row = row.copy()
        new_row["quantity"] = int(qty)  # Quantities should be integers
        new_row["unit_price_kes"] = price
        converted_rows.append(new_row)

    return converted_rows, skipped_rows

convert_rows(read_sales(DATA_PATH))

def row_revenue(row: dict) -> float:
    """Revenue of one sale = quantity x unit price."""
    return row["quantity"] * row["unit_price_kes"]
 
 
def total_revenue(rows: list[dict]) -> float:
    """Sum of quantity x unit_price_kes over all rows."""
    total = 0.0
    for row in rows:
        total += row_revenue(row)
    return total


def format_kes(amount: float) -> str:
    """Format as 'KES """
    return f"KES {amount:,.2f}"


def report_total_revenue(path=DATA_PATH) -> float:
    """Read, clean, add up revenue, print the result and return the total."""
    rows = read_sales(path)                          # raw rows (strings)
    clean_rows, skipped_rows = convert_rows(rows)    # numeric rows + skipped list

    print(f"Rows read   : {len(rows)}")
    print(f"Rows used   : {len(clean_rows)}")
    print(f"Rows skipped: {len(skipped_rows)}")
    

    total = total_revenue(clean_rows)
    print("Total revenue:", format_kes(total))
    return total


total = report_total_revenue()


def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals = {}                              # plain dict, no defaultdict or Counter
    for row in rows:
        key = row[field]                     # e.g. the product name
        if key in totals:
            totals[key] += row_revenue(row)  # seen before: add to its total
        else:
            totals[key] = row_revenue(row)   # first time: create the entry
    return totals

    
def print_breakdown(title: str, totals: dict[str, float]) -> None:
    """Print a revenue dict sorted highest first (ties broken A-Z)."""
    print(f"\n{title}")
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    for name, amount in ranked:
        print(f"  {name:<24} {format_kes(amount):>18}")


# Uses clean_rows from convert_rows
rows = read_sales(DATA_PATH)
clean_rows, skipped_rows = convert_rows(rows)

by_product = revenue_by(clean_rows, "product")
by_store = revenue_by(clean_rows, "store")
by_payment = revenue_by(clean_rows, "payment_method")

print_breakdown("Revenue by product (KES)", by_product)
print_breakdown("Revenue by store (KES)", by_store)
print_breakdown("Revenue by payment method (KES)", by_payment)

def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first.
    Ties on revenue are broken alphabetically (A-Z) by product name.
    """
    if n < 0:
        raise ValueError("n must not be negative")
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]


top3 = top_n(by_product, 3)

print("Top 3 products")
for position, (product, amount) in enumerate(top3, start=1):
    print(f"  {position}. {product} - {format_kes(amount)}")


THRESHOLD = 50000

def high_value(rows: list[dict], threshold: float) -> list[dict]:
    """Transactions whose revenue is at or above threshold."""
    return [row for row in rows if row_revenue(row) >= threshold]


big_sales = high_value(clean_rows, THRESHOLD)


# Dict comprehension: store -> number of high-value sales
stores = sorted({row["store"] for row in clean_rows})
big_per_store = {
    store: len([r for r in big_sales if r["store"] == store])
    for store in stores
}

# printing big_sales
print(f"High-value transactions (>= {format_kes(THRESHOLD)}): {len(big_sales)}")
for r in big_sales:
    print(f"  {r['sale_id']}  {r['sale_date']}  {r['store']:<18} "
          f"{r['product']:<22} {format_kes(row_revenue(r))}")

print("\nHigh-value sales per store")
for store, count in big_per_store.items():
    print(f"  {store:<20} transaction ({count})")


def mean(values: list[float]) -> float:
    """Average of the values."""

    if not values:
        raise ValueError("mean() needs at least one value, got an empty list")

    total = 0.0
    for v in values:
        total += v
    return total / len(values)

def median(values: list[float]) -> float:

    if not values:
        raise ValueError("median() needs at least one value, got an empty list")
    ordered = sorted(values)
    n = len(ordered)          # sorted() returns a copy, the input is untouched
    mid = n // 2
    if n % 2 == 1:         # odd count: one middle value
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2   # even count: average the middle two


def minimum_maximum(values: list[float]) -> tuple[float, float]:

    if not values:
        raise ValueError("minimum_maximum() needs at least one value, got an empty list")
    lowest = highest = values[0]      # start with the first value as both
    for v in values[1:]:
        if v < lowest:
            lowest = v
        if v > highest:
            highest = v
    return lowest, highest


# Apply to per-transaction revenue
revenues = [row_revenue(row) for row in clean_rows]
low, high = minimum_maximum(revenues)

print("Transaction revenue statistics")
print(f"  revenue_mean   : {format_kes(mean(revenues))}")
print(f"  revenue_median : {format_kes(median(revenues))}")
print(f"  revenue_min    : {format_kes(low)}")
print(f"  revenue_max    : {format_kes(high)}")


import math

def verify_with_pandas(path, my_results: dict) -> None:
    """Recompute the headline numbers with pandas and print MATCH or MISMATCH."""

    # 1. Read everything as text, so pandas doesn't guess anything
    df = pd.read_csv(path, dtype=str)

    # 2. Clean the two number columns (same rules as parse_number)
    for col in ["quantity", "unit_price_kes"]:
        df[col] = (
            df[col]
            .str.replace("KES", "", regex=False)   # remove the currency label
            .str.replace(",", "", regex=False)     # remove thousands commas
            .str.strip()                           # remove spaces
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")   # "two", "N/A", "" become NaN

    # 3. Drop rows with a missing quantity or price (same as skipped rows)
    df = df.dropna(subset=["quantity", "unit_price_kes"])

    # 4. Revenue per sale
    df["revenue"] = df["quantity"] * df["unit_price_kes"]

    # 5. Compare each number
    def same(a, b):
        return math.isclose(a, b, abs_tol=0.01)   # allow tiny rounding differences

    # Total revenue
    pandas_total = df["revenue"].sum()
    ok = same(my_results["total"], pandas_total)
    print("Total revenue      :", "MATCH" if ok else f"MISMATCH (pure={my_results['total']}, pandas={pandas_total})")

    # Revenue by product
    pandas_by_product = df.groupby("product")["revenue"].sum().to_dict()
    ok = all(same(my_results["by_product"][p], pandas_by_product[p]) for p in pandas_by_product) \
         and len(my_results["by_product"]) == len(pandas_by_product)
    print("Revenue by product :", "MATCH" if ok else "MISMATCH")

    # Top 3 products (revenue high to low, then name A-Z)
    pandas_top3 = (
        df.groupby("product")["revenue"].sum()
        .reset_index()
        .sort_values(["revenue", "product"], ascending=[False, True])
        .head(3)
    )
    pandas_top3 = list(zip(pandas_top3["product"], pandas_top3["revenue"]))
    ok = [p for p, _ in my_results["top3"]] == [p for p, _ in pandas_top3]
    print("Top 3              :", "MATCH" if ok else f"MISMATCH (pure={my_results['top3']}, pandas={pandas_top3})")

    # Mean and median
    ok = same(my_results["mean"], df["revenue"].mean()) and same(my_results["median"], df["revenue"].median())
    print("Mean / median      :", "MATCH" if ok else "MISMATCH")


# ---- Collect my own results, then verify ----
rows = read_sales(DATA_PATH)
clean_rows, skipped_rows = convert_rows(rows)
revenues = [row_revenue(r) for r in clean_rows]
by_product = revenue_by(clean_rows, "product")

my_results = {
    "total": total_revenue(clean_rows),
    "by_product": by_product,
    "top3": top_n(by_product, 3),
    "mean": mean(revenues),
    "median": median(revenues),
}

print("\n=== pandas verification ===")
verify_with_pandas(DATA_PATH, my_results)

def main() -> None:
    # Task 1-2: read and convert
    raw_rows = read_sales(DATA_PATH)
    clean_rows, skipped_rows = convert_rows(raw_rows)

    print("\n=== Sales report: September 2026 ===")
    print(f"Rows read          : {len(raw_rows)}")
    print(f"Rows used          : {len(clean_rows)}")
    reasons = ", ".join(f"{s['sale_id']}: {s['reason']}" for s in skipped_rows)
    print(f"Rows skipped       : {len(skipped_rows)}   ({reasons})")

    # Task 3: total revenue
    total = total_revenue(clean_rows)
    print(f"\nTotal revenue (KES): {total:,.2f}")

    # Task 4: revenue by product, highest first
    by_product = revenue_by(clean_rows, "product")
    print("\nRevenue by product (KES)")
    for product, amount in top_n(by_product, len(by_product)):
        print(f"  {product:<24} {amount:>14,.2f}")

    # Store and payment method breakdowns
    for title, field in [("store", "store"), ("payment method", "payment_method")]:
        print(f"\nRevenue by {title} (KES)")
        totals = revenue_by(clean_rows, field)
        for name, amount in top_n(totals, len(totals)):
            print(f"  {name:<24} {amount:>14,.2f}")

    # Task 5: top 3 products
    top3 = top_n(by_product, 3)
    print("\nTop 3 products")
    for position, (product, amount) in enumerate(top3, start=1):
        print(f"  {position}. {product} - KES {amount:,.2f}")

    # Task 6: high-value transactions
    big_sales = high_value(clean_rows, THRESHOLD)
    print(f"\nHigh-value transactions (>= KES {THRESHOLD:,.2f}): {len(big_sales)}")
    for r in big_sales:
        print(f"  {r['sale_id']}  {r['sale_date']}  {r['store']}  "
              f"{r['product']}  KES {row_revenue(r):,.2f}")

    stores = sorted({row["store"] for row in clean_rows})
    big_per_store = {s: len([r for r in big_sales if r["store"] == s]) for s in stores}
    print("\nHigh-value sales per store")
    for store, count in big_per_store.items():
        print(f"  {store:<20} No. of Transaction: {count}")

    # Task 7: statistics on per-transaction revenue
    revenues = [row_revenue(r) for r in clean_rows]
    low, high = minimum_maximum(revenues)
    print("\nTransaction revenue statistics")
    print(f"  mean   : {mean(revenues):,.2f}")
    print(f"  median : {median(revenues):,.2f}")
    print(f"  min    : {low:,.2f}")
    print(f"  max    : {high:,.2f}")

    # Task 8: pandas verification
    my_results = {
        "total": total,
        "by_product": by_product,
        "top3": top3,
        "mean": mean(revenues),
        "median": median(revenues),
    }
    print("\n=== pandas verification ===")
    verify_with_pandas(DATA_PATH, my_results)


if __name__ == "__main__":
    main()











