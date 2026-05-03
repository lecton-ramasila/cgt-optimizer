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


def test_country_summary_uses_r50000_and_numeric_cgt(app_server):
    with sync_playwright() as p:
        browser = _open_browser(p)
        page = browser.new_page()

        page.route(
            "**/api/data**",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body='''{
                    "as_of": "03 May 2026 12:00:00",
                    "eur_usd": 1.13,
                    "zar_usd": 0.054,
                    "stocks": [],
                    "totals": {
                        "cost_usd": 119808.10,
                        "value_usd": 127215,
                        "pnl_usd": 7407,
                        "total_fees": 3.26,
                        "fx_fee": 2,
                        "net_pnl_local": 137163.15,
                        "taxable_local": 87163.15,
                        "inclusion_local": 34865.26,
                        "inclusion_rate": 0.4,
                        "marginal_rate": 0.18,
                        "cgt_local": 6275.75,
                        "local_currency": "ZAR",
                        "cgt_usd": 338.89,
                        "net_cash_usd": 126872.85,
                        "net_cash_local": 2349460.19
                    },
                    "country_summaries": [{
                        "country": "South Africa",
                        "country_key": "SouthAfrica",
                        "cgt_rate_pct": 18,
                        "cgt_exemption": "R50,000",
                        "local_currency": "ZAR",
                        "net_pnl_local": 137163.15,
                        "taxable_local": 87163.15,
                        "inclusion_local": 34865.26,
                        "inclusion_rate": 0.4,
                        "marginal_rate": 0.18,
                        "cgt_local": 6275.75,
                        "cgt_usd": 338.89,
                        "sale_signal": "ELIGIBLE FOR SALE in South Africa"
                    }],
                    "selected_countries": ["South Africa"],
                    "selected_tickers": []
                }''',
            ),
        )

        page.goto(app_server)

        summary_text = page.locator("#country-summaries").inner_text()
        assert "R50,000" in summary_text
        assert "CGT (ZAR)" in summary_text
        assert "R6,275.75" in summary_text
        assert "Marginal 18%" not in summary_text

        browser.close()
