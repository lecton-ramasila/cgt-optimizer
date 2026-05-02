# CGT + FX Reality Engine (Ireland)

A minimal Flask web app to convert USD broker trades into EUR outcomes, account for FX movement, IBKR fees, and Irish CGT.

## Files

- `app.py` — Flask application entry point
- `parser.py` — CSV parsing and ticker-level aggregation
- `fx.py` — FX conversion and P/L decomposition
- `tax.py` — Irish CGT allocation and action guidance
- `templates/index.html` — single-page UI

## Usage

1. Install dependencies from `pyproject.toml`:
   ```bash
   python -m pip install -e .
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000`

## What it does

- Upload a USD-based broker CSV
- Enter current EUR/USD FX rate (required)
- Optionally enter FX rate at purchase (defaults to `1.00`)
- CSV can include an optional `current_price_usd` / `Current Price` column so the app can compute today’s market price and value clearly
- The app also pulls live ticker pricing from Yahoo Finance at runtime where available
- Outputs per-ticker EUR cost, value, market/FX P&L, fees, tax, and net cash
- Provides a simple Sell/Hold action recommendation

## Notes

- No database required
- No auth
- No live FX API integration
- Only USD/EUR tracked
