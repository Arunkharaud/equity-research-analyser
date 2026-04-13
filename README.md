# Equity Research Analyser

A Python tool that automates equity research by pulling live financial data, calculating key valuation metrics, and running a Discounted Cash Flow (DCF) model to estimate a company's intrinsic value versus its current market price.

## What It Does

- Fetches real-time financial statements (income statement, balance sheet, cash flow) for any publicly listed company using its stock ticker
- Calculates the core financial ratios used by equity analysts
- Runs a simplified DCF valuation model to estimate intrinsic value per share
- Generates a 4-panel chart visualising revenue, net income, free cash flow, and DCF vs market price
- Exports a full report to Excel

## Key Metrics Calculated

| Metric | What It Measures |
|---|---|
| P/E Ratio | How much investors pay per $1 of earnings |
| Forward P/E | P/E based on projected future earnings |
| EV/EBITDA | Company value relative to operating earnings |
| Price/Book | Market value relative to book value |
| Gross Margin | Profitability after cost of goods sold |
| Net Margin | Profitability after all expenses |
| Return on Equity | How efficiently management generates profit from shareholders equity |
| Debt/Equity | Financial leverage and risk |
| Current Ratio | Short term liquidity |
| Free Cash Flow | Cash remaining after capital expenditure |

## DCF Model

The DCF model projects free cash flow over a 5 year horizon using the following assumptions:

- **Revenue growth rate:** 10% per year
- **Terminal growth rate:** 3% (long run perpetual growth)
- **Discount rate:** 10% (required rate of return)

These are simplified assumptions intended as a baseline. In practice, growth rates and discount rates would be tailored to each company based on its sector, risk profile, and historical performance.

The model outputs an estimated intrinsic value per share and flags whether the stock appears undervalued or overvalued relative to its current market price.

## Technologies Used

- **Python 3**
- **yfinance** — fetches live financial data from Yahoo Finance
- **pandas** — data processing and manipulation
- **matplotlib** — data visualisation and chart generation
- **openpyxl** — Excel report export

## How To Run

1. Clone the repository
2. Install dependencies:
```
pip3 install yfinance pandas matplotlib openpyxl
```
3. Run the script:
```
python3 equity_analyser.py
```
4. Enter any stock ticker when prompted (e.g. AAPL, MSFT, TSLA, JPM)

## Example Output

Running the analyser on Apple Inc. (AAPL) produces:
- A full metrics table including P/E, EV/EBITDA, margins, and free cash flow
- A DCF intrinsic value estimate compared against the current market price
- A 4-panel chart saved as `AAPL_analysis.png`
- An Excel report saved as `AAPL_equity_research.xlsx`

## Limitations

- DCF assumptions are fixed and simplified — real valuations require company-specific research
- Financial data is sourced from Yahoo Finance which may occasionally have gaps or delays
- The model works best for large cap companies with stable, positive free cash flow
- Short term sentiment, macro factors, and qualitative considerations are not captured

## Author

Built as a personal finance project to automate fundamental equity analysis and deepen understanding of financial statement analysis and valuation methodology.
