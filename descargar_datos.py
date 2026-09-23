"""Descarga precios diarios de un universo amplio de acciones USA (~2,100) + macro.
Guarda en /datos: CSV para las 35 series originales y parquet por año para el universo."""
import os, time
import pandas as pd, yfinance as yf, financedatabase as fd

INICIO = "2015-01-01"
os.makedirs("datos", exist_ok=True)

# ---- 1) Series base (compatibilidad con la versión anterior)
BASE = ["MCD","KO","PEP","MNST","PG","COST","WMT","JNJ","NVDA","MSFT","AVGO","AMD","META","TSM","GOOGL","PLTR",
        "CCJ","VST","VRT","CRWD","RKLB","AXON","IONQ","SMR","ANET","CLS",
        "^VIX","^IRX","DX-Y.NYB","HYG","IEF","^GSPC","SPY","QQQ","IWM"]
df = yf.download(BASE, start=INICIO, auto_adjust=True, progress=False)
for campo in ["Close","High","Low","Open","Volume"]:
    df[campo].to_csv(f"datos/{campo.lower()}.csv")
print("Base OK:", df["Close"].index[-1].date())

# ---- 2) Universo amplio (reglas objetivas, reproducibles)
eq = fd.Equities().select(country="United States")
eq = eq[eq.exchange.isin(["NMS","NYQ","NGM","NCM","ASE"]) & (eq.currency=="USD")]
eq = eq[~eq.index.str.contains(r"[\.\-\^]", regex=True)]
eq = eq[~eq.sector.isin(["Financials","Real Estate","Utilities"])]
eq = eq[eq.market_cap.isin(["Mega Cap","Large Cap","Mid Cap","Small Cap"])]
eq[["name","sector","industry","market_cap"]].to_csv("datos/universo.csv")
tickers = sorted(eq.index.tolist())
print("Universo:", len(tickers))

# ---- 3) Descarga por lotes
partes = []
for i in range(0, len(tickers), 150):
    lote = tickers[i:i+150]
    for intento in range(3):
        try:
            d = yf.download(lote, start=INICIO, auto_adjust=True, progress=False, threads=True)
            partes.append(d[["Close","High","Volume"]]); break
        except Exception as e:
            print("reintento", i, e); time.sleep(10)
    print(f"lote {i//150+1}/{(len(tickers)-1)//150+1}")
full = pd.concat(partes, axis=1)

# ---- 4) Guardar parquet por año (solo cambia el año en curso cada día)
for campo in ["Close","High","Volume"]:
    tabla = full[campo].astype("float32")
    for anio, g in tabla.groupby(tabla.index.year):
        g.to_parquet(f"datos/{campo.lower()}_{anio}.parquet", compression="zstd")
print("Universo OK:", full["Close"].index[-1].date(), full["Close"].shape)
