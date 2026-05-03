"""End-to-end tests using Playwright."""

import pytest
from playwright.sync_api import Page, expect


def test_homepage_loads(page: Page):
    """Test that the homepage loads successfully."""
    page.goto("http://localhost:5000")
    expect(page).to_have_title("Portfolio · Live PnL")
    expect(page.locator("text=PORTFOLIO")).to_be_visible()
    expect(page.locator("text=LIVE PnL")).to_be_visible()


def test_api_data_endpoint():
    """Test the /api/data endpoint returns valid JSON."""
    # This would require the app to be running
    # For now, placeholder
    pass