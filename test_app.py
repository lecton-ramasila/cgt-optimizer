"""Comprehensive unit tests for portfolio optimizer."""

import pytest
import json
from config import PORTFOLIO, CGT_RATE, CGT_EXEMPTION_EUR, SA_CGT_RATE, SA_EXEMPTION_ZAR
from portfolio import Portfolio, Lot, Position
from tax import CGTCalculator, get_cgt_params
from fees import FeeCalculator
from app import app, SUPPORTED_COUNTRIES, COUNTRY_LABELS


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestCurrencySupport:
    """Test currency handling for different countries."""

    def test_ireland_currency_is_eur(self):
        """Test that Ireland uses EUR."""
        rate, exemption = get_cgt_params("Ireland")
        assert rate == CGT_RATE
        assert exemption == CGT_EXEMPTION_EUR

    def test_south_africa_currency_is_zar(self):
        """Test that South Africa uses ZAR-based calculation."""
        rate, exemption = get_cgt_params("SouthAfrica")
        assert rate == SA_CGT_RATE
        assert exemption == SA_EXEMPTION_ZAR

    def test_cgt_calculator_ireland_returns_eur(self):
        """Test that Ireland CGT computation returns EUR as local currency."""
        calc = CGTCalculator(CGT_RATE, CGT_EXEMPTION_EUR, "Ireland")
        result = calc.compute(10000, 1.13)
        assert result["local_currency"] == "EUR"
        assert "net_pnl_local" in result
        assert "taxable_local" in result
        assert "cgt_local" in result

    def test_cgt_calculator_south_africa_returns_zar(self):
        """Test that South Africa CGT computation returns ZAR as local currency."""
        calc = CGTCalculator(SA_CGT_RATE, SA_EXEMPTION_ZAR, "SouthAfrica")
        result = calc.compute(10000, 1.13, 0.054)
        assert result["local_currency"] == "ZAR"
        assert "net_pnl_local" in result
        assert result["net_pnl_local"] > 0  # Should convert USD to ZAR

    def test_ireland_cgt_calculation(self):
        """Test Ireland CGT calculation with EUR conversion."""
        calc = CGTCalculator(0.33, 1270.0, "Ireland")
        net_pnl_usd = 10000
        eur_usd = 1.13
        result = calc.compute(net_pnl_usd, eur_usd)

        net_pnl_eur = net_pnl_usd / eur_usd
        expected_taxable = max(0, net_pnl_eur - 1270.0)
        expected_cgt = expected_taxable * 0.33

        assert abs(result["net_pnl_local"] - net_pnl_eur) < 0.01
        assert abs(result["taxable_local"] - expected_taxable) < 0.01
        assert abs(result["cgt_local"] - expected_cgt) < 0.01

    def test_south_africa_cgt_calculation(self):
        """Test South Africa CGT calculation with ZAR conversion."""
        calc = CGTCalculator(0.18, 50000.0, "SouthAfrica")
        net_pnl_usd = 10000
        zar_usd = 0.054
        result = calc.compute(net_pnl_usd, 1.13, zar_usd)

        net_pnl_zar = net_pnl_usd / zar_usd
        expected_taxable = max(0, net_pnl_zar - 50000.0)
        expected_cgt = (expected_taxable * 0.40) * 0.18

        assert abs(result["net_pnl_local"] - net_pnl_zar) < 0.01
        assert abs(result["taxable_local"] - expected_taxable) < 0.01
        assert abs(result["cgt_local"] - expected_cgt) < 0.01


class TestStockSelection:
    """Test individual and bulk stock selection."""

    def test_all_stocks_in_portfolio(self):
        """Test that all stocks are available."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        assert len(portfolio.positions) > 0
        tickers = [p.ticker for p in portfolio.positions]
        assert "GOOGL" in tickers
        assert "BRK-B" in tickers
        assert "AMZN" in tickers

    def test_portfolio_filtering_by_ticker(self):
        """Test filtering portfolio by specific tickers."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        filtered = portfolio.filtered(["GOOGL", "MSFT"])
        assert len(filtered.positions) == 2
        tickers = [p.ticker for p in filtered.positions]
        assert "GOOGL" in tickers
        assert "MSFT" in tickers
        assert "BRK-B" not in tickers

    def test_portfolio_filtering_single_stock(self):
        """Test filtering to a single stock."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        filtered = portfolio.filtered(["GOOGL"])
        assert len(filtered.positions) == 1
        assert filtered.positions[0].ticker == "GOOGL"

    def test_filtered_portfolio_maintains_country(self):
        """Test that filtered portfolio maintains country setting."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="SouthAfrica")
        filtered = portfolio.filtered(["GOOGL"])
        assert filtered.country == "SouthAfrica"
        assert filtered.cgt_calculator.country == "SouthAfrica"

    def test_filtered_portfolio_calculates_totals(self):
        """Test that filtered portfolio correctly calculates totals."""
        full_portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        price_dict = {position.ticker: 100.0 for position in full_portfolio.positions}
        full_portfolio.update_prices(price_dict)
        full_dict = full_portfolio.as_dict(1.13)

        filtered_portfolio = full_portfolio.filtered(["GOOGL"])
        googl_position = next(p for p in full_portfolio.positions if p.ticker == "GOOGL")
        googl_price = googl_position.price
        filtered_price_dict = {"GOOGL": googl_price}
        filtered_portfolio.update_prices(filtered_price_dict)
        filtered_dict = filtered_portfolio.as_dict(1.13)

        # Filtered should have fewer/different totals
        assert filtered_dict["totals"]["value_usd"] <= full_dict["totals"]["value_usd"]
        assert len(filtered_dict["stocks"]) == 1


