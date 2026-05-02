"""Brokerage and conversion fee calculations."""

from config import (
    EP_COMM_PC,
    FINRA_MAX,
    FINRA_RATE,
    IBKR_COMM_MAX_PC,
    IBKR_COMM_MIN,
    IBKR_COMM_RATE,
    IBKR_FX_MIN,
    IBKR_FX_RATE,
    MS_FLAT_FEE,
    SEC_FEE_RATE,
)


class FeeCalculator:
    def commission(self, platform: str, shares: float, value: float) -> float:
        if platform == "IBKR":
            return max(IBKR_COMM_MIN, min(IBKR_COMM_RATE * shares, IBKR_COMM_MAX_PC * value))
        if platform == "Morgan Stanley":
            return MS_FLAT_FEE
        return max(1.00, EP_COMM_PC * value)

    def regulatory_fees(self, shares: float, value: float) -> tuple[float, float]:
        sec = SEC_FEE_RATE * value
        finra = min(FINRA_RATE * shares, FINRA_MAX)
        return round(sec, 4), round(finra, 4)

    def total_fees(self, platform: str, shares: float, value: float) -> dict[str, float]:
        commission = self.commission(platform, shares, value)
        sec, finra = self.regulatory_fees(shares, value)
        return {
            "comm": round(commission, 4),
            "sec": sec,
            "finra": finra,
            "total_fees": round(commission + sec + finra, 4),
        }

    def fx_fee(self, ibkr_value: float) -> float:
        return max(IBKR_FX_MIN, ibkr_value * IBKR_FX_RATE)
