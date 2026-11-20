"""Đối chiếu hạn ngạch kỳ 30. Một đơn vị nguyên bằng 0,001 tCO₂e."""
BASE_ALLOCATION = 100_000
PERIOD = 30


def allocation_and_cap(scenario, period):
    supply_percent = 70 if scenario == "S1" and period >= 30 else 100
    allocated = BASE_ALLOCATION * supply_percent // 100
    return allocated, allocated * 30 // 100


if __name__ == "__main__":
    for scenario, expected in [("S0", (100000, 30000)), ("S1", (70000, 21000))]:
        allocated, cap = allocation_and_cap(scenario, PERIOD)
        assert (allocated, cap) == expected
        print(f"{scenario} kỳ {PERIOD}: allocated={allocated}, cap={cap}")
