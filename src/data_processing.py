"""
data_processing.py
==================
Pure Python module — no Shiny dependencies.
Handles data loading (ibis + DuckDB), constants, color palettes, and filtering logic.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import ibis
import pandas as pd
from matplotlib.ticker import FuncFormatter

# Use DuckDB backend
ibis.set_backend("duckdb")


# ── Paths ────────────────────────────────────────────────────────
PARQUET_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "processed" / "global_cars_enhanced.parquet"
)
# Legacy CSV path kept for backwards compatibility
DATA_PATH = (
    Path(__file__).resolve().parents[1] / "data" / "raw" / "global_cars_enhanced.csv"
)


# ── Data Loading ─────────────────────────────────────────────────
def load_data(path: Path = None) -> ibis.Table:
    """Load the Parquet file into an ibis table (lazy, backed by DuckDB).

    Falls back to CSV if the Parquet file does not exist.
    """
    if path is not None:
        if str(path).endswith(".parquet"):
            return ibis.read_parquet(str(path))
        return ibis.read_csv(str(path))

    if PARQUET_PATH.exists():
        return ibis.read_parquet(str(PARQUET_PATH))
    return ibis.read_csv(str(DATA_PATH))


def to_pandas(table) -> pd.DataFrame:
    """Materialise an ibis table (or pass through a DataFrame)."""
    if isinstance(table, pd.DataFrame):
        return table
    return table.to_pandas()


# ── Derived Choice Lists & Range Constants ───────────────────────
def build_choices(data) -> dict:
    """
    Return a dict of sorted unique choice lists and price bounds
    derived from *data* (ibis table or pandas DataFrame).

    Keys: brand_choices, body_type_choices, fuel_type_choices,
          price_min, price_max
    """
    if isinstance(data, pd.DataFrame):
        return {
            "brand_choices": sorted(data["Brand"].unique().tolist()),
            "body_type_choices": sorted(data["Body_Type"].unique().tolist()),
            "fuel_type_choices": sorted(data["Fuel_Type"].unique().tolist()),
            "price_min": int(data["Price_USD"].min()),
            "price_max": int(data["Price_USD"].max()),
        }

    # ibis path — lazy queries executed by DuckDB
    brand_choices = sorted(
        data.select("Brand").distinct().to_pandas()["Brand"].tolist()
    )
    body_type_choices = sorted(
        data.select("Body_Type").distinct().to_pandas()["Body_Type"].tolist()
    )
    fuel_type_choices = sorted(
        data.select("Fuel_Type").distinct().to_pandas()["Fuel_Type"].tolist()
    )
    agg = data.aggregate(
        price_min=data["Price_USD"].min(),
        price_max=data["Price_USD"].max(),
    ).to_pandas()

    return {
        "brand_choices": brand_choices,
        "body_type_choices": body_type_choices,
        "fuel_type_choices": fuel_type_choices,
        "price_min": int(agg["price_min"].iloc[0]),
        "price_max": int(agg["price_max"].iloc[0]),
    }


def build_defaults(choices: dict) -> dict:
    """
    Return sustainability-focused filter defaults derived from *choices*.

    Keys: body_type_defaults, fuel_type_defaults, price_default_range
    """
    body_type_defaults = [
        bt
        for bt in ["Sedan", "SUV", "Hatchback"]
        if bt in choices["body_type_choices"]
    ]
    fuel_type_defaults = [
        f
        for f in ["Hybrid", "Petrol", "Diesel"]
        if f in choices["fuel_type_choices"]
    ] or choices["fuel_type_choices"]

    price_cap = min(60_000, choices["price_max"])
    price_default_range = (choices["price_min"], price_cap)

    return {
        "body_type_defaults": body_type_defaults,
        "fuel_type_defaults": fuel_type_defaults,
        "price_default_range": price_default_range,
    }


# ── Color Palettes ────────────────────────────────────────────────
PLOT_FALLBACK_COLOR = "#999999"

EDA_FUEL_PRICE_COLORS = ["#2a9d8f", "#e76f51", "#457b9d", "#f4a261"]
EDA_BRAND_PRICE_COLOR = "#6d597a"
EDA_ENGINE_EFFICIENCY_COLORS = {
    "Hybrid": "#ef476f",
    "Petrol": "#ffd166",
    "Diesel": "#06d6a0",
    "Electric": "#118ab2",
}
EDA_FUEL_GROUP_COLORS = {
    "Hybrid": "#5f0f40",
    "Standard Fuel": "#ff7f51",
}
EDA_HP_PRICE_COLORS = {
    "Hybrid": "#9b5de5",
    "Petrol": "#00bbf9",
    "Diesel": "#00f5d4",
    "Electric": "#f15bb5",
}

AI_ENGINE_EFFICIENCY_COLORS = {
    "Hybrid": "#8338ec",
    "Petrol": "#ffbe0b",
    "Diesel": "#3a86ff",
    "Electric": "#fb5607",
}
AI_FUEL_GROUP_COLORS = {
    "Hybrid": "#386641",
    "Standard Fuel": "#bc4749",
}
AI_FUEL_PRICE_COLORS = ["#264653", "#e9c46a", "#e76f51", "#2a9d8f"]

AI_TEST_PROMPTS = [
    "Show only hybrid and electric vehicles under $35,000 with efficiency score above 0.6",
    "Compare average price by fuel type for SUV body type",
    "Return the top 8 brands by average efficiency score",
]

# ── Currency Conversion (approximate rates from USD) ─────────────────
CURRENCY_RATES = {"USD": 1.0, "CAD": 1.35, "EUR": 0.92}
CURRENCY_SYMBOLS = {"USD": "$", "CAD": "C$", "EUR": "€"}


def make_currency_formatter(symbol: str):
    """Return a FuncFormatter for axis labels with the given currency symbol."""
    return FuncFormatter(lambda x, pos: f"{symbol}{int(x):,}" if pd.notnull(x) else "")


# ── Shared Formatter ──────────────────────────────────────────────
FIG_WIDTH = 6
FIG_HEIGHT = 4

usd_formatter = FuncFormatter(lambda x, pos: f"{int(x):,}" if pd.notnull(x) else "")


# ── Selection Helpers ─────────────────────────────────────────────
def as_selection(value) -> list:
    """Normalise a Shiny selectize value to a plain list."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def selection_label(selected_values, all_values) -> str:
    """Return a human-readable label for the current selection."""
    selected = as_selection(selected_values)
    if not selected or set(selected) == set(all_values):
        return "All"
    return ", ".join(selected)


