from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from datetime import datetime

app = FastAPI(
    title="US Federal Budget API",
    description="US federal budget data including deficit/surplus, revenue, spending, and national debt. Powered by FRED.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

SERIES = {
    "deficit":          {"id": "FYFSD",       "name": "Federal Surplus/Deficit",              "unit": "Millions of USD", "frequency": "Annual"},
    "revenue":          {"id": "FYONET",       "name": "Federal Net Receipts (Revenue)",       "unit": "Millions of USD", "frequency": "Annual"},
    "spending":         {"id": "FYONGDA188S",  "name": "Federal Outlays (Spending)",           "unit": "% of GDP",        "frequency": "Annual"},
    "national_debt":    {"id": "GFDEBTN",      "name": "Federal Debt: Total Public Debt",      "unit": "Millions of USD", "frequency": "Quarterly"},
    "debt_pct_gdp":     {"id": "GFDEGDQ188S",  "name": "Federal Debt to GDP",                 "unit": "% of GDP",        "frequency": "Quarterly"},
    "interest_expense": {"id": "FYOIGDA188S",  "name": "Federal Interest Payments",           "unit": "% of GDP",        "frequency": "Annual"},
    "defense_spending": {"id": "FYFSGDA188S",  "name": "Federal Surplus/Deficit % GDP",       "unit": "% of GDP",        "frequency": "Annual"},
    "tax_receipts":     {"id": "W006RC1Q027SBEA","name":"Federal Tax Receipts",                "unit": "Billions of USD", "frequency": "Quarterly"},
}


async def fetch_fred(series_id: str, limit: int = 20):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.get(FRED_BASE, params=params)
        data = res.json()
    obs = data.get("observations", [])
    return [
        {"date": o["date"], "value": float(o["value"]) if o["value"] != "." else None}
        for o in obs
        if o.get("value") != "."
    ]


@app.get("/")
def root():
    return {
        "api": "US Federal Budget API",
        "version": "1.0.0",
        "provider": "GlobalData Store",
        "source": "FRED - Federal Reserve Bank of St. Louis",
        "endpoints": ["/summary", "/deficit", "/revenue", "/spending", "/national-debt", "/debt-gdp", "/interest", "/tax-receipts"],
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/summary")
async def summary(limit: int = Query(default=10, ge=1, le=50)):
    """All federal budget indicators snapshot"""
    results = {}
    for key, meta in SERIES.items():
        results[key] = await fetch_fred(meta["id"], limit)
    formatted = {
        key: {
            "name": SERIES[key]["name"],
            "unit": SERIES[key]["unit"],
            "frequency": SERIES[key]["frequency"],
            "data": results[key],
        }
        for key in SERIES
    }
    return {
        "country": "United States",
        "source": "FRED - Federal Reserve Bank of St. Louis",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "indicators": formatted,
    }


@app.get("/deficit")
async def deficit(limit: int = Query(default=20, ge=1, le=80)):
    """Federal budget surplus or deficit (millions USD, positive = surplus)"""
    data = await fetch_fred("FYFSD", limit)
    return {"indicator": "Federal Surplus/Deficit", "series_id": "FYFSD", "unit": "Millions of USD", "frequency": "Annual", "note": "Positive = surplus, Negative = deficit", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/revenue")
async def revenue(limit: int = Query(default=20, ge=1, le=80)):
    """Federal net receipts (total government revenue)"""
    data = await fetch_fred("FYONET", limit)
    return {"indicator": "Federal Net Receipts (Revenue)", "series_id": "FYONET", "unit": "Millions of USD", "frequency": "Annual", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/spending")
async def spending(limit: int = Query(default=20, ge=1, le=80)):
    """Federal outlays (total government spending, % of GDP)"""
    data = await fetch_fred("FYONGDA188S", limit)
    return {"indicator": "Federal Outlays (Spending)", "series_id": "FYONGDA188S", "unit": "% of GDP", "frequency": "Annual", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/national-debt")
async def national_debt(limit: int = Query(default=20, ge=1, le=80)):
    """Federal debt: total public debt outstanding"""
    data = await fetch_fred("GFDEBTN", limit)
    return {"indicator": "Federal Debt: Total Public Debt", "series_id": "GFDEBTN", "unit": "Millions of USD", "frequency": "Quarterly", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/debt-gdp")
async def debt_gdp(limit: int = Query(default=20, ge=1, le=80)):
    """Federal debt as a percent of GDP"""
    data = await fetch_fred("GFDEGDQ188S", limit)
    return {"indicator": "Federal Debt to GDP", "series_id": "GFDEGDQ188S", "unit": "% of GDP", "frequency": "Quarterly", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/interest")
async def interest(limit: int = Query(default=20, ge=1, le=80)):
    """Federal interest payments on public debt (% of GDP)"""
    data = await fetch_fred("FYOIGDA188S", limit)
    return {"indicator": "Federal Interest Payments", "series_id": "FYOIGDA188S", "unit": "% of GDP", "frequency": "Annual", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}


@app.get("/tax-receipts")
async def tax_receipts(limit: int = Query(default=20, ge=1, le=80)):
    """Federal tax receipts (billions USD)"""
    data = await fetch_fred("W006RC1Q027SBEA", limit)
    return {"indicator": "Federal Tax Receipts", "series_id": "W006RC1Q027SBEA", "unit": "Billions of USD", "frequency": "Quarterly", "source": "FRED", "updated_at": datetime.utcnow().isoformat() + "Z", "data": data}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/":
        return await call_next(request)
    key = request.headers.get("X-RapidAPI-Key", "")
    if not key:
        return JSONResponse(status_code=401, content={"detail": "Missing X-RapidAPI-Key header"})
    return await call_next(request)
