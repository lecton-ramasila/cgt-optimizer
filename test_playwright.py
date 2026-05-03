"""End-to-end UI tests using Playwright with mocked API responses."""

import threading
import pytest
from playwright.sync_api import sync_playwright, Error as PlaywrightError

from app import create_app


@pytest.fixture(scope="module")
def app_server():
    app = create_app()
    server = threading.Thread(target=lambda: app.run(host="127.0.0.1", port=5010, debug=False, use_reloader=False), daemon=True)
    server.start()
    yield "http://127.0.0.1:5010"


def _open_browser(playwright):
    try:
        return playwright.chromium.launch()
    except PlaywrightError as exc:
        pytest.skip(f"Playwright browser unavailable: {exc}")


def test_homepage_loads_and_uses_zar_formatting(app_server):
    with sync_playwright() as p:
        browser = _open_browser(p)
        page = browser.new_page()

        def handle_api(route):
            route.fulfill(
                status=200,
                content_type="application/json",
                body='''{
                    "as_of": "03 May 2026 12:00:00",
                    "eur_usd": 1.13,
                    "stocks": [],
                    "totals": {
                        "cost_usd": 0,
                        "value_usd": 0,
                        "pnl_usd": 0,
                        "total_fees": 0,
                        "fx_fee": 0,
                        "net_pnl_local": 1000,
                        "taxable_local": 500,
                        "cgt_local": 90,
                        "local_currency": "ZAR",
                        "cgt_usd": 4.86,
                        "net_cash_usd": 5000,
                        "net_cash_local": 92592.59
                    },
                    "country_summaries": [{
                        "country": "South Africa",
                        "country_key": "SouthAfrica",
                        "cgt_rate_pct": 18,
                        "cgt_exemption": "$2,500",
                        "local_currency": "ZAR",
                        "net_pnl_local": 1000,
                        "taxable_local": 500,
                        "cgt_local": 90,
                        "cgt_usd": 4.86
                    }],
                    "selected_countries": ["South Africa"],
                    "selected_tickers": []
                }''',
            )

        page.route("**/api/data**", handle_api)
        page.goto(app_server)

        assert "Portfolio" in page.title()
        # Catch Bug 1 + Bug 4 + Bug 5 regressions in a single UI flow
        assert page.locator("#k-net").inner_text().startswith("R")
        assert page.locator("#b-net-eur").inner_text().startswith("R")
        assert "$2,500" in page.locator("#country-summaries").inner_text()

        browser.close()
