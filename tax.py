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

    def compute(self, net_pnl_usd: float, eur_usd: float) -> dict[str, float]:
        if self.country == "Ireland":
            net_pnl_base = net_pnl_usd / eur_usd
            taxable_base = max(0.0, net_pnl_base - self.exemption)
            cgt_base = taxable_base * self.rate
            cgt_usd = cgt_base * eur_usd
        elif self.country == "SouthAfrica":
            taxable_usd = max(0.0, net_pnl_usd - self.exemption)
            cgt_usd = taxable_usd * self.rate
            cgt_base = cgt_usd / eur_usd
            net_pnl_base = net_pnl_usd / eur_usd
            taxable_base = taxable_usd / eur_usd
        else:
            raise ValueError(f"Unsupported country: {self.country}")

        return {
            "net_pnl_eur": round(net_pnl_base, 2),
            "taxable_eur": round(taxable_base, 2),
            "cgt_eur": round(cgt_base, 2),
            "cgt_usd": round(cgt_usd, 2),
        }
