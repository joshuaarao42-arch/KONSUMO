import numpy as np
import pandas as pd
from .analytics import daily_series

def forecast_daily(resource, db_path, user_id=None):
    s=daily_series(resource,db_path,user_id=user_id)
    if len(s)<7: raise ValueError("at least 7 days of history are required")
    vals=s.to_numpy(float); window=min(7,len(vals)); avg=float(vals[-window:].mean())
    trend=float(np.polyfit(np.arange(min(30,len(vals))), vals[-min(30,len(vals)):],1)[0]) if len(vals)>1 else 0
    dates=pd.date_range(s.index[-1]+pd.Timedelta(days=1), periods=30, freq="D")
    pred=np.maximum(0, avg + trend*np.arange(1,31))
    return pd.Series(pred,index=dates), {"method":"moving-average + linear trend","mae":round(float(np.mean(np.abs(vals[-window:]-avg))),3)}

def forecast_all(db_path, user_id=None):
    return {r: forecast_daily(r,db_path,user_id=user_id)[0] for r in ("electricity","water")}
