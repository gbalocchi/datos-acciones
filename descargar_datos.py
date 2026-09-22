"""Descarga precios diarios (acciones + macro) y los guarda en /datos como CSV."""
import os
import yfinance as yf

TICKERS = [
    # defensivas
    "MCD", "KO", "PEP", "MNST", "PG", "COST", "WMT", "JNJ",
    # tech / IA
    "NVDA", "MSFT", "AVGO", "AMD", "META", "TSM", "GOOGL", "PLTR",
    # small / mid caps
    "CCJ", "VST", "VRT", "CRWD", "RKLB", "AXON", "IONQ", "SMR", "ANET", "CLS",
    # macro
    "^VIX", "^IRX", "DX-Y.NYB", "HYG", "IEF", "^GSPC", "SPY", "QQQ", "IWM",
]

os.makedirs("datos", exist_ok=True)
df = yf.download(TICKERS, start="2015-01-01", auto_adjust=True, progress=False)
for campo in ["Close", "High", "Low", "Open", "Volume"]:
    df[campo].to_csv(f"datos/{campo.lower()}.csv")
print("OK:", df["Close"].index[-1].date(), "-", df["Close"].shape)