class TestCountrySelection:
    """Test country selection and comparison."""

    def test_supported_countries(self):
        """Test that supported countries are defined."""
        assert "Ireland" in SUPPORTED_COUNTRIES
        assert "SouthAfrica" in SUPPORTED_COUNTRIES

    def test_country_labels(self):
        """Test country label mappings."""
        assert COUNTRY_LABELS["Ireland"] == "Ireland"
        assert COUNTRY_LABELS["SouthAfrica"] == "South Africa"

    def test_portfolio_with_ireland(self):
        """Test portfolio initialized with Ireland."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        assert portfolio.country == "Ireland"
        assert portfolio.cgt_calculator.country == "Ireland"
        assert portfolio.cgt_calculator.rate == CGT_RATE

    def test_portfolio_with_south_africa(self):
        """Test portfolio initialized with South Africa."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="SouthAfrica")
        assert portfolio.country == "SouthAfrica"
        assert portfolio.cgt_calculator.country == "SouthAfrica"
        assert portfolio.cgt_calculator.rate == SA_CGT_RATE


class TestFeeCalculations:
    """Test fee calculations across platforms."""

    def test_ibkr_commission(self):
        """Test IBKR commission calculation."""
        calc = FeeCalculator()
        # 100 shares * $0.005 = $0.50, but min is $1
        comm = calc.commission("IBKR", 100, 500)
        assert comm == 1.0  # Minimum

    def test_morgan_stanley_flat_fee(self):
        """Test Morgan Stanley flat fee."""
        calc = FeeCalculator()
        comm = calc.commission("Morgan Stanley", 100, 10000)
        assert comm == 9.99

    def test_regulatory_fees(self):
        """Test SEC and FINRA regulatory fees."""
        calc = FeeCalculator()
        sec, finra = calc.regulatory_fees(100, 10000)
        assert sec > 0
        assert finra > 0

    def test_total_fees_calculation(self):
        """Test total fees calculation."""
        calc = FeeCalculator()
        fees = calc.total_fees("IBKR", 100, 5000)
        assert "comm" in fees
        assert "sec" in fees
        assert "finra" in fees
        assert "total_fees" in fees
        assert fees["total_fees"] == fees["comm"] + fees["sec"] + fees["finra"]

    def test_fx_fee_calculation(self):
        """Test FX fee calculation."""
        calc = FeeCalculator()
        fx_fee = calc.fx_fee(10000)
        assert fx_fee >= 2.0  # Minimum FX fee


