"""Flask application entrypoint for the portfolio dashboard."""

from flask import Flask, jsonify, render_template_string

from config import PORTFOLIO, COUNTRY
from portfolio import Portfolio
from pricing import PriceFetcher


def create_app() -> Flask:
    app = Flask(__name__)
    portfolio = Portfolio.from_definition(PORTFOLIO)
    price_fetcher = PriceFetcher([position.ticker for position in portfolio.positions])

    cgt_rate_pct = int(portfolio.cgt_calculator.rate * 100)
    cgt_exemption = f"€{portfolio.cgt_calculator.exemption:,.0f}" if COUNTRY == "Ireland" else f"${portfolio.cgt_calculator.exemption:,.0f}"
    country_display = "South Africa" if COUNTRY == "SouthAfrica" else COUNTRY

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio · Live PnL</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg:       #080c14;
    --surface:  #0d1321;
    --card:     #111827;
    --border:   #1e2d45;
    --accent:   #3b82f6;
    --gain:     #10b981;
    --loss:     #ef4444;
    --gold:     #f59e0b;
    --muted:    #475569;
    --text:     #e2e8f0;
    --dim:      #94a3b8;
    --mono:     'DM Mono', monospace;
    --sans:     'Syne', sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: var(--sans); min-height: 100vh; }}
  header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.5rem 2rem; border-bottom: 1px solid var(--border);
    background: var(--surface);
  }}
  .logo {{ font-size: 1.1rem; font-weight: 800; letter-spacing: -.02em; color: var(--text); }}
  .logo span {{ color: var(--accent); }}
  .meta {{ font-family: var(--mono); font-size: .72rem; color: var(--muted); text-align: right; line-height: 1.6; }}
  .dot {{ display: inline-block; width: 7px; height: 7px; border-radius: 50%; background: var(--gain);
         box-shadow: 0 0 8px var(--gain); animation: pulse 2s ease-in-out infinite; margin-right: 5px; }}
  @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.4}} }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 1px;
          background: var(--border); border-bottom: 1px solid var(--border); }}
  .kpi {{ background: var(--surface); padding: 1.25rem 1.5rem; }}
  .kpi-label {{ font-family: var(--mono); font-size: .65rem; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin-bottom: .4rem; }}
  .kpi-val {{ font-size: 1.45rem; font-weight: 700; letter-spacing: -.03em; }}
  .kpi-sub {{ font-family: var(--mono); font-size: .7rem; color: var(--muted); margin-top: .2rem; }}
  .pos {{ color: var(--gain); }} .neg {{ color: var(--loss); }} .gold {{ color: var(--gold); }}
  main {{ padding: 2rem; display: flex; flex-direction: column; gap: 2rem; }}
  .table-wrap {{ overflow-x: auto; border-radius: 8px; border: 1px solid var(--border); }}
  table {{ width: 100%; border-collapse: collapse; font-family: var(--mono); font-size: .75rem; }}
  thead th {{
    background: var(--card); padding: .75rem 1rem; text-align: right;
    font-size: .62rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted);
    white-space: nowrap; border-bottom: 1px solid var(--border);
  }}
  thead th:first-child, thead th:nth-child(2), thead th:nth-child(3) {{ text-align: left; }}
  tbody tr {{ border-bottom: 1px solid var(--border); transition: background .15s; }}
  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: rgba(59,130,246,.05); }}
  td {{ padding: .65rem 1rem; white-space: nowrap; }}
  td:not(:first-child):not(:nth-child(2)):not(:nth-child(3)) {{ text-align: right; }}
  .ticker {{ font-weight: 500; color: var(--accent); font-size: .8rem; }}
  .name {{ color: var(--dim); font-size: .72rem; }}
  .badge {{
    display: inline-block; padding: .1rem .45rem; border-radius: 3px; font-size: .6rem;
    letter-spacing: .06em; text-transform: uppercase; font-weight: 500;
  }}
  .badge-ibkr   {{ background: #1e3a5f; color: #60a5fa; }}
  .badge-ms     {{ background: #1a3a2a; color: #34d399; }}
  .badge-ep     {{ background: #3a2a10; color: #fbbf24; }}
  .badge-rsu    {{ background: #2a1a3a; color: #c084fc; }}
  .badge-espp   {{ background: #3a2010; color: #fb923c; }}
  .pnl-cell {{ font-weight: 500; }}
  tfoot td {{ background: var(--card); font-weight: 600; border-top: 2px solid var(--border); }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px,1fr)); gap: 1rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.25rem 1.5rem; }}
  .card-title {{ font-size: .65rem; letter-spacing: .1em; text-transform: uppercase; color: var(--muted);
                margin-bottom: 1rem; font-family: var(--mono); }}
  .line {{ display: flex; justify-content: space-between; align-items: center; padding: .3rem 0;
          border-bottom: 1px solid rgba(255,255,255,.04); }}
  .line:last-child {{ border-bottom: none; }}
  .line-label {{ font-size: .72rem; color: var(--dim); }}
  .line-val {{ font-family: var(--mono); font-size: .78rem; font-weight: 500; }}
  .line-sep {{ border-top: 1px solid var(--border); margin: .5rem 0; }}
  .line.total .line-label {{ font-weight: 600; color: var(--text); font-size: .76rem; }}
  .line.total .line-val {{ font-size: .9rem; }}
  .refresh-btn {{
    background: var(--accent); color: #fff; border: none; padding: .6rem 1.4rem;
    border-radius: 5px; cursor: pointer; font-family: var(--sans); font-weight: 600;
    font-size: .8rem; transition: opacity .2s;
  }}
  .refresh-btn:hover {{ opacity: .8; }}
  .refresh-btn:disabled {{ opacity: .4; cursor: default; }}
  .note {{ font-family: var(--mono); font-size: .62rem; color: var(--muted); line-height: 1.7; max-width: 800px; }}
</style>
</head>
<body>

<header>
  <div class="logo">PORTFOLIO <span>·</span> LIVE PnL</div>
  <div class="meta">
    <span class="dot"></span><span id="as-of">Loading…</span><br>
    EUR/USD <span id="fx-rate">—</span>
    &nbsp;|&nbsp; {country_display} CGT {cgt_rate_pct}% &nbsp;|&nbsp; {cgt_exemption} exemption
  </div>
</header>

<div class="kpis" id="kpis">
  <div class="kpi"><div class="kpi-label">Market Value</div><div class="kpi-val" id="k-val">—</div></div>
  <div class="kpi"><div class="kpi-label">Cost Basis</div><div class="kpi-val" id="k-cost">—</div></div>
  <div class="kpi"><div class="kpi-label">Gross PnL</div><div class="kpi-val" id="k-pnl">—</div></div>
  <div class="kpi"><div class="kpi-label">Total Broker Fees</div><div class="kpi-val" id="k-fees">—</div></div>
  <div class="kpi"><div class="kpi-label">CGT Liability</div><div class="kpi-val neg" id="k-cgt">—</div></div>
  <div class="kpi"><div class="kpi-label">Net Cash (EUR)</div><div class="kpi-val gold" id="k-net">—</div></div>
</div>

<main>

  <div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Ticker</th><th>Name</th><th>Platform / Type</th>
            <th>Shares</th><th>Cost Basis</th><th>Price</th><th>Market Value</th>
            <th>PnL (USD)</th><th>PnL %</th>
            <th>Commission</th><th>SEC + FINRA</th><th>Total Fees</th>
            <th>Net PnL</th>
          </tr>
        </thead>
        <tbody id="tbody"></tbody>
        <tfoot id="tfoot"></tfoot>
      </table>
    </div>
  </div>

  <div class="cards">

    <div class="card">
      <div class="card-title">Fees Breakdown</div>
      <div class="line"><span class="line-label">IBKR commissions</span><span class="line-val" id="s-ibkr-comm">—</span></div>
      <div class="line"><span class="line-label">SEC + FINRA (all platforms)</span><span class="line-val" id="s-regfees">—</span></div>
      <div class="line"><span class="line-label">Morgan Stanley flat fee</span><span class="line-val" id="s-ms">—</span></div>
      <div class="line"><span class="line-label">Equate Plus commission</span><span class="line-val" id="s-ep">—</span></div>
      <div class="line"><span class="line-label">IBKR FX conversion (0.002%)</span><span class="line-val" id="s-fx">—</span></div>
      <div class="line-sep"></div>
      <div class="line total"><span class="line-label">Total Fees</span><span class="line-val" id="s-tot-fees">—</span></div>
    </div>

    <div class="card">
      <div class="card-title">{country_display} CGT Calculation</div>
      <div class="line"><span class="line-label">Net PnL (USD)</span><span class="line-val" id="t-pnl-usd">—</span></div>
      <div class="line"><span class="line-label">Net PnL (EUR)</span><span class="line-val" id="t-pnl-eur">—</span></div>
      <div class="line"><span class="line-label">Annual exemption</span><span class="line-val">− {cgt_exemption}</span></div>
      <div class="line"><span class="line-label">Taxable gain (EUR)</span><span class="line-val" id="t-taxable">—</span></div>
      <div class="line-sep"></div>
      <div class="line total"><span class="line-label">CGT @ {cgt_rate_pct}% (EUR)</span><span class="line-val neg" id="t-cgt-eur">—</span></div>
      <div class="line total"><span class="line-label">CGT (USD equiv.)</span><span class="line-val neg" id="t-cgt-usd">—</span></div>
    </div>

    <div class="card">
      <div class="card-title">Bottom Line</div>
      <div class="line"><span class="line-label">Gross proceeds</span><span class="line-val" id="b-gross">—</span></div>
      <div class="line"><span class="line-label">Less: all broker fees</span><span class="line-val neg" id="b-fees">—</span></div>
      <div class="line"><span class="line-label">Less: CGT</span><span class="line-val neg" id="b-cgt">—</span></div>
      <div class="line-sep"></div>
      <div class="line total"><span class="line-label">Net cash (USD)</span><span class="line-val gold" id="b-net-usd">—</span></div>
      <div class="line total"><span class="line-label">Net cash (EUR)</span><span class="line-val gold" id="b-net-eur">—</span></div>
    </div>

  </div>

  <div style="display:flex; align-items:center; gap:1.5rem; flex-wrap:wrap;">
    <button class="refresh-btn" id="refresh-btn" onclick="load()">↻ Refresh Prices</button>
    <div class="note">
      Assumptions: IBKR $0.005/share (min $1, max 1% trade value) · SEC $0.000008/$ proceeds · FINRA $0.000166/share (max $8.30) ·
      Morgan Stanley $9.99 flat · Equate Plus 0.1% · IBKR FX 0.002% of IBKR proceeds (min $2) ·
      RSU cost = FMV at vest (income tax already paid at vest — PnL shown is CGT-eligible gain only) ·
      Not tax advice — consult a professional.
    </div>
  </div>

</main>

<script>
const $ = id => document.getElementById(id);
const usd = (v, decimals=0) => v == null ? '—' : '$' + v.toLocaleString('en-US', {{minimumFractionDigits:decimals, maximumFractionDigits:decimals}});
const eur = (v, decimals=0) => v == null ? '—' : '€' + v.toLocaleString('en-US', {{minimumFractionDigits:decimals, maximumFractionDigits:decimals}});
const pct = v => v == null ? '—' : (v >= 0 ? '+' : '') + v.toFixed(1) + '%';
const signed = (v, fmt) => v == null ? '—' : (v >= 0 ? '+' : '') + fmt(v);
const cls = v => v == null ? '' : v >= 0 ? 'pos' : 'neg';

function badge(platform, type) {{
  const pm = platform === 'IBKR' ? 'badge-ibkr' : platform === 'Morgan Stanley' ? 'badge-ms' : 'badge-ep';
  const tp = type === 'RSU' ? 'badge-rsu' : type === 'ESPP' ? 'badge-espp' : '';
  return `<span class="badge ${{pm}}">${{platform}}</span> ${{tp ? `<span class="badge ${{tp}}">${{type}}</span>` : ''}}`;
}}

async function load() {{
  const btn = $('refresh-btn');
  btn.disabled = true; btn.textContent = 'Fetching…';
  try {{
    const res = await fetch('/api/data');
    if (!res.ok) {{
      throw new Error(`HTTP ${{res.status}}`);
    }}
    const d = await res.json();
    render(d);
  }} catch(e) {{
    alert('Price fetch failed: ' + e);
  }} finally {{
    btn.disabled = false; btn.textContent = '↻ Refresh Prices';
  }}
}}

function render(d) {{
  $('as-of').textContent = d.as_of;
  $('fx-rate').textContent = d.eur_usd.toFixed(4);

  const t = d.totals;
  $('k-val').textContent  = usd(t.value_usd);
  $('k-cost').textContent = usd(t.cost_usd);
  $('k-pnl').innerHTML    = `<span class="${{cls(t.pnl_usd)}}">${{signed(t.pnl_usd, usd)}}</span>`;
  $('k-fees').textContent = usd(t.total_fees + t.fx_fee, 2);
  $('k-cgt').textContent  = eur(t.cgt_eur);
  $('k-net').textContent  = eur(t.net_cash_eur);

  // Table
  const tbody = $('tbody');
  tbody.innerHTML = '';
  for (const s of d.stocks) {{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="ticker">${{s.ticker}}</td>
      <td class="name">${{s.name}}</td>
      <td>${{badge(s.platform, s.type)}}</td>
      <td>${{s.units.toLocaleString('en-US', {{maximumFractionDigits:4}})}}</td>
      <td>${{usd(s.cost_usd)}}</td>
      <td>${{usd(s.price, 2)}}</td>
      <td>${{usd(s.value_usd)}}</td>
      <td class="pnl-cell ${{cls(s.pnl_usd)}}">${{signed(s.pnl_usd, usd)}}</td>
      <td class="${{cls(s.pnl_pct)}}">${{pct(s.pnl_pct)}}</td>
      <td>${{usd(s.comm, 2)}}</td>
      <td>${{usd(s.sec != null && s.finra != null ? s.sec + s.finra : null, 2)}}</td>
      <td>${{usd(s.total_fees, 2)}}</td>
      <td class="pnl-cell ${{cls(s.net_pnl_usd)}}">${{signed(s.net_pnl_usd, usd)}}</td>
    `;
    tbody.appendChild(tr);
  }}

  $('tfoot').innerHTML = `<tr>
    <td colspan="3">TOTAL</td>
    <td></td>
    <td>${{usd(t.cost_usd)}}</td>
    <td></td>
    <td>${{usd(t.value_usd)}}</td>
    <td class="${{cls(t.pnl_usd)}}">${{signed(t.pnl_usd, usd)}}</td>
    <td></td>
    <td></td><td></td>
    <td>${{usd(t.total_fees, 2)}}</td>
    <td class="${{cls(t.pnl_usd - t.total_fees)}}">${{signed(t.pnl_usd - t.total_fees, usd)}}</td>
  </tr>`;

  // Cards — fees
  const stocks = d.stocks;
  const ibkr = stocks.filter(s => s.platform === 'IBKR');
  const ms   = stocks.find(s => s.platform === 'Morgan Stanley');
  const ep   = stocks.find(s => s.platform === 'Equate Plus');

  $('s-ibkr-comm').textContent = usd(ibkr.reduce((a,s) => a + (s.comm||0), 0), 2);
  const reg = stocks.reduce((a,s) => a + ((s.sec||0) + (s.finra||0)), 0);
  $('s-regfees').textContent = usd(reg, 2);
  $('s-ms').textContent = usd(ms?.comm, 2);
  $('s-ep').textContent = usd(ep?.comm, 2);
  $('s-fx').textContent = usd(t.fx_fee, 2);
  $('s-tot-fees').textContent = usd(t.total_fees + t.fx_fee, 2);

  // Cards — CGT
  $('t-pnl-usd').textContent = usd(t.pnl_usd);
  $('t-pnl-eur').textContent = eur(t.net_pnl_eur);
  $('t-taxable').textContent = eur(t.taxable_eur);
  $('t-cgt-eur').textContent = eur(t.cgt_eur);
  $('t-cgt-usd').textContent = usd(t.cgt_usd);

  // Cards — bottom line
  $('b-gross').textContent  = usd(t.value_usd);
  $('b-fees').textContent   = '− ' + usd(t.total_fees + t.fx_fee, 2);
  $('b-cgt').textContent    = '− ' + usd(t.cgt_usd);
  $('b-net-usd').textContent = usd(t.net_cash_usd);
  $('b-net-eur').textContent = eur(t.net_cash_eur);
}}

load();
</script>
</body>
</html>
"""

    @app.route("/")
    def index():
        return html

    @app.route("/api/data")
    def api_data():
        prices, eur_usd = price_fetcher.fetch()
        portfolio.update_prices(prices)
        return jsonify(portfolio.as_dict(eur_usd))

    return app


app = create_app()