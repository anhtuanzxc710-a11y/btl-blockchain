"""Integer carbon ledger; cash and prices in normalized monetary units."""
from dataclasses import dataclass
from decimal import Decimal
from random import Random

import networkx as nx

from .inputs import COUNTS

@dataclass
class Firm:
    kind: str
    size: int
    base_ea: int = 0
    ea: int = 0
    cc: int = 0
    cash: float = 0
    margin: float = 0
    fixed: float = 0
    weak_ticks: int = 0
    active: bool = True

def initialize(ranges, seed):
    rng = Random(seed)
    firms = []
    for group, count in COUNTS.items():
        def ratio(key):
            lo, hi = ranges[group, key]
            return lo + (hi-lo)*Decimal(str(rng.random()))
        for _ in range(count):
            name = "issuance" if group == "green" else "demand"
            size = rng.randint(*ranges[group, name])
            firm = Firm(group, size)
            if group != "green":
                firm.base_ea = int(size * ratio("quota_ratio"))
                firm.cash = float(size * ratio("cash_ratio"))
                firm.margin = float(ratio("margin"))
                firm.fixed = float(ratio("fixed_cost"))
            firms.append(firm)
    nodes = list(range(len(firms)))
    rng.shuffle(nodes)
    carbon = nx.relabel_nodes(nx.barabasi_albert_graph(len(nodes), 3, seed=seed), dict(enumerate(nodes)))
    supply = nx.DiGraph()
    supply.add_nodes_from(nodes)
    smes = [i for i,f in enumerate(firms) if f.kind == "sme"]
    for buyer, firm in enumerate(firms):
        if firm.kind != "large":
            continue
        suppliers = rng.sample(smes, rng.randint(6,10))
        weights = [rng.uniform(0.5,1.5) for _ in suppliers]
        for seller,w in zip(suppliers,weights):
            supply.add_edge(seller,buyer,weight=w/sum(weights))
    return firms, carbon, supply

def gini(holdings):
    total = sum(holdings)
    if not total:
        return float("nan")
    n = len(holdings)
    return sum((2*i-n-1)*v for i,v in enumerate(sorted(holdings),1))/(n*total)

def settle_market(firms, carbon, neighbors, order, needs, caps, price_anchor):
    volume, value = 0, 0.0
    for buyer in order:
        b = firms[buyer]
        if not b.active or b.kind == "green":
            continue
        for asset in ("ea", "cc"):
            for seller in neighbors[buyer]:
                s = firms[seller]
                need = needs[buyer] - b.ea - min(b.cc,caps[buyer])
                if asset == "cc":
                    need = min(need, caps[buyer]-b.cc)
                if need <= 0:
                    break
                if not s.active:
                    continue
                offer = max(0,s.ea-needs[seller]) if asset == "ea" else (s.cc if s.kind=="green" else 0)
                if not offer:
                    continue
                # Bilateral quotes depend on counterparties' degrees and buyer resources.
                reference = price_anchor if asset == "ea" else 0.75*price_anchor
                ask = reference*(0.85+0.15*carbon.degree[seller]/(carbon.degree[seller]+carbon.degree[buyer]))
                bid = reference*(1+0.10*min(2,max(0,b.cash)/b.size))
                if bid < ask:
                    continue
                price = (ask+bid)/2
                qty = min(need,offer,int(max(0,b.cash)/price))
                if qty:
                    setattr(s,asset,getattr(s,asset)-qty)
                    setattr(b,asset,getattr(b,asset)+qty)
                    s.cash += qty*price
                    b.cash -= qty*price
                    if asset=="ea":
                        volume += qty
                        value += qty*price
    return volume,value

def simulate(ranges, seed, scenario):
    if scenario not in {"S0","S1"}:
        raise ValueError(scenario)
    firms,carbon,supply = initialize(ranges,seed)
    edges = [(s,b,w) for s,b,w in supply.edges.data("weight")]
    weight_total = sum(w for _,_,w in edges)
    for tick in range(1,101):
        # Always draw for every node, even after exit: S0 and S1 use paired draws.
        rng = Random(seed*1000+tick)
        order = list(range(len(firms)))
        rng.shuffle(order)
        neighbors = {i: list(carbon[i]) for i in order}
        for group in neighbors.values():
            rng.shuffle(group)
        inputs = [1.0]*len(firms)
        for s,b,w in edges:
            if not firms[s].active:
                inputs[b] -= w
        needs,caps = [],[]
        for i,f in enumerate(firms):
            shock = rng.uniform(0.96,1.04)
            emitting = f.active and f.kind!="green"
            needs.append(round(f.size*max(0,inputs[i])*shock) if emitting else 0)
            allocated = f.base_ea if emitting else 0
            if scenario=="S1" and tick>=30:
                allocated = allocated*70//100
            f.ea += allocated
            caps.append(allocated*30//100)
            if f.kind=="green":
                f.cc += f.size
        stocks = [f.ea for f in firms if f.active]
        price_anchor = min(5,max(0.25,sum(needs)/max(1,sum(stocks))))
        volume,value = settle_market(firms,carbon,neighbors,order,needs,caps,price_anchor)
        for i,f in enumerate(firms):
            if not f.active or f.kind=="green":
                continue
            ea_used = min(needs[i],f.ea)
            cc_used = min(f.cc,caps[i],needs[i]-ea_used)
            f.ea -= ea_used
            f.cc -= cc_used
            output = ea_used+cc_used
            f.cash += output*f.margin-f.fixed*f.size
            fraction = output/f.size
            f.weak_ticks = f.weak_ticks+1 if fraction<0.78 else 0
            if f.cash < -0.15*f.size or (f.weak_ticks>=5 and f.cash<f.size):
                f.active=False
        inventory = [f.ea+f.cc for f in firms]
        row = dict(scenario=scenario,seed=seed,tick=tick,ea_price_index=value/volume if volume else float("nan"),
                   ea_trade_volume=volume,gini=gini(inventory),
                   sme_survival=sum(f.active for f in firms if f.kind=="sme")/COUNTS["sme"],
                   supply_loss=sum(w for s,_,w in edges if not firms[s].active)/weight_total)
        for group in COUNTS:
            row["balance_"+group] = sum(v for v,f in zip(inventory,firms) if f.kind==group)
        yield row
