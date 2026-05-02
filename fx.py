def enrich_positions(positions, fx_at_purchase, fx_current, live_prices=None):
    live_prices = live_prices or {}
    enriched = []
    for position in positions:
        cost_usd = position["cost_usd"]
        fees_usd = position["fees_usd"]
        current_price_usd = live_prices.get(position["ticker"], position.get("current_price_usd", 0.0))
        quantity = position["quantity"]

        if current_price_usd > 0:
            market_value_usd = current_price_usd * quantity
        else:
            market_value_usd = position.get("market_value_usd", position.get("value_usd", 0.0))

        cost_eur = cost_usd / fx_at_purchase
        value_eur = market_value_usd / fx_current
        fees_eur = fees_usd / fx_current

        adjusted_cost_eur = cost_eur + fees_eur / 2.0
        adjusted_value_eur = value_eur - fees_eur / 2.0

        market_pnl_eur = (market_value_usd - cost_usd) / fx_current
        total_pnl_eur = adjusted_value_eur - adjusted_cost_eur
        fx_pnl_eur = total_pnl_eur - market_pnl_eur

        market_price_usd = current_price_usd if current_price_usd > 0 else (market_value_usd / quantity if quantity else 0.0)
        market_price_eur = market_price_usd / fx_current if fx_current else 0.0
        cost_per_unit_usd = cost_usd / quantity if quantity else 0.0
        cost_per_unit_eur = cost_eur / quantity if quantity else 0.0
        cost_basis_usd = cost_usd
        cost_basis_eur = cost_eur
        market_value_eur = value_eur

        enriched.append(
            {
                "ticker": position["ticker"],
                "name": position.get("name", position["ticker"]),
                "broker": position.get("broker", ""),
                "asset_type": position.get("asset_type", ""),
                "quantity": quantity,
                "cost_basis_usd": cost_basis_usd,
                "cost_basis_eur": cost_basis_eur,
                "cost_per_unit_usd": cost_per_unit_usd,
                "cost_per_unit_eur": cost_per_unit_eur,
                "market_value_usd": market_value_usd,
                "market_value_eur": market_value_eur,
                "adjusted_cost_eur": adjusted_cost_eur,
                "adjusted_value_eur": adjusted_value_eur,
                "fees_eur": fees_eur,
                "market_pnl_eur": market_pnl_eur,
                "fx_pnl_eur": fx_pnl_eur,
                "total_pnl_eur": total_pnl_eur,
                "market_price_usd": market_price_usd,
                "market_price_eur": market_price_eur,
                "net_cash_eur": adjusted_value_eur,
                "fx_at_purchase": fx_at_purchase,
                "fx_current": fx_current,
            }
        )

    return enriched
