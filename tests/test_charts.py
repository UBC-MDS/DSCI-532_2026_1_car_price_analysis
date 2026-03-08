"""
Smoke tests: chart functions return valid matplotlib Figure objects.
Run from project root: pytest tests/test_charts.py -v
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

# Add src to path so we can import charts (which imports data_processing)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from charts import (
    chart_fuel_avg_price,
    chart_brand_avg_price,
    chart_engine_efficiency_scatter,
    chart_fuel_group_efficiency,
    chart_hp_price_scatter,
    ai_chart_engine_efficiency_scatter,
    ai_chart_fuel_group_efficiency,
    ai_chart_fuel_avg_price,
)


def _is_valid_figure(fig):
    """Return True if fig is a matplotlib Figure with at least one axes."""
    return isinstance(fig, plt.Figure) and len(fig.axes) >= 1


# Fixtures: minimal DataFrames for EDA and AI charts 

@pytest.fixture
def df_eda():
    """Minimal DataFrame with columns needed for EDA chart functions."""
    return pd.DataFrame({
        "Brand": ["Toyota", "Honda"],
        "Body_Type": ["Sedan", "SUV"],
        "Fuel_Type": ["Petrol", "Hybrid"],
        "Price_USD": [25000.0, 35000.0],
        "Engine_CC": [1800, 2000],
        "Efficiency_Score": [0.5, 0.7],
        "Horsepower": [140, 180],
    })


@pytest.fixture
def df_ai():
    """Minimal DataFrame with columns needed for AI chart functions."""
    return pd.DataFrame({
        "Fuel_Type": ["Petrol", "Hybrid"],
        "Price_USD": [25000.0, 35000.0],
        "Engine_CC": [1800, 2000],
        "Efficiency_Score": [0.5, 0.7],
    })


@pytest.fixture
def df_empty():
    """Empty DataFrame with required columns for empty-state charts."""
    return pd.DataFrame(
        columns=["Brand", "Fuel_Type", "Price_USD", "Engine_CC", "Efficiency_Score", "Horsepower"]
    )


#  EDA chart smoke tests 

def test_chart_fuel_avg_price_returns_figure(df_eda):
    fig = chart_fuel_avg_price(df_eda)
    assert _is_valid_figure(fig)


def test_chart_fuel_avg_price_empty_returns_figure(df_empty):
    fig = chart_fuel_avg_price(df_empty)
    assert _is_valid_figure(fig)


def test_chart_fuel_avg_price_currency_params(df_eda):
    fig = chart_fuel_avg_price(df_eda, currency_sym="C$", currency_rate=1.35)
    assert _is_valid_figure(fig)


def test_chart_brand_avg_price_returns_figure(df_eda):
    fig = chart_brand_avg_price(df_eda)
    assert _is_valid_figure(fig)


def test_chart_brand_avg_price_empty_returns_figure(df_empty):
    fig = chart_brand_avg_price(df_empty)
    assert _is_valid_figure(fig)


def test_chart_engine_efficiency_scatter_returns_figure(df_eda):
    fig = chart_engine_efficiency_scatter(df_eda)
    assert _is_valid_figure(fig)


def test_chart_engine_efficiency_scatter_empty_returns_figure(df_empty):
    fig = chart_engine_efficiency_scatter(df_empty)
    assert _is_valid_figure(fig)


def test_chart_fuel_group_efficiency_returns_figure(df_eda):
    fig = chart_fuel_group_efficiency(df_eda)
    assert _is_valid_figure(fig)


def test_chart_fuel_group_efficiency_empty_returns_figure(df_empty):
    fig = chart_fuel_group_efficiency(df_empty)
    assert _is_valid_figure(fig)


def test_chart_hp_price_scatter_returns_figure(df_eda):
    fig = chart_hp_price_scatter(df_eda)
    assert _is_valid_figure(fig)


def test_chart_hp_price_scatter_empty_returns_figure(df_empty):
    fig = chart_hp_price_scatter(df_empty)
    assert _is_valid_figure(fig)


def test_chart_hp_price_scatter_currency_params(df_eda):
    fig = chart_hp_price_scatter(df_eda, currency_sym="€", currency_rate=0.92)
    assert _is_valid_figure(fig)


# AI chart smoke tests 

def test_ai_chart_engine_efficiency_scatter_returns_figure(df_ai):
    fig = ai_chart_engine_efficiency_scatter(df_ai)
    assert _is_valid_figure(fig)


def test_ai_chart_engine_efficiency_scatter_empty_returns_figure(df_empty):
    fig = ai_chart_engine_efficiency_scatter(df_empty)
    assert _is_valid_figure(fig)


def test_ai_chart_fuel_group_efficiency_returns_figure(df_ai):
    fig = ai_chart_fuel_group_efficiency(df_ai)
    assert _is_valid_figure(fig)


def test_ai_chart_fuel_group_efficiency_empty_returns_figure(df_empty):
    fig = ai_chart_fuel_group_efficiency(df_empty)
    assert _is_valid_figure(fig)


def test_ai_chart_fuel_avg_price_returns_figure(df_ai):
    fig = ai_chart_fuel_avg_price(df_ai)
    assert _is_valid_figure(fig)


def test_ai_chart_fuel_avg_price_empty_returns_figure(df_empty):
    fig = ai_chart_fuel_avg_price(df_empty)
    assert _is_valid_figure(fig)


def test_ai_chart_fuel_avg_price_currency_params(df_ai):
    fig = ai_chart_fuel_avg_price(df_ai, currency_sym="C$", currency_rate=1.35)
    assert _is_valid_figure(fig)
