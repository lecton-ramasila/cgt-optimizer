TAX_RATE = 0.33


def allocate_taxes(positions, fx_at_purchase, fx_current):
    net_pnls = [pos["total_pnl_eur"] for pos in positions]
    total_positive = sum(p for p in net_pnls if p > 0)
    total_net = sum(net_pnls)
    total_tax = TAX_RATE * max(total_net, 0.0)

    for pos in positions:
        if total_positive > 0 and pos["total_pnl_eur"] > 0:
            pos["tax_eur"] = total_tax * (pos["total_pnl_eur"] / total_positive)
        else:
            pos["tax_eur"] = 0.0

        pos["net_cash_eur"] = pos["adjusted_value_eur"] - pos["tax_eur"]
        pos["action"] = determine_action(pos, total_positive, fx_at_purchase, fx_current)

    return positions


def determine_action(position, total_positive_gain, fx_at_purchase, fx_current):
    fx_tailwind = fx_current > fx_at_purchase
    strong_proceeds = position["net_cash_eur"] > max(50.0, 0.02 * position["adjusted_value_eur"])
    loss_harvest = position["total_pnl_eur"] < 0 and total_positive_gain > 0

    if loss_harvest:
        return "Sell"
    if strong_proceeds and fx_tailwind and position["total_pnl_eur"] >= 0:
        return "Sell"
    return "Hold"