class TestPortfolioAggregation:
    """Test portfolio aggregation and data structure."""

    def test_portfolio_as_dict_structure(self):
        """Test that portfolio.as_dict() returns correct structure."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        prices = {position.ticker: 100.0 for position in portfolio.positions}
        portfolio.update_prices(prices)
        data = portfolio.as_dict(1.13)

        assert "stocks" in data
        assert "totals" in data
        assert "eur_usd" in data
        assert "as_of" in data

        # Test totals structure
        totals = data["totals"]
        assert "cost_usd" in totals
        assert "value_usd" in totals
        assert "pnl_usd" in totals
        assert "total_fees" in totals
        assert "fx_fee" in totals
        assert "net_pnl_local" in totals
        assert "taxable_local" in totals
        assert "cgt_local" in totals
        assert "local_currency" in totals
        assert "cgt_usd" in totals
        assert "net_cash_usd" in totals
        assert "net_cash_local" in totals

    def test_portfolio_stock_detail_structure(self):
        """Test that each stock has required fields."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        prices = {position.ticker: 100.0 for position in portfolio.positions}
        portfolio.update_prices(prices)
        data = portfolio.as_dict(1.13)

        for stock in data["stocks"]:
            assert "ticker" in stock
            assert "name" in stock
            assert "platform" in stock
            assert "type" in stock
            assert "currency" in stock
            assert "units" in stock
            assert "cost_usd" in stock
            assert "price" in stock
            assert "value_usd" in stock
            assert "pnl_usd" in stock
            assert "pnl_pct" in stock
            assert "comm" in stock
            assert "sec" in stock
            assert "finra" in stock
            assert "total_fees" in stock
            assert "net_pnl_usd" in stock

    def test_portfolio_with_zar_usd_parameter(self):
        """Test that portfolio.as_dict() accepts zar_usd parameter."""
        portfolio = Portfolio.from_definition(PORTFOLIO, country="SouthAfrica")
        prices = {position.ticker: 100.0 for position in portfolio.positions}
        portfolio.update_prices(prices)
        data = portfolio.as_dict(1.13, 0.054)

        assert data["totals"]["local_currency"] == "ZAR"


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_api_data_no_params(self, client):
        """Test /api/data returns valid JSON."""
        response = client.get("/api/data")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "stocks" in data
        assert "totals" in data

    def test_api_data_with_country_ireland(self, client):
        """Test /api/data with Ireland selected."""
        response = client.get("/api/data?countries=Ireland")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["totals"]["local_currency"] == "EUR"

    def test_api_data_with_country_south_africa(self, client):
        """Test /api/data with South Africa selected."""
        response = client.get("/api/data?countries=SouthAfrica")
        assert response.status_code == 200
        data = json.loads(response.data)
        # Primary country should be SouthAfrica, so currency should be ZAR
        assert data["totals"]["local_currency"] == "ZAR"

    def test_api_data_with_single_stock(self, client):
        """Test /api/data with single stock selected."""
        response = client.get("/api/data?stocks=GOOGL")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["stocks"]) == 1
        assert data["stocks"][0]["ticker"] == "GOOGL"

    def test_api_data_with_multiple_stocks(self, client):
        """Test /api/data with multiple stocks selected."""
        response = client.get("/api/data?stocks=GOOGL,MSFT,BRK-B")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["stocks"]) == 3
        tickers = [stock["ticker"] for stock in data["stocks"]]
        assert "GOOGL" in tickers
        assert "MSFT" in tickers
        assert "BRK-B" in tickers

    def test_api_data_country_summaries(self, client):
        """Test /api/data returns country summaries when multiple countries selected."""
        response = client.get("/api/data?countries=Ireland,SouthAfrica")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "country_summaries" in data
        assert len(data["country_summaries"]) >= 1

    def test_api_data_country_summary_structure(self, client):
        """Test that country summary has required fields."""
        response = client.get("/api/data?countries=Ireland,SouthAfrica")
        assert response.status_code == 200
        data = json.loads(response.data)
        
        for summary in data["country_summaries"]:
            assert "country" in summary
            assert "country_key" in summary
            assert "cgt_rate_pct" in summary
            assert "cgt_exemption" in summary
            assert "local_currency" in summary
            assert "net_pnl_local" in summary
            assert "taxable_local" in summary
            assert "cgt_local" in summary
            assert "cgt_usd" in summary

    def test_api_data_bottom_line_values_present(self, client):
        """Test that bottom line values are calculated."""
        response = client.get("/api/data")
        assert response.status_code == 200
        data = json.loads(response.data)
        totals = data["totals"]

        # These should not be null/missing
        assert "net_cash_usd" in totals
        assert "net_cash_local" in totals
        # At least one should have a value (assuming prices are available)
        assert totals["net_cash_usd"] is not None or totals["value_usd"] == 0

    def test_api_data_homepage_loads(self, client):
        """Test that homepage loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"PORTFOLIO" in response.data
        assert b"LIVE PnL" in response.data


class TestCGTExemptions:
    """Test CGT exemption handling."""

    def test_ireland_exemption_eur(self):
        """Test Ireland exemption is in EUR."""
        calc = CGTCalculator(CGT_RATE, CGT_EXEMPTION_EUR, "Ireland")
        assert calc.exemption == CGT_EXEMPTION_EUR

    def test_south_africa_exemption_usd(self):
        """Test South Africa exemption is in USD."""
        calc = CGTCalculator(SA_CGT_RATE, SA_EXEMPTION_ZAR, "SouthAfrica")
        assert calc.exemption == SA_EXEMPTION_ZAR

    def test_exemption_applied_in_ireland(self):
        """Test that exemption reduces taxable gain in Ireland."""
        calc = CGTCalculator(0.33, 1000.0, "Ireland")
        eur_usd = 1.13
        net_pnl_usd = 10000

        result = calc.compute(net_pnl_usd, eur_usd)
        net_pnl_eur = net_pnl_usd / eur_usd
        expected_taxable = max(0, net_pnl_eur - 1000.0)

        assert abs(result["taxable_local"] - expected_taxable) < 0.01

    def test_exemption_applied_in_south_africa(self):
        """Test that exemption reduces taxable gain in South Africa."""
        calc = CGTCalculator(0.18, 2000.0, "SouthAfrica")
        zar_usd = 0.054
        net_pnl_usd = 10000

        result = calc.compute(net_pnl_usd, 1.13, zar_usd)
        net_pnl_zar = net_pnl_usd / zar_usd
        expected_taxable = max(0, net_pnl_zar - 2000.0)

        assert abs(result["taxable_local"] - expected_taxable) < 0.01

    def test_negative_gain_uses_zero_exemption(self):
        """Test that negative gains don't apply exemption incorrectly."""
        calc = CGTCalculator(0.33, 1000.0, "Ireland")
        result = calc.compute(-5000, 1.13)

        assert result["taxable_local"] == 0
        assert result["cgt_local"] == 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_gain_no_cgt(self):
        """Test that zero gain results in zero CGT."""
        calc = CGTCalculator(0.33, 1000.0, "Ireland")
        result = calc.compute(0, 1.13)

        assert result["cgt_local"] == 0
        assert result["cgt_usd"] == 0

    def test_small_gain_below_exemption(self):
        """Test gain below exemption threshold."""
        calc = CGTCalculator(0.33, 1000.0, "Ireland")
        eur_usd = 1.13
        net_pnl_usd = 500  # Less than 1000 EUR exemption

        result = calc.compute(net_pnl_usd, eur_usd)
        assert result["cgt_local"] == 0

    def test_large_gain_above_exemption(self):
        """Test gain significantly above exemption."""
        calc = CGTCalculator(0.33, 1000.0, "Ireland")
        eur_usd = 1.13
        net_pnl_usd = 100000

        result = calc.compute(net_pnl_usd, eur_usd)
        assert result["cgt_local"] > 0

    def test_currency_conversion_accuracy(self):
        """Test currency conversion maintains accuracy."""
        calc = CGTCalculator(0.33, 1000.0, "Ireland")
        eur_usd = 1.13
        net_pnl_usd = 1000

        result = calc.compute(net_pnl_usd, eur_usd)
        # Should be roughly 1000 / 1.13 EUR
        assert abs(result["net_pnl_local"] - (1000 / 1.13)) < 0.01

    def test_zar_conversion_accuracy(self):
        """Test ZAR conversion maintains accuracy."""
        calc = CGTCalculator(0.18, 0, "SouthAfrica")
        zar_usd = 0.054
        net_pnl_usd = 1000

        result = calc.compute(net_pnl_usd, 1.13, zar_usd)
        # Should be roughly 1000 / 0.054 ZAR
        assert abs(result["net_pnl_local"] - (1000 / zar_usd)) < 1.0  # Allow 1 ZAR error


