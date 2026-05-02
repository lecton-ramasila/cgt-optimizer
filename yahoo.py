import requests

YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


def fetch_live_prices(tickers):
    if not tickers:
        return {}

    symbols = ",".join(tickers)
    try:
        response = requests.get(
            YAHOO_QUOTE_URL,
            params={"symbols": symbols},
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("quoteResponse", {}).get("result", [])
        prices = {}
        for quote in results:
            symbol = quote.get("symbol")
            if not symbol:
                continue
            price = quote.get("regularMarketPrice")
            if price is None:
                price = quote.get("postMarketPrice")
            if price is not None:
                prices[symbol.upper()] = float(price)
        return prices
    except requests.RequestException:
        return {}
