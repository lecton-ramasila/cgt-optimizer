"""Market data retrieval for prices and FX rates."""

try:
    import yfinance as yf
except ImportError as error:
    raise SystemExit("Run: pip install flask yfinance") from error

from typing import Iterable
from config import DEFAULT_EUR_USD, DEFAULT_ZAR_USD, FX_TICKER


class PriceFetcher:
    def __init__(self, tickers: Iterable[str], fx_ticker: str = FX_TICKER, fallback_eur_usd: float = DEFAULT_EUR_USD, fallback_zar_usd: float = DEFAULT_ZAR_USD) -> None:
        self.tickers = list(tickers)
        self.fx_ticker = fx_ticker
        self.fallback_eur_usd = fallback_eur_usd
        self.fallback_zar_usd = fallback_zar_usd
        self.zar_usd_ticker = "ZARJPY=X"  # Use ZARJPY as proxy; will divide EUR rate by this

    def fetch(self) -> tuple[dict[str, float | None], float, float]:
        download_tickers = self.tickers + [self.fx_ticker]
        data = yf.download(download_tickers, period="1d", auto_adjust=True, progress=False)

        prices: dict[str, float | None] = {}
        for ticker in self.tickers:
            try:
                close_series = data["Close"][ticker].dropna()
                prices[ticker] = float(close_series.iloc[-1]) if not close_series.empty else None
            except Exception:
                prices[ticker] = None

        try:
            fx_series = data["Close"][self.fx_ticker].dropna()
            eur_usd = float(fx_series.iloc[-1]) if not fx_series.empty else self.fallback_eur_usd
        except Exception:
            eur_usd = self.fallback_eur_usd

        try:
            zar_data = yf.download("ZARJPY=X", period="1d", auto_adjust=True, progress=False)
            zar_jpy = float(zar_data["Close"].iloc[-1]) if not zar_data["Close"].empty else None
            if zar_jpy:
                zar_usd = 100 / zar_jpy
            else:
                zar_usd = self.fallback_zar_usd
        except Exception:
            zar_usd = self.fallback_zar_usd

        return prices, eur_usd, zar_usd
