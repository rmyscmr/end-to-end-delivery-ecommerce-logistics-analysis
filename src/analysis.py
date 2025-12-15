import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# -------------------------------------------------------------------
# 1. Paths & Setup
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]  # project root
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
VISUALS_DIR = BASE_DIR / "visuals"

DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VISUALS_DIR.mkdir(parents=True, exist_ok=True)

ORDERS_PATH = DATA_RAW_DIR / "E-Commerce Order Fulfillment Dataset (50K Records).csv"

sns.set(style="whitegrid")


# -------------------------------------------------------------------
# 2. Load Data
# -------------------------------------------------------------------
def load_orders():
    df_orders = pd.read_csv(ORDERS_PATH)
    return df_orders


# -------------------------------------------------------------------
# 3. Cleaning & Date Logic
# -------------------------------------------------------------------
def adjust_shipping_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make shipping dates realistic for domestic e-commerce:

    total_cycle_days = delivery_date - order_date

    - If total_cycle_days <= 4      -> same-day shipping (0 days delay)
    - If 5 <= total_cycle_days <= 8 -> next-day shipping (1 day delay)
    - If total_cycle_days > 8       -> 3 days delay

    Only applied where order_date and delivery_date are valid.
    """
    df = df.copy()

    if not {"order_date", "delivery_date"}.issubset(df.columns):
        return df

    mask = df["order_date"].notna() & df["delivery_date"].notna()
    total_cycle = (df.loc[mask, "delivery_date"] - df.loc[mask, "order_date"]).dt.days

    # Replace negative or weird values with median
    median_cycle = total_cycle[total_cycle >= 0].median()
    total_cycle = total_cycle.where(total_cycle >= 0, median_cycle)

    dispatch_delay_days = np.select(
        [
            total_cycle <= 4,
            (total_cycle > 4) & (total_cycle <= 8),
            total_cycle > 8,
        ],
        [0, 1, 3],
        default=1,
    )

    dispatch_delay = pd.to_timedelta(dispatch_delay_days, unit="D")

    df.loc[mask, "ship_date"] = df.loc[mask, "order_date"] + dispatch_delay
    df.loc[mask, "delivery_days"] = (
        df.loc[mask, "delivery_date"] - df.loc[mask, "ship_date"]
    ).dt.days

    return df


def clean_orders_data(df_orders: pd.DataFrame) -> pd.DataFrame:
    """
    Clean e-commerce orders dataset and standardise column names.
    """
    df = df_orders.copy()
    df.columns = [c.strip() for c in df.columns]

    rename_map = {
        "Order_ID": "order_id",
        "Customer_Region": "customer_region",
        "Product_Category": "product_category",
        "Order_Date": "order_date",
        "Ship_Date": "ship_date",
        "Delivery_Date": "delivery_date",
        "Shipping_Mode": "shipping_mode",
        "Shipping_Cost": "shipping_cost",
        "Delivery_Status": "delivery_status",
        "Delivery_Days": "delivery_days",
    }
    df = df.rename(columns=rename_map)

    # Parse dates
    for col in ["order_date", "ship_date", "delivery_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # On-time vs delayed flags (based on delivery_status)
    df["delivery_status_lower"] = df["delivery_status"].str.lower()
    df["on_time_flag"] = np.where(df["delivery_status_lower"] == "delayed", 0, 1)
    df["delay_flag"] = 1 - df["on_time_flag"]
    df.drop(columns=["delivery_status_lower"], inplace=True)

    # If delivery_days missing or weird, recalc from dates
    if "delivery_days" not in df.columns or df["delivery_days"].isna().all():
        df["delivery_days"] = (df["delivery_date"] - df["ship_date"]).dt.days

    # Adjust ship_date using your realistic 0–3 day rule
    df = adjust_shipping_dates(df)

    return df


# -------------------------------------------------------------------
# 4. KPI Calculations
# -------------------------------------------------------------------
def compute_kpis(df_final: pd.DataFrame):
    kpis = {}

    kpis["overall_on_time_pct"] = df_final["on_time_flag"].mean() * 100
    kpis["avg_delivery_days"] = df_final["delivery_days"].mean()

    if "shipping_mode" in df_final.columns:
        kpis["delays_by_shipping_mode"] = (
            df_final.groupby("shipping_mode")["delay_flag"].mean().sort_values(ascending=False)
        )

    if "product_category" in df_final.columns:
        kpis["orders_by_category"] = df_final["product_category"].value_counts()

    if "customer_region" in df_final.columns:
        kpis["deliveries_by_region"] = df_final["customer_region"].value_counts()

    df_time = df_final.copy()
    if "order_date" in df_time.columns:
        df_time["order_month"] = df_time["order_date"].dt.to_period("M").dt.to_timestamp()
        kpis["deliveries_over_time"] = df_time.groupby("order_month")["order_id"].count()

    return kpis


# -------------------------------------------------------------------
# 5. Visualisations
# -------------------------------------------------------------------
def plot_bar(series: pd.Series, title: str, xlabel: str, ylabel: str, filename: str, rotation: int = 0):
    plt.figure(figsize=(10, 6))
    series.plot(kind="bar")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=rotation)
    plt.tight_layout()
    plt.savefig(VISUALS_DIR / filename)
    plt.close()


def plot_line(series: pd.Series, title: str, xlabel: str, ylabel: str, filename: str):
    plt.figure(figsize=(10, 6))
    series.plot(kind="line", marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(VISUALS_DIR / filename)
    plt.close()


def create_visuals(kpis: dict):
    if "deliveries_by_region" in kpis:
        plot_bar(
            kpis["deliveries_by_region"],
            title="Deliveries by Region",
            xlabel="Customer Region",
            ylabel="Number of Orders",
            filename="deliveries_by_region.png",
            rotation=45,
        )

    if "delays_by_shipping_mode" in kpis:
        plot_bar(
            (kpis["delays_by_shipping_mode"] * 100).round(1),
            title="Delay Rate by Shipping Mode (%)",
            xlabel="Shipping Mode",
            ylabel="Delay Rate (%)",
            filename="delays_by_shipping_mode.png",
            rotation=0,
        )

    if "deliveries_over_time" in kpis:
        plot_line(
            kpis["deliveries_over_time"],
            title="Deliveries Over Time (Orders per Month)",
            xlabel="Month",
            ylabel="Number of Orders",
            filename="deliveries_over_time.png",
        )

    if "orders_by_category" in kpis:
        plot_bar(
            kpis["orders_by_category"],
            title="Orders by Product Category",
            xlabel="Product Category",
            ylabel="Number of Orders",
            filename="orders_by_category.png",
            rotation=45,
        )


# -------------------------------------------------------------------
# 6. Main
# -------------------------------------------------------------------
def main():
    print("Loading orders dataset...")
    df_orders_raw = load_orders()

    print("Cleaning orders dataset...")
    df_orders = clean_orders_data(df_orders_raw)

    print("Saving cleaned dataset...")
    processed_path = DATA_PROCESSED_DIR / "cleaned_merged_data.csv"
    df_orders.to_csv(processed_path, index=False)
    print(f"Cleaned data saved to: {processed_path}")

    print("Computing KPIs...")
    kpis = compute_kpis(df_orders)

    print("Creating visuals...")
    create_visuals(kpis)

    print("Done. Visuals saved in:", VISUALS_DIR)


if __name__ == "__main__":
    main()
