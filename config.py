"""Static portfolio definition and application defaults."""

import os
from dotenv import load_dotenv

load_dotenv()


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return int(default)


FX_TICKER = os.getenv("FX_TICKER", "EURUSD=X")
DEFAULT_EUR_USD = _env_float("EUR_USD_FALLBACK", 1.13)
PORT = _env_int("PORT", 5000)
COUNTRY = os.getenv("COUNTRY", "Ireland")

CGT_RATE = _env_float("CGT_RATE", 0.33)
CGT_EXEMPTION_EUR = _env_float("CGT_EXEMPTION_EUR", 1270.0)

SA_CGT_RATE = _env_float("SA_CGT_RATE", 0.18)
SA_EXEMPTION_USD = _env_float("SA_EXEMPTION_USD", 2500.0)

IBKR_COMM_RATE = _env_float("IBKR_COMM_RATE", 0.005)
IBKR_COMM_MIN = _env_float("IBKR_COMM_MIN", 1.00)
IBKR_COMM_MAX_PC = _env_float("IBKR_COMM_MAX_PC", 0.01)
IBKR_FX_RATE = _env_float("IBKR_FX_RATE", 0.00002)
IBKR_FX_MIN = _env_float("IBKR_FX_MIN", 2.00)

MS_FLAT_FEE = _env_float("MS_FLAT_FEE", 9.99)
EP_COMM_PC = _env_float("EP_COMM_PC", 0.001)

SEC_FEE_RATE = _env_float("SEC_FEE_RATE", 0.000008)
FINRA_RATE = _env_float("FINRA_RATE", 0.000166)
FINRA_MAX = _env_float("FINRA_MAX", 8.30)

# Each lot is a tuple: (date, cost_per_share, units)
PORTFOLIO = {
    "GOOGL": {
        "name": "Alphabet",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-23", 340.909752, 32.26660),
            ("2026-04-27", 346.015187, 37.57060),
            ("2026-04-30", 368.492692, 260.00000),
        ],
    },
    "BRK-B": {
        "name": "Berkshire Hathaway",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-23", 467.654636, 23.52160),
            ("2026-04-27", 469.600908, 18.95220),
            ("2026-04-30", 477.000000,  2.00000),
        ],
    },
    "LLY": {
        "name": "Eli Lilly",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-30", 925.930000, 20.00000),
        ],
    },
    "MSFT": {
        "name": "Microsoft",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-20", 418.990000,  0.24000),
            ("2026-04-23", 419.897850, 39.29520),
            ("2026-04-27", 422.511273, 42.60240),
            ("2026-04-30", 402.765000, 100.00000),
        ],
    },
    "JNJ": {
        "name": "Johnson & Johnson",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-24", 227.660000,  57.00000),
            ("2026-04-24", 227.680000,   0.10260),
            ("2026-04-30", 230.780000,  50.00000),
        ],
    },
    "KO": {
        "name": "Coca-Cola",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-24",  76.650000,  91.00000),
            ("2026-04-24",  76.650000,   0.32420),
            ("2026-04-30",  78.930000, 100.00000),
        ],
    },
    "NVDA": {
        "name": "NVIDIA",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-23", 208.780000,  62.00000),
            ("2026-04-23", 208.775000,   0.26650),
        ],
    },
    "V": {
        "name": "Visa",
        "platform": "IBKR",
        "type": "Stock",
        "lots": [
            ("2026-04-24", 311.600000, 17.00000),
            ("2026-04-24", 311.030000,  0.65200),
        ],
    },
    "AMZN": {
        "name": "Amazon",
        "platform": "Morgan Stanley",
        "type": "RSU",
        "lots": [
            ("2021-09-15", 170.97,  40),
            ("2022-03-15", 146.14,  60),
            ("2022-09-15", 127.72,  67),
            ("2023-03-15",  94.22,  67),
            ("2023-05-15", 110.36,  36),
            ("2023-05-22", 115.09,   9),
            ("2023-09-15", 141.01,  67),
            ("2023-11-15", 144.21,  36),
            ("2024-05-15", 184.35,  49),
            ("2024-05-15", 184.35,  32),
            ("2024-05-21", 181.52,  28),
            ("2024-11-15", 203.09,  59),
            ("2024-11-15", 203.09,  21),
            ("2024-11-21", 198.46,  19),
            ("2025-05-15", 204.18,  18),
            ("2025-05-21", 201.57,  19),
        ],
    },
    "IBM": {
        "name": "IBM",
        "platform": "Equate Plus",
        "type": "ESPP",
        "lots": [
            ("2026-01-28", 248.26, 5.04064),
            ("2026-02-23", 202.27, 6.35032),
            ("2026-03-25", 210.83, 5.91879),
        ],
    },
}
