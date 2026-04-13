import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ---- FETCH DATA ----
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    income_stmt = stock.financials
    balance_sheet = stock.balance_sheet
    cash_flow = stock.cashflow
    return stock, info, income_stmt, balance_sheet, cash_flow

ticker = input("Enter a stock ticker (e.g. AAPL): ").upper()
stock, info, income_stmt, balance_sheet, cash_flow = get_stock_data(ticker)

print("\nCompany: " + str(info.get("longName", "N/A")))
print("Sector: " + str(info.get("sector", "N/A")))
print("Current Price: $" + str(info.get("currentPrice", "N/A")))

# ---- METRICS ----
def calculate_metrics(info, cash_flow):
    metrics = {}
    metrics["P/E Ratio"] = info.get("trailingPE", "N/A")
    metrics["Forward P/E"] = info.get("forwardPE", "N/A")
    metrics["EV/EBITDA"] = info.get("enterpriseToEbitda", "N/A")
    metrics["Price/Book"] = info.get("priceToBook", "N/A")
    metrics["Gross Margin"] = str(round(info.get("grossMargins", 0) * 100, 1)) + "%"
    metrics["Net Margin"] = str(round(info.get("profitMargins", 0) * 100, 1)) + "%"
    metrics["Return on Equity"] = str(round(info.get("returnOnEquity", 0) * 100, 1)) + "%"
    metrics["Debt/Equity"] = info.get("debtToEquity", "N/A")
    metrics["Current Ratio"] = info.get("currentRatio", "N/A")
    try:
        fcf = cash_flow.loc["Free Cash Flow"].iloc[0]
        metrics["Free Cash Flow"] = "$" + str(round(fcf / 1e9, 2)) + "B"
    except:
        metrics["Free Cash Flow"] = "N/A"
    return metrics

metrics = calculate_metrics(info, cash_flow)
print("\n--- KEY FINANCIAL METRICS ---")
for key, value in metrics.items():
    print(key + ": " + str(value))

# ---- DCF VALUATION ----
def simple_dcf(info, cash_flow):
    try:
        fcf = cash_flow.loc["Free Cash Flow"].iloc[0]
        growth_rate = 0.10
        terminal_growth = 0.03
        discount_rate = 0.10
        shares = info.get("sharesOutstanding", None)
        if not shares:
            return "N/A"
        projected_fcf = []
        for year in range(1, 6):
            projected_fcf.append(fcf * (1 + growth_rate) ** year)
        terminal_value = projected_fcf[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
        pv_fcfs = sum([cf / (1 + discount_rate) ** i for i, cf in enumerate(projected_fcf, 1)])
        pv_terminal = terminal_value / (1 + discount_rate) ** 5
        intrinsic_value = (pv_fcfs + pv_terminal) / shares
        return round(intrinsic_value, 2)
    except Exception as e:
        return "Could not calculate: " + str(e)

dcf_value = simple_dcf(info, cash_flow)
current_price = info.get("currentPrice", 0)
print("\n--- DCF VALUATION ---")
print("Estimated Intrinsic Value: $" + str(dcf_value))
print("Current Market Price: $" + str(current_price))
if isinstance(dcf_value, float):
    if dcf_value > current_price:
        print("Signal: Potentially UNDERVALUED")
    else:
        print("Signal: Potentially OVERVALUED")

# ---- CHARTS ----
def create_charts(ticker, income_stmt, cash_flow, dcf_value, current_price):
    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(ticker + " - Equity Research Summary", fontsize=16, fontweight="bold")
    gs = gridspec.GridSpec(2, 2, figure=fig)

    ax1 = fig.add_subplot(gs[0, 0])
    try:
        revenue = income_stmt.loc["Total Revenue"].dropna() / 1e9
        ax1.bar(revenue.index.year, revenue.values, color="steelblue")
        ax1.set_title("Revenue (Billions $)")
        ax1.set_xlabel("Year")
    except:
        ax1.set_title("Revenue - Data unavailable")

    ax2 = fig.add_subplot(gs[0, 1])
    try:
        net_income = income_stmt.loc["Net Income"].dropna() / 1e9
        colors = ["green" if x > 0 else "red" for x in net_income.values]
        ax2.bar(net_income.index.year, net_income.values, color=colors)
        ax2.set_title("Net Income (Billions $)")
        ax2.set_xlabel("Year")
    except:
        ax2.set_title("Net Income - Data unavailable")

    ax3 = fig.add_subplot(gs[1, 0])
    try:
        fcf = cash_flow.loc["Free Cash Flow"].dropna() / 1e9
        ax3.plot(fcf.index.year, fcf.values, marker="o", color="purple", linewidth=2)
        ax3.set_title("Free Cash Flow (Billions $)")
        ax3.set_xlabel("Year")
        ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
    except:
        ax3.set_title("FCF - Data unavailable")

    ax4 = fig.add_subplot(gs[1, 1])
    if isinstance(dcf_value, float):
        bars = ax4.bar(["Intrinsic Value (DCF)", "Market Price"],
                       [dcf_value, current_price],
                       color=["green", "steelblue"])
        ax4.set_title("DCF Value vs Market Price ($)")
        for bar, val in zip(bars, [dcf_value, current_price]):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                     "$" + str(val), ha="center", fontweight="bold")
    else:
        ax4.set_title("DCF - Could not calculate")

    plt.tight_layout()
    plt.savefig(ticker + "_analysis.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("\nChart saved as " + ticker + "_analysis.png")

create_charts(ticker, income_stmt, cash_flow, dcf_value, current_price)

# ---- EXPORT TO EXCEL ----
def export_to_excel(ticker, metrics, dcf_value, current_price):
    with pd.ExcelWriter(ticker + "_equity_research.xlsx", engine="openpyxl") as writer:
        metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
        metrics_df.to_excel(writer, sheet_name="Key Metrics", index=False)
        signal = "Undervalued" if isinstance(dcf_value, float) and dcf_value > current_price else "Overvalued"
        valuation_df = pd.DataFrame({
            "Metric": ["DCF Intrinsic Value", "Current Market Price", "Signal"],
            "Value": ["$" + str(dcf_value), "$" + str(current_price), signal]
        })
        valuation_df.to_excel(writer, sheet_name="Valuation", index=False)
    print("Excel report saved as " + ticker + "_equity_research.xlsx")

export_to_excel(ticker, metrics, dcf_value, current_price)