class TestRegressionBugs:
    """Regression tests for previously reported currency/FX bugs."""

    def test_south_africa_exemption_string_is_usd(self, client):
        response = client.get("/api/data?countries=SouthAfrica")
        data = json.loads(response.data)
        sa_summary = next(summary for summary in data["country_summaries"] if summary["country_key"] == "SouthAfrica")
        assert sa_summary["cgt_exemption"].startswith("R")

    def test_position_currency_defaults_to_usd(self):
        portfolio = Portfolio.from_definition(PORTFOLIO, country="Ireland")
        assert all(position.currency == "USD" for position in portfolio.positions)


class TestPriceFetcher:
    def test_fetch_uses_zarusd_ticker(self, monkeypatch):
        from pricing import PriceFetcher
        import pandas as pd

        calls = []

        def fake_download(tickers, period, auto_adjust, progress):
            calls.append(tickers)
            if tickers == "ZARUSD=X":
                return pd.DataFrame({"Close": [0.054]})
            cols = pd.MultiIndex.from_product([["Close"], ["GOOGL", "EURUSD=X"]])
            return pd.DataFrame([[100.0, 1.13]], columns=cols)

        monkeypatch.setattr("pricing.yf.download", fake_download)
        prices, eur_usd, zar_usd = PriceFetcher(["GOOGL"]).fetch()

        assert "ZARUSD=X" in calls
        assert prices["GOOGL"] == 100.0
        assert eur_usd == 1.13
        assert zar_usd == 0.054


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
