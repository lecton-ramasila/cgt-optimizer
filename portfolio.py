"""Portfolio aggregation and per-position profit/loss calculation."""

from dataclasses import dataclass, field
from typing import Iterable

from fees import FeeCalculator
from tax import CGTCalculator, get_cgt_params
from config import COUNTRY


@dataclass(frozen=True)
class Lot:
    date: str
    cost_per_share: float
    units: float


@dataclass
class Position:
    ticker: str
    name: str
    platform: str
    asset_type: str
    lots: list[Lot]
    price: float | None = None
    fee_calculator: FeeCalculator = field(default_factory=FeeCalculator)

    @property
    def total_units(self) -> float:
        return sum(lot.units for lot in self.lots)

    @property
    def total_cost(self) -> float:
        return sum(lot.cost_per_share * lot.units for lot in self.lots)

    @property
    def market_value(self) -> float | None:
        if self.price is None:
            return None
        return self.price * self.total_units

    @property
    def pnl(self) -> float | None:
        if self.market_value is None:
            return None
        return self.market_value - self.total_cost

    @property
    def pnl_pct(self) -> float | None:
        if self.pnl is None or self.total_cost == 0:
            return None
        return self.pnl / self.total_cost

    def fee_summary(self) -> dict[str, float | None]:
        if self.market_value is None:
            return {"comm": None, "sec": None, "finra": None, "total_fees": None}

        fees = self.fee_calculator.total_fees(self.platform, self.total_units, self.market_value)
        return {
            "comm": round(fees["comm"], 2),
            "sec": round(fees["sec"], 4),
            "finra": round(fees["finra"], 4),
            "total_fees": round(fees["total_fees"], 2),
        }

    @property
    def net_pnl(self) -> float | None:
        if self.pnl is None:
            return None
        fees = self.fee_summary()
        if fees["total_fees"] is None:
            return None
        return round(self.pnl - fees["total_fees"], 2)

    def to_dict(self) -> dict[str, float | str | None]:
        fees = self.fee_summary()
        return {
            "ticker": self.ticker,
            "name": self.name,
            "platform": self.platform,
            "type": self.asset_type,
            "units": round(self.total_units, 4),
            "cost_usd": round(self.total_cost, 2),
            "price": round(self.price, 2) if self.price is not None else None,
            "value_usd": round(self.market_value, 2) if self.market_value is not None else None,
            "pnl_usd": round(self.pnl, 2) if self.pnl is not None else None,
            "pnl_pct": round(self.pnl_pct * 100, 2) if self.pnl_pct is not None else None,
            "comm": fees["comm"],
            "sec": fees["sec"],
            "finra": fees["finra"],
            "total_fees": fees["total_fees"],
            "net_pnl_usd": self.net_pnl,
        }


class Portfolio:
    def __init__(self, positions: Iterable[Position], fx_ticker: str = "EURUSD=X") -> None:
        self.positions = list(positions)
        self.fx_ticker = fx_ticker
        rate, exemption = get_cgt_params(COUNTRY)
        self.cgt_calculator = CGTCalculator(rate, exemption, COUNTRY)
        self.fee_calculator = FeeCalculator()

    @classmethod
    def from_definition(cls, portfolio_definition: dict[str, dict]) -> "Portfolio":
        positions = []
        for ticker, info in portfolio_definition.items():
            lots = [Lot(date, cost, units) for date, cost, units in info["lots"]]
            positions.append(
                Position(
                    ticker=ticker,
                    name=info["name"],
                    platform=info["platform"],
                    asset_type=info["type"],
                    lots=lots,
                )
            )
        return cls(positions)

    def update_prices(self, prices: dict[str, float | None]) -> None:
        for position in self.positions:
            position.price = prices.get(position.ticker)

    def as_dict(self, eur_usd: float) -> dict[str, object]:
        stocks = [position.to_dict() for position in self.positions]
        valid_stocks = [stock for stock in stocks if stock["value_usd"] is not None]

        total_cost = sum(stock["cost_usd"] for stock in valid_stocks)
        total_value = sum(stock["value_usd"] for stock in valid_stocks)
        total_fees = sum(stock["total_fees"] for stock in valid_stocks)
        total_pnl = sum(stock["pnl_usd"] for stock in valid_stocks)

        ibkr_value = sum(stock["value_usd"] for stock in valid_stocks if stock["platform"] == "IBKR")
        fx_fee = self.fee_calculator.fx_fee(ibkr_value)
        cgt_info = self.cgt_calculator.compute(total_pnl, eur_usd)

        net_cash_usd = total_value - total_fees - fx_fee - cgt_info["cgt_usd"]

        return {
            "stocks": stocks,
            "eur_usd": round(eur_usd, 4),
            "as_of": datetime_now(),
            "totals": {
                "cost_usd": round(total_cost, 2),
                "value_usd": round(total_value, 2),
                "pnl_usd": round(total_pnl, 2),
                "total_fees": round(total_fees, 2),
                "fx_fee": round(fx_fee, 2),
                "net_pnl_eur": cgt_info["net_pnl_eur"],
                "taxable_eur": cgt_info["taxable_eur"],
                "cgt_eur": cgt_info["cgt_eur"],
                "cgt_usd": cgt_info["cgt_usd"],
                "net_cash_usd": round(net_cash_usd, 2),
                "net_cash_eur": round(net_cash_usd / eur_usd, 2),
            },
        }


def datetime_now() -> str:
    from datetime import datetime
    return datetime.now().strftime("%d %b %Y  %H:%M:%S")
