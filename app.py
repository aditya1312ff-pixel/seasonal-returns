import sys, os
import pandas as pd

def load_data(asset):
    d = "data" if os.path.exists("data") else "."
    for f in os.listdir(d):
        if f.lower().startswith(asset.lower()) and f.endswith(".csv"):
            df = pd.read_csv(os.path.join(d, f))
            df.columns = [c.strip().lower() for c in df.columns]
            dc = next((c for c in df.columns if c in ("time","date")), None)
            pc = next((c for c in df.columns if c in ("close","close price","settle")), None)
            if not dc or not pc:
                raise ValueError(f"{f}: need a date col and a close col")
            for fmt in ("%d-%m-%Y","%Y-%m-%d","%m/%d/%Y"):
                try:
                    df[dc] = pd.to_datetime(df[dc], format=fmt); break
                except Exception:
                    continue
            else:
                df[dc] = pd.to_datetime(df[dc])
            df = df.rename(columns={dc:"time", pc:"close"}).sort_values("time").reset_index(drop=True)
            return df
    raise FileNotFoundError(f"No CSV found starting with '{asset}' in {d}")

def snap(df, s, roll):
    t = pd.Timestamp(s)
    c = df[df["time"] >= t] if roll == "forward" else df[df["time"] <= t]
    return (c.iloc[0] if roll == "forward" else c.iloc[-1]) if len(c) else None

def main():
    if len(sys.argv) < 4:
        print("Usage: python app.py <asset> <MM-DD entry> <MM-DD exit> [forward|backward]")
        sys.exit(1)
    asset, emd, xmd = sys.argv[1], sys.argv[2], sys.argv[3]
    roll = sys.argv[4] if len(sys.argv) > 4 else "forward"
    df = load_data(asset)
    cross = int(xmd.split("-")[0]) < int(emd.split("-")[0])
    rows = []
    for y in range(df["time"].dt.year.min(), df["time"].dt.year.max() + 1):
        e = snap(df, f"{y}-{emd}", roll)
        x = snap(df, f"{y + cross}-{xmd}", roll)
        if e is None or x is None or x["time"] <= e["time"]: continue
        r = (x["close"]/e["close"] - 1) * 100
        rows.append({"Year":y,"Entry":e["time"].date(),"In$":round(e["close"],4),
                     "Exit":x["time"].date(),"Out$":round(x["close"],4),
                     "Return%":round(r,2),"Days":(x["time"]-e["time"]).days})
    out = pd.DataFrame(rows)
    if out.empty:
        print("No trades."); return
    print(out.to_string(index=False))
    print(f"\nTrades {len(out)} | Win {(out['Return%']>0).mean()*100:.1f}% | "
          f"Avg {out['Return%'].mean():.2f}% | Med {out['Return%'].median():.2f}% | "
          f"Best {out['Return%'].max():.2f}% | Worst {out['Return%'].min():.2f}%")

if __name__ == "__main__":
    main()
