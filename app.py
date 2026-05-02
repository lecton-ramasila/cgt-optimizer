from flask import Flask, render_template, request
from parser import parse_broker_csv
from fx import enrich_positions
from tax import allocate_taxes
from yahoo import fetch_live_prices

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

@app.route("/", methods=["GET", "POST"])
def index():
    positions = []
    errors = []
    fx_current = None
    fx_at_purchase = 1.0

    if request.method == "POST":
        csv_file = request.files.get("csv_file")
        fx_current_raw = request.form.get("fx_current", "").strip()
        fx_at_purchase_raw = request.form.get("fx_at_purchase", "").strip() or "1.00"

        if not csv_file or csv_file.filename == "":
            errors.append("Please upload a broker CSV file.")

        if not fx_current_raw:
            errors.append("Current EUR/USD FX rate is required.")

        try:
            fx_current = float(fx_current_raw)
            if fx_current <= 0:
                errors.append("Current EUR/USD FX rate must be greater than zero.")
        except (ValueError, TypeError):
            errors.append("Current EUR/USD FX rate must be a valid number.")

        try:
            fx_at_purchase = float(fx_at_purchase_raw)
            if fx_at_purchase <= 0:
                errors.append("FX rate at purchase must be greater than zero.")
        except (ValueError, TypeError):
            errors.append("FX rate at purchase must be a valid number.")

        if not errors:
            content = csv_file.stream.read().decode("utf-8-sig")
            rows, parse_errors = parse_broker_csv(content)
            if parse_errors:
                errors.extend(parse_errors)
            else:
                tickers = [row["ticker"] for row in rows]
                live_prices = fetch_live_prices(tickers)
                positions = enrich_positions(rows, fx_at_purchase, fx_current, live_prices)
                positions = allocate_taxes(positions, fx_at_purchase, fx_current)

    return render_template(
        "index.html",
        positions=positions,
        errors=errors,
        fx_current=fx_current,
        fx_at_purchase=fx_at_purchase,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
