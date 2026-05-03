"""Irish CGT calculation logic."""

from config import CGT_EXEMPTION_EUR, CGT_RATE, COUNTRY, SA_CGT_RATE, SA_EXEMPTION_USD


def get_cgt_params(country: str) -> tuple[float, float]:
    if country == "Ireland":
        return CGT_RATE, CGT_EXEMPTION_EUR
    elif country == "SouthAfrica":
        return SA_CGT_RATE, SA_EXEMPTION_USD
    else:
        raise ValueError(f"Unsupported country: {country}")


class CGTCalculator:
    def __init__(self, rate: float, exemption: float, country: str) -> None:
        self.rate = rate
        self.exemption = exemption
        self.country = country

    def compute(self, net_pnl_usd: float, eur_usd: float, zar_usd: float = 0.054) -> dict[str, float | str]:
        if self.country == "Ireland":
            net_pnl_local = net_pnl_usd / eur_usd
            taxable_local = max(0.0, net_pnl_local - self.exemption)
            cgt_local = taxable_local * self.rate
            cgt_usd = cgt_local * eur_usd
            local_currency = "EUR"
        elif self.country == "SouthAfrica":
            net_pnl_local = net_pnl_usd / zar_usd
            taxable_local = max(0.0, net_pnl_local - self.exemption)
            cgt_local = taxable_local * self.rate
            cgt_usd = cgt_local * zar_usd
            local_currency = "ZAR"
        else:
            raise ValueError(f"Unsupported country: {self.country}")

        return {
            "net_pnl_local": round(net_pnl_local, 2),
            "taxable_local": round(taxable_local, 2),
            "cgt_local": round(cgt_local, 2),
            "local_currency": local_currency,
            "cgt_usd": round(cgt_usd, 2),
        }
