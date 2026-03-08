"""
Edge-case and correctness tests for data_processing module.
Run from project root: pytest tests/test_data_processing.py -v
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src to path so we can import data_processing
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_processing import (
    build_choices,
    build_defaults,
    filter_dataframe,
    compute_kpis,
    load_data,
    as_selection,
    selection_label,
    DATA_PATH,
)


#  Fixtures: minimal DataFrames

@pytest.fixture
def df_empty():
    """DataFrame with required columns but no rows."""
    return pd.DataFrame(
        columns=[
            "Brand", "Body_Type", "Fuel_Type", "Price_USD",
            "Manufacturing_Country", "Manufacture_Year",
        ]
    )


@pytest.fixture
def df_minimal():
    """Minimal valid DataFrame for build_choices / filter_dataframe."""
    return pd.DataFrame({
        "Brand": ["Toyota", "Honda", "Toyota"],
        "Body_Type": ["Sedan", "SUV", "Sedan"],
        "Fuel_Type": ["Petrol", "Hybrid", "Diesel"],
        "Price_USD": [25000, 35000, 28000],
        "Manufacturing_Country": ["Japan", "Japan", "USA"],
        "Manufacture_Year": [2020, 2021, 2019],
    })


@pytest.fixture
def df_with_nulls():
    """DataFrame with some nulls in key columns."""
    return pd.DataFrame({
        "Brand": ["Toyota", None, "Honda"],
        "Body_Type": ["Sedan", "SUV", None],
        "Fuel_Type": ["Petrol", "Hybrid", "Diesel"],
        "Price_USD": [25000, 35000, None],
        "Manufacturing_Country": ["Japan", "Japan", "USA"],
        "Manufacture_Year": [2020, 2021, 2019],
    })


# load_data 

def test_load_data_returns_dataframe():
    """load_data returns a DataFrame with expected columns."""
    df = load_data(DATA_PATH)
    assert isinstance(df, pd.DataFrame)
    required = {"Brand", "Body_Type", "Fuel_Type", "Price_USD", "Manufacturing_Country", "Manufacture_Year"}
    assert required.issubset(df.columns), f"Missing columns: {required - set(df.columns)}"


def test_load_data_default_path():
    """load_data uses DATA_PATH when no path given."""
    df = load_data()
    assert isinstance(df, pd.DataFrame)
    assert "Price_USD" in df.columns


#  build_choices: empty and type checks 

def test_build_choices_empty_df_raises(df_empty):
    """build_choices on empty DataFrame raises (min/max of empty Price_USD)."""
    with pytest.raises((ValueError, TypeError)):
        build_choices(df_empty)


def test_build_choices_with_nulls_raises(df_with_nulls):
    """build_choices with None in categorical columns raises (sorted can't compare None to str)."""
    with pytest.raises(TypeError):
        build_choices(df_with_nulls)


def test_build_choices_type_checks(df_minimal):
    """build_choices returns correct types and keys."""
    choices = build_choices(df_minimal)
    assert set(choices.keys()) == {
        "brand_choices", "body_type_choices", "fuel_type_choices",
        "price_min", "price_max",
    }
    assert isinstance(choices["brand_choices"], list)
    assert isinstance(choices["body_type_choices"], list)
    assert isinstance(choices["fuel_type_choices"], list)
    assert all(isinstance(x, str) for x in choices["brand_choices"])
    assert isinstance(choices["price_min"], (int, float))
    assert isinstance(choices["price_max"], (int, float))


def test_build_choices_correctness(df_minimal):
    """build_choices derives correct unique values and price range."""
    choices = build_choices(df_minimal)
    assert set(choices["brand_choices"]) == {"Honda", "Toyota"}
    assert set(choices["body_type_choices"]) == {"Sedan", "SUV"}
    assert set(choices["fuel_type_choices"]) == {"Diesel", "Hybrid", "Petrol"}
    assert choices["price_min"] == 25000
    assert choices["price_max"] == 35000


# build_defaults 

def test_build_defaults_type_and_keys(df_minimal):
    """build_defaults returns dict with expected keys."""
    choices = build_choices(df_minimal)
    defaults = build_defaults(choices)
    assert isinstance(defaults, dict)
    assert set(defaults.keys()) == {
        "body_type_defaults", "fuel_type_defaults", "price_default_range",
    }
    assert isinstance(defaults["body_type_defaults"], list)
    assert isinstance(defaults["fuel_type_defaults"], list)
    assert isinstance(defaults["price_default_range"], tuple)
    assert len(defaults["price_default_range"]) == 2


def test_build_defaults_sustainability_subset(df_minimal):
    """Defaults prefer Sedan/SUV/Hatchback and Hybrid/Petrol/Diesel."""
    choices = build_choices(df_minimal)
    defaults = build_defaults(choices)
    for bt in defaults["body_type_defaults"]:
        assert bt in ["Sedan", "SUV", "Hatchback"]
    assert defaults["price_default_range"][0] == choices["price_min"]
    assert defaults["price_default_range"][1] <= min(60_000, choices["price_max"])


# filter_dataframe 

def test_filter_dataframe_empty_df(df_empty):
    """filter_dataframe on empty DataFrame returns empty DataFrame."""
    out = filter_dataframe(
        df_empty,
        brands=[],
        body_types=[],
        fuel_types=[],
        price_range=(0, 100_000),
    )
    assert isinstance(out, pd.DataFrame)
    assert len(out) == 0
    assert out.columns.tolist() == df_empty.columns.tolist()


def test_filter_dataframe_empty_lists_returns_copy(df_minimal):
    """Empty filter lists mean no filter applied; returns copy."""
    out = filter_dataframe(
        df_minimal,
        brands=[],
        body_types=[],
        fuel_types=[],
        price_range=(0, 100_000),
    )
    assert len(out) == len(df_minimal)
    assert out is not df_minimal


def test_filter_dataframe_brand_correctness(df_minimal):
    """Filter by brand keeps only selected brands."""
    out = filter_dataframe(
        df_minimal,
        brands=["Toyota"],
        body_types=[],
        fuel_types=[],
        price_range=(0, 100_000),
    )
    assert len(out) == 2
    assert set(out["Brand"]) == {"Toyota"}


def test_filter_dataframe_body_type_correctness(df_minimal):
    """Filter by body type keeps only selected body types."""
    out = filter_dataframe(
        df_minimal,
        brands=[],
        body_types=["SUV"],
        fuel_types=[],
        price_range=(0, 100_000),
    )
    assert len(out) == 1
    assert out["Body_Type"].iloc[0] == "SUV"


def test_filter_dataframe_fuel_type_correctness(df_minimal):
    """Filter by fuel type keeps only selected fuel types."""
    out = filter_dataframe(
        df_minimal,
        brands=[],
        body_types=[],
        fuel_types=["Hybrid", "Diesel"],
        price_range=(0, 100_000),
    )
    assert len(out) == 2
    assert set(out["Fuel_Type"]) == {"Hybrid", "Diesel"}


def test_filter_dataframe_price_range_correctness(df_minimal):
    """Filter by price range keeps only rows in [low, high]."""
    out = filter_dataframe(
        df_minimal,
        brands=[],
        body_types=[],
        fuel_types=[],
        price_range=(26000, 34000),
    )
    # Only 28000 is in [26000, 34000]; 25000 and 35000 are outside
    assert len(out) == 1
    assert out["Price_USD"].iloc[0] == 28000
    assert out["Price_USD"].min() >= 26000
    assert out["Price_USD"].max() <= 34000


def test_filter_dataframe_combined_filters(df_minimal):
    """Combined filters apply AND logic."""
    out = filter_dataframe(
        df_minimal,
        brands=["Toyota"],
        body_types=["Sedan"],
        fuel_types=["Petrol", "Diesel"],
        price_range=(24000, 30000),
    )
    # df_minimal has Toyota Sedan Petrol 25000 and Toyota Sedan Diesel 28000
    assert len(out) == 2
    assert set(out["Brand"]) == {"Toyota"}
    assert set(out["Body_Type"]) == {"Sedan"}
    assert set(out["Fuel_Type"]) == {"Petrol", "Diesel"}
    assert out["Price_USD"].min() >= 24000
    assert out["Price_USD"].max() <= 30000


# compute_kpis 

def test_compute_kpis_empty_df(df_empty):
    """compute_kpis on empty DataFrame: count 0, avg_price None."""
    result = compute_kpis(df_empty)
    assert result["count"] == 0
    assert result["avg_price"] is None


def test_compute_kpis_type_checks(df_minimal):
    """compute_kpis returns dict with int count and float or None avg_price."""
    result = compute_kpis(df_minimal)
    assert isinstance(result, dict)
    assert "count" in result
    assert "avg_price" in result
    assert isinstance(result["count"], int)
    assert result["avg_price"] is None or isinstance(result["avg_price"], (int, float))


def test_compute_kpis_correctness(df_minimal):
    """compute_kpis count and mean match DataFrame."""
    result = compute_kpis(df_minimal)
    assert result["count"] == 3
    expected_mean = df_minimal["Price_USD"].mean()
    assert result["avg_price"] == pytest.approx(expected_mean, rel=1e-9)


def test_compute_kpis_currency_rate(df_minimal):
    """compute_kpis applies currency_rate to avg_price."""
    result = compute_kpis(df_minimal, currency_rate=1.35)
    assert result["count"] == 3
    expected = df_minimal["Price_USD"].mean() * 1.35
    assert result["avg_price"] == pytest.approx(expected, rel=1e-9)


# as_selection / selection_label 

def test_as_selection_none():
    """as_selection(None) returns []."""
    assert as_selection(None) == []


def test_as_selection_string():
    """as_selection(str) returns [str]."""
    assert as_selection("Toyota") == ["Toyota"]


def test_as_selection_list():
    """as_selection(list) returns same list."""
    assert as_selection(["A", "B"]) == ["A", "B"]


def test_selection_label_all():
    """selection_label when all selected or none selected returns 'All'."""
    assert selection_label([], ["A", "B"]) == "All"
    assert selection_label(["A", "B"], ["A", "B"]) == "All"


def test_selection_label_subset():
    """selection_label for subset returns comma-separated."""
    assert selection_label(["A"], ["A", "B"]) == "A"
    assert selection_label(["A", "B"], ["A", "B", "C"]) == "A, B"
