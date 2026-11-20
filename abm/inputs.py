"""Load a group's calibration ranges. Keep carbon quantities as integers."""
import csv
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from pathlib import Path

COUNTS = {"large": 20, "sme": 140, "green": 40}
EMITTERS = ("large", "sme")
FIELDS = {
    **{(g, "demand"): "carbon" for g in EMITTERS},
    **{(g, "quota_ratio"): "ratio" for g in EMITTERS},
    **{(g, "cash_ratio"): "ratio" for g in EMITTERS},
    **{(g, "margin"): "ratio" for g in EMITTERS},
    **{(g, "fixed_cost"): "ratio" for g in EMITTERS},
    ("green", "issuance"): "carbon",
}
COLUMNS = ["group", "parameter", "low", "high", "unit", "evidence",
           "source_ref", "reference_period", "model_use"]
EVIDENCE = {"observed", "proxy", "assumption"}

def read_inputs(path):
    rows = {}
    units = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != set(COLUMNS):
            raise ValueError(f"Expected columns: {COLUMNS}")
        for i, row in enumerate(reader, 2):
            key = (row["group"], row["parameter"])
            if key not in FIELDS or key in rows:
                raise ValueError(f"Row {i}: unknown or duplicate key {key}")
            if any(not row[c] or not row[c].strip() for c in COLUMNS):
                raise ValueError(f"Row {i}: missing field")
            try:
                lo, hi = Decimal(row["low"]), Decimal(row["high"])
            except InvalidOperation as exc:
                raise ValueError(f"Row {i}: invalid decimal") from exc
            if not all(x.is_finite() for x in (lo, hi)) or not 0 <= lo <= hi:
                raise ValueError(f"Row {i}: invalid range")
            if row["evidence"] not in EVIDENCE:
                raise ValueError(f"Row {i}: unknown evidence")
            if FIELDS[key] == "carbon":
                unit = row["unit"]
                if unit not in {"tCO2e_per_tick", "model_unit_per_tick"}:
                    raise ValueError(f"Row {i}: invalid carbon unit")
                units.add(unit)
                factor = 1000 if unit == "tCO2e_per_tick" else 1
                lo, hi = [int((x * factor).to_integral_value(rounding=ROUND_FLOOR))
                          for x in (lo, hi)]
                if not lo:
                    raise ValueError(f"Row {i}: carbon quantity falls below one unit")
            elif row["unit"] != "ratio":
                raise ValueError(f"Row {i}: expected ratio")
            rows[key] = (lo, hi)
    if rows.keys() != FIELDS.keys() or len(units) != 1:
        raise ValueError(f"Missing keys {FIELDS.keys() - rows.keys()} or mixed carbon units")
    return rows, units.pop()
