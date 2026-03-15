"""
Playwright end-to-end tests for the Car Price Analysis dashboard.

Run from project root with a single command:
    pytest tests/test_playwright.py -v

Requires:
    pip install pytest-playwright
    playwright install chromium
"""

import re

import pytest
from playwright.sync_api import Page, expect

# Milliseconds to wait for reactive Shiny outputs to settle
TIMEOUT = 30_000

# ── helpers ──────────────────────────────────────────────────────────────────


def go_to_eda(page: Page, base_url: str) -> None:
    """Navigate to the app and open the EDA tab."""
    page.goto(base_url)
    page.get_by_role("tab", name="EDA").click()
    # Wait until the reactive filter-state card has rendered
    expect(page.locator("#current_filter_state")).to_be_visible(timeout=TIMEOUT)


# ── tests ─────────────────────────────────────────────────────────────────────


def test_eda_tab_loads_filter_state(page: Page, app_server: str) -> None:
    """Verifies the EDA tab renders the Current filter state card with Brand
    defaulting to 'All', confirming the dashboard loads and reactive outputs
    are working."""
    go_to_eda(page, app_server)

    filter_card = page.locator("#current_filter_state")
    expect(filter_card).to_be_visible(timeout=TIMEOUT)
    # Brand pill should read "All" when no brand is selected
    expect(filter_card).to_contain_text("All", timeout=TIMEOUT)


def test_vehicle_count_kpi_shows_positive_number(page: Page, app_server: str) -> None:
    """Verifies the Vehicle Count KPI in the EDA tab displays a positive integer,
    confirming that data is loaded and the summary aggregation is working."""
    go_to_eda(page, app_server)

    count_box = page.locator("#value_box_count")
    # Wait until the reactive value has rendered (shell appears before content)
    expect(count_box).to_contain_text(re.compile(r"\d+"), timeout=TIMEOUT)

    count_text = count_box.inner_text()
    digits = "".join(ch for ch in count_text if ch.isdigit())
    assert int(digits) > 0, f"Vehicle count should be > 0, got: {count_text!r}"


def test_currency_selector_updates_avg_price_label(page: Page, app_server: str) -> None:
    """Verifies that switching the currency radio button to CAD updates the
    Average Price KPI to display 'CAD', confirming currency conversion is
    reactive and wired to the display."""
    go_to_eda(page, app_server)

    # Default is USD — the KPI title should include "USD"
    avg_price_box = page.locator("#value_box_avg_price")
    expect(avg_price_box).to_contain_text("USD", timeout=TIMEOUT)

    # Switch to CAD
    page.locator("input[type='radio'][value='CAD']").click()

    # KPI title should now include "CAD"
    expect(avg_price_box).to_contain_text("CAD", timeout=TIMEOUT)


def test_reset_filters_restores_brand_to_all(page: Page, app_server: str) -> None:
    """Verifies that clicking Reset Filters clears a brand selection and returns
    the Brand filter-state pill to 'All', confirming the reset button correctly
    restores sidebar defaults."""
    go_to_eda(page, app_server)

    # Programmatically set the brand input to a single brand via the Shiny JS API
    page.evaluate("Shiny.setInputValue('input_brand', ['Toyota'], {priority: 'event'})")

    # Wait for the filter state to reflect the selection (Brand no longer "All")
    filter_card = page.locator("#current_filter_state")
    expect(filter_card).to_contain_text("Toyota", timeout=TIMEOUT)

    # Click Reset Filters
    page.locator("#reset_btn").click()

    # Brand pill should return to "All"
    expect(filter_card).to_contain_text("All", timeout=TIMEOUT)


def test_fuel_filter_change_updates_vehicle_count(page: Page, app_server: str) -> None:
    """Verifies that programmatically clearing the fuel-type filter to a single
    value reduces the Vehicle Count KPI, confirming the fuel-type filter drives
    the dataset visible to the dashboard charts."""
    go_to_eda(page, app_server)

    count_box = page.locator("#value_box_count")
    # Wait until the reactive value has rendered
    expect(count_box).to_contain_text(re.compile(r"\d+"), timeout=TIMEOUT)

    # Record the default vehicle count
    default_count = int("".join(ch for ch in count_box.inner_text() if ch.isdigit()))

    # Narrow the fuel type to only "Electric"
    page.evaluate(
        "Shiny.setInputValue('input_fuel_type', ['Electric'], {priority: 'event'})"
    )

    # Wait for the count to stabilize at a value different from the default.
    # Using not_to_contain_text(str(default_count)) is unreliable when the
    # default count is a substring of the filtered count (e.g. "68" inside
    # "168"), so we poll until the extracted integer changes instead.
    def get_count() -> int:
        return int("".join(ch for ch in count_box.inner_text() if ch.isdigit()))

    page.wait_for_function(
        f"() => document.querySelector('#value_box_count').innerText.replace(/\\D/g, '') !== '{default_count}'",
        timeout=TIMEOUT,
    )
    expect(count_box).to_contain_text(re.compile(r"\d+"), timeout=TIMEOUT)

    filtered_count = get_count()

    assert filtered_count < default_count, (
        f"Expected filtered count ({filtered_count}) < default ({default_count}) "
        "after restricting to Electric only"
    )
