# US Federal Budget API

US federal budget data including deficit/surplus, government revenue, spending, national debt, debt-to-GDP ratio, interest payments, and tax receipts. Powered by FRED.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info and available endpoints |
| `GET /summary` | All budget indicators snapshot |
| `GET /deficit` | Federal surplus/deficit |
| `GET /revenue` | Federal net receipts (revenue) |
| `GET /spending` | Federal outlays (spending % of GDP) |
| `GET /national-debt` | Total public debt outstanding |
| `GET /debt-gdp` | Federal debt as % of GDP |
| `GET /interest` | Federal interest payments |
| `GET /tax-receipts` | Federal tax receipts |

## Data Source

FRED — Federal Reserve Bank of St. Louis
https://fred.stlouisfed.org

## Authentication

Requires `X-RapidAPI-Key` header via RapidAPI.
