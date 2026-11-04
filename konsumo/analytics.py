import numpy as np
import pandas as pd
from .config import TARIFFS
from .database import connect

def _frame(resource, db_path):
    with connect(db_path) as c: rows = pd.read_sql_query("SELECT * FROM consumption WHERE resource=? ORDER BY recorded_at", c, params=[resource])
    if rows.empty: return pd.DataFrame(columns=["recorded_at","amount","cost"])
    rows["recorded_at"] = pd.to_datetime(rows["recorded_at"]); return rows

def tiered_cost(amount, resource="electricity"):
    total=0.; prior=0.
    for cap, rate in TARIFFS[resource]:
        take=min(max(float(amount)-prior,0), cap-prior); total += take*rate; prior=cap
        if amount <= cap: break
    return round(total, 2)

def daily_series(resource, db_path):
    f=_frame(resource,db_path)
    if f.empty: return pd.Series(dtype=float)
    return f.set_index("recorded_at")["amount"].resample("D").sum()

def monthly_summary(resource, months=14, db_path=None):
    f=_frame(resource,db_path)
    if f.empty: return pd.DataFrame(columns=["usage","cost"])
    out=f.set_index("recorded_at").resample("MS").agg(usage=("amount","sum"),cost=("cost","sum"))
    return out.tail(months)

def usage_stats(resource, db_path):
    s=daily_series(resource,db_path)
    return {"resource":resource,"count":int(len(s)),"total":round(float(s.sum()),2),"average":round(float(s.mean() or 0),2),"maximum":round(float(s.max() or 0),2)}

def month_over_month(resource, db_path):
    m=monthly_summary(resource,2,db_path); return round(float(m.iloc[-1].usage/m.iloc[-2].usage-1),4) if len(m)>1 and m.iloc[-2].usage else 0

def detect_anomalies(resource, db_path):
    s=daily_series(resource,db_path); mean=s.mean(); std=s.std();
    if len(s)<3 or not std: return []
    return [{"date":d.strftime("%Y-%m-%d"),"amount":round(float(v),3),"z_score":round(float((v-mean)/std),2),"cost":tiered_cost(v,resource)} for d,v in s.items() if abs((v-mean)/std)>=2.5]
