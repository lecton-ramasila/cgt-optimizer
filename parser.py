import csv
from io import StringIO

REQUIRED_FIELDS = [
    "date",
    "name",
    "ticker",
    "broker",
    "asset_type",
    "currency",
    "price_usd",
    "quantity",
    "cost_usd",
    "pnl_usd",
]

FIELD_SYNONYMS = {
    "date": ["date"],
    "name": ["name"],
    "ticker": ["ticker", "symbol"],
    "broker": ["broker", "platform"],
    "asset_type": ["asset_type", "type"],
    "currency": ["currency"],
    "price_usd": ["price_usd", "cost/unit", "cost per unit", "price"],
    "quantity": ["quantity", "units"],
    "cost_usd": ["cost_usd", "purchase value", "purchase_value", "cost", "purchasevalue"],
    "value_usd": ["value_usd", "current value", "current_value", "value", "market value", "currentvalue"],
    "pnl_usd": ["pnl_usd", "pnl", "profit", "profit/loss", "profitloss"],
    "fee": ["fee", "fees"],
    "current_price_usd": ["current_price_usd", "current price", "market_price_usd", "market price", "price/usd"],
}


def normalize_field_name(name):
    if not name:
        return ""
    return "".join(ch for ch in name.lower() if ch.isalnum())


def build_header_map(headers):
    return {normalize_field_name(name): name for name in headers if name and name.strip()}


def find_header(header_map, *names):
    for name in names:
        match = header_map.get(normalize_field_name(name))
        if match:
            return match.lower()
    return None


def parse_number(value, default=0.0):
    if value is None:
        return default
    text = str(value).strip().replace(",", "").replace("$", "")
    if text == "":
        return default
    try:
        return float(text)
    except ValueError:
        return default


def parse_broker_csv(csv_text):
    errors = []
    reader = csv.DictReader(StringIO(csv_text))
    if reader.fieldnames is None:
        return [], ["CSV file is empty or malformed."]

    header_map = build_header_map(reader.fieldnames)
    missing = [field for field in REQUIRED_FIELDS if field != "value_usd" and find_header(header_map, *FIELD_SYNONYMS[field]) is None]
    if find_header(header_map, *FIELD_SYNONYMS["value_usd"]) is None and find_header(header_map, *FIELD_SYNONYMS["current_price_usd"]) is None:
        missing.append("value_usd or current_price_usd")
    if missing:
        return [], [f"Missing required CSV columns: {', '.join(missing)}."]

    field_map = {field: find_header(header_map, *FIELD_SYNONYMS[field]) for field in FIELD_SYNONYMS}
    fee_present = field_map.get("fee") is not None
    aggregated = {}

    for row_index, raw_row in enumerate(reader, start=1):
        row = {key.lower(): (value or "").strip() for key, value in raw_row.items()}
        if not any(row.values()):
            continue

        ticker = row.get(field_map["ticker"], "").upper()
        if not ticker:
            errors.append(f"Row {row_index}: ticker is required.")
            continue

        currency = row.get(field_map["currency"], "USD").upper()
        if currency != "USD":
            errors.append(f"Row {row_index}: only USD based trades are supported; found {currency}.")
            continue

        quantity = parse_number(row.get(field_map["quantity"]), 0.0)
        cost_usd = parse_number(row.get(field_map["cost_usd"]), 0.0)
        value_usd = parse_number(row.get(field_map["value_usd"]), 0.0)
        current_price_usd = parse_number(row.get(field_map.get("current_price_usd"), ""), 0.0)
        fee_usd = parse_number(row.get(field_map.get("fee"), ""), 1.0 if not fee_present else 0.0)
        if not fee_present:
            fee_usd = 1.0

        if quantity > 0 and value_usd <= 0 and current_price_usd > 0:
            value_usd = current_price_usd * quantity

        market_value_usd = current_price_usd * quantity if current_price_usd > 0 else value_usd

        if ticker not in aggregated:
            aggregated[ticker] = {
                "ticker": ticker,
                "name": row.get(field_map["name"], "").strip() or ticker,
                "broker": row.get(field_map["broker"], "").strip(),
                "asset_type": row.get(field_map["asset_type"], "").strip(),
                "quantity": 0.0,
                "cost_usd": 0.0,
                "value_usd": 0.0,
                "market_value_usd": 0.0,
                "current_price_usd": 0.0,
                "fees_usd": 0.0,
            }

        aggregated[ticker]["quantity"] += quantity
        aggregated[ticker]["cost_usd"] += cost_usd
        aggregated[ticker]["value_usd"] += value_usd
        aggregated[ticker]["market_value_usd"] += market_value_usd
        if current_price_usd > 0:
            aggregated[ticker]["current_price_usd"] = current_price_usd
        aggregated[ticker]["fees_usd"] += fee_usd

    if not aggregated and not errors:
        errors.append("No valid rows found in the CSV.")

    return list(aggregated.values()), errors