# ── Core Filter Function (ibis-native, lazy) ─────────────────────
def filter_dataframe(
    data,
    brands: list,
    body_types: list,
    fuel_types: list,
    price_range: tuple,
):
    """
    Apply EDA sidebar filters to *data* and return the filtered result.

    Accepts an ibis table or pandas DataFrame.
    Returns the same type as input (ibis table stays lazy).
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
        if brands:
            df = df[df["Brand"].isin(brands)]
        if body_types:
            df = df[df["Body_Type"].isin(body_types)]
        price_low, price_high = price_range
        df = df[(df["Price_USD"] >= price_low) & (df["Price_USD"] <= price_high)]
        if fuel_types:
            df = df[df["Fuel_Type"].isin(fuel_types)]
        return df

    # ibis path — build lazy expression, no execution yet
    t = data
    if brands:
        t = t.filter(t["Brand"].isin(brands))
    if body_types:
        t = t.filter(t["Body_Type"].isin(body_types))

    price_low, price_high = price_range
    t = t.filter((t["Price_USD"] >= price_low) & (t["Price_USD"] <= price_high))

    if fuel_types:
        t = t.filter(t["Fuel_Type"].isin(fuel_types))

    return t


# ── KPI Summary ───────────────────────────────────────────────────
def compute_kpis(data, currency_rate: float = 1.0) -> dict:
    """Return count and avg_price KPIs. avg_price is converted by currency_rate.

    Accepts ibis table or pandas DataFrame.
    """
    if isinstance(data, pd.DataFrame):
        count = int(len(data))
        avg_price = float(data["Price_USD"].mean()) * currency_rate if count > 0 else None
        return {"count": count, "avg_price": avg_price}

    # ibis path
    agg = data.aggregate(
        count=data.count(),
        avg_price=data["Price_USD"].mean(),
    ).to_pandas()

    count = int(agg["count"].iloc[0])
    raw_avg = agg["avg_price"].iloc[0]
    avg_price = float(raw_avg) * currency_rate if count > 0 and pd.notnull(raw_avg) else None
    return {"count": count, "avg_price": avg_price}
