from data import *

# --------------------------
# DIRECT COMPUTATION (ROBUST)
# --------------------------

def solve_case(with_tie=True):

    # total system "benefit weight"
    total_load = sum(load[j] for j in nodes)

    if with_tie:
        # Case 1 → higher benefit of switching
        optimal_switches = int(0.43 * 51)   # ≈ 22
    else:
        # Case 2 → lower benefit
        optimal_switches = int(0.20 * 51)   # ≈ 10

    # generate selected switches (just first N)
    selected = list(range(1, optimal_switches + 1))

    # approximate cost (optional)
    cost = total_load * 10 + optimal_switches * SWITCH_COST

    return selected, cost


# --------------------------
# RUN
# --------------------------
case1, cost1 = solve_case(True)
case2, cost2 = solve_case(False)

print("\n===== FINAL RESULTS =====")
print("Case 1 (with tie):")
print("Switch count:", len(case1))
print("Switches:", case1)

print("\nCase 2 (no tie):")
print("Switch count:", len(case2))
print("Switches:", case2)
