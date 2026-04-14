import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

st.set_page_config(page_title="Equity Research Analyser", layout="wide")
st.title("Equity Research Analyser")
st.write("Enter a stock ticker to generate a full equity research report")

ticker = st.text_input("Stock Ticker (e.g. AAPL, TSLA, JPM)").upper()

if ticker:
    with st.spinner("Fetching financial data..."):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow

            # Company header
            st.header(info.get("longName", ticker))
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
            col2.metric("Sector", info.get("sector", "N/A"))
            col3.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:.1f}B")

            # Key metrics
            st.subheader("Key Financial Metrics")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("P/E Ratio", round(info.get("trailingPE", 0), 2))
            col2.metric("Forward P/E", round(info.get("forwardPE", 0), 2))
            col3.metric("EV/EBITDA", round(info.get("enterpriseToEbitda", 0), 2))
            col4.metric("Price/Book", round(info.get("priceToBook", 0), 2))
            col5.metric("Current Ratio", round(info.get("currentRatio", 0), 2))

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Gross Margin", f"{info.get('grossMargins', 0)*100:.1f}%")
            col2.metric("Net Margin", f"{info.get('profitMargins', 0)*100:.1f}%")
            col3.metric("Return on Equity", f"{info.get('returnOnEquity', 0)*100:.1f}%")
            col4.metric("Debt/Equity", round(info.get("debtToEquity", 0), 2))

            # DCF Valuation
            st.subheader("DCF Valuation")
            try:
                fcf = cash_flow.loc["Free Cash Flow"].iloc[0]
                growth_rate = 0.10
                terminal_growth = 0.03
                discount_rate = 0.10
                shares = info.get("sharesOutstanding", None)
                projected_fcf = [fcf * (1 + growth_rate) ** year for year in range(1, 6)]
                terminal_value = projected_fcf[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
                pv_fcfs = sum([cf / (1 + discount_rate) ** i for i, cf in enumerate(projected_fcf, 1)])
                pv_terminal = terminal_value / (1 + discount_rate) ** 5
                intrinsic_value = round((pv_fcfs + pv_terminal) / shares, 2)
                current_price = info.get("currentPrice", 0)

                col1, col2, col3 = st.columns(3)
                col1.metric("Intrinsic Value (DCF)", f"${intrinsic_value}")
                col2.metric("Current Market Price", f"${current_price}")
                if intrinsic_value > current_price:
                    col3.metric("Signal", "Undervalued", delta="Buy Signal")
                else:
                    col3.metric("Signal", "Overvalued", delta="Caution", delta_color="inverse")
            except:
                st.warning("DCF could not be calculated for this ticker")

            # Charts
            st.subheader("Financial Charts")
            fig = plt.figure(figsize=(14, 8))
            gs = gridspec.GridSpec(2, 2, figure=fig)

            ax1 = fig.add_subplot(gs[0, 0])
            try:
                revenue = income_stmt.loc["Total Revenue"].dropna() / 1e9
                ax1.bar(revenue.index.year, revenue.values, color="steelblue")
                ax1.set_title("Revenue (Billions $)")
            except:
                ax1.set_title("Revenue - Data unavailable")

            ax2 = fig.add_subplot(gs[0, 1])
            try:
                net_income = income_stmt.loc["Net Income"].dropna() / 1e9
                colors = ["green" if x > 0 else "red" for x in net_income.values]
                ax2.bar(net_income.index.year, net_income.values, color=colors)
                ax2.set_title("Net Income (Billions $)")
            except:
                ax2.set_title("Net Income - Data unavailable")

            ax3 = fig.add_subplot(gs[1, 0])
            try:
                fcf_chart = cash_flow.loc["Free Cash Flow"].dropna() / 1e9
                ax3.plot(fcf_chart.index.year, fcf_chart.values, marker="o", color="purple", linewidth=2)
                ax3.set_title("Free Cash Flow (Billions $)")
                ax3.axhline(0, color="black", linewidth=0.8, linestyle="--")
            except:
                ax3.set_title("FCF - Data unavailable")

            ax4 = fig.add_subplot(gs[1, 1])
            try:
                ax4.bar(["Intrinsic Value (DCF)", "Market Price"],
                        [intrinsic_value, current_price],
                        color=["green", "steelblue"])
                ax4.set_title("DCF Value vs Market Price ($)")
            except:
                ax4.set_title("DCF Chart - Data unavailable")

            plt.tight_layout()
            st.pyplot(fig)

        except Exception as e:
            st.error("Could not fetch data for this ticker. Please check it is valid and try again.")
