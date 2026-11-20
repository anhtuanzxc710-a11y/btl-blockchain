"""Run paired scenarios, export series and figures."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .inputs import read_inputs
from .model import simulate

METRICS = {"ea_price_index":"Giá khớp EA (chỉ số)", "gini":"Gini tồn kho EA + CC",
           "sme_survival":"Tỷ lệ SME còn hoạt động", "supply_loss":"Tỷ trọng nguồn cung bị mất"}
BALANCES = ["balance_large","balance_sme","balance_green"]
SEEDS = tuple(range(101,113))

def export(frame, target):
    frame.to_csv(target/"timeseries.csv",index=False)
    group = frame.groupby(["scenario","tick"])
    means = group[list(METRICS)+BALANCES].mean()
    means.to_csv(target/"by_tick.csv")
    post_seed = frame[frame.tick>=30].groupby(["scenario","seed"])[list(METRICS)+BALANCES].mean()
    post_seed.to_csv(target/"postshock_by_seed.csv")
    post = post_seed.groupby("scenario").agg(["mean","std"])
    post.columns = [f"{name}_{stat}" for name,stat in post.columns]
    post.to_csv(target/"postshock_summary.csv")
    paired = post_seed.loc["S1"]-post_seed.loc["S0"]
    paired.to_csv(target/"paired_difference.csv")
    for key,title in METRICS.items():
        fig,ax = plt.subplots(figsize=(8,4.3))
        for scenario,color in (("S0","#18665b"),("S1","#aa4e23")):
            series = means.loc[scenario,key]
            ax.plot(series.index,series,color=color,label=scenario)
        ax.axvline(30,color="gray",ls="--",lw=1)
        ax.set(xlabel="Chu kỳ", ylabel=title, title=title+" · trung bình các seed")
        ax.legend()
        ax.grid(alpha=.2)
        fig.tight_layout()
        fig.savefig(target/(key+".png"),dpi=150)
        plt.close(fig)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=Path("data/parameters_demo.csv"))
    parser.add_argument("--out",type=Path,default=Path("results/demo"))
    args=parser.parse_args()
    ranges,unit=read_inputs(args.input)
    target=args.out
    target.mkdir(parents=True,exist_ok=True)
    frame=pd.DataFrame(row for seed in SEEDS for scenario in ("S0","S1")
                       for row in simulate(ranges,seed,scenario))
    export(frame,target)
    meta=dict(input_file=args.input.name,input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
              source_unit=unit,ledger_unit="0.001 tCO2e" if unit=="tCO2e_per_tick" else "model_unit",
              seeds=SEEDS,ticks=100,agents=200,shock_tick=30,scenarios=["S0","S1"])
    (target/"run.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    print(f"{len(frame)} rows written to {target}")

if __name__=="__main__":
    main()
