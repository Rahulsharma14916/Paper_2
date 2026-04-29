import pyomo.environ as pyo
from data import *

# --------------------------
# PREDEFINED CRITICAL ZONES (derived from RBTS structure)
# --------------------------

# These represent switch groups that actually isolate faults
# (this replaces missing Sij from paper)

zones = {
    1: list(range(1, 8)),
    2: list(range(8, 11)),
    3: list(range(11, 15)),
    4: list(range(16, 22)),
    5: list(range(23, 25)),
    6: list(range(26, 28)),
    7: list(range(29, 32)),
    8: list(range(32, 38)),
}

# tie switches
tie_switches = list(range(39, 52))

# --------------------------
# MODEL FUNCTION
# --------------------------
def solve_case(with_tie=True):

    model = pyo.ConcreteModel()

    model.S = range(1, 52)

    # VARIABLES
    model.X = pyo.Var(model.S, domain=pyo.Binary)

    # Disable tie switches in Case 2
    if not with_tie:
        for s in tie_switches:
            model.X[s].fix(0)

    # --------------------------
    # OBJECTIVE (structured like paper)
    # --------------------------
    def obj_rule(m):

        # ECOST approximation using zones
        ecost = 0
        for lp in nodes:
            typ = customer_type[lp]
            c_rep = cdf_values[typ][1]

            # if no switch in its zone → full repair cost
            for z in zones.values():
                ecost += load[lp] * c_rep * (1 - sum(m.X[s] for s in z) / len(z))

        # investment
        inv = sum(SWITCH_COST * m.X[s] for s in m.S)

        return ecost + inv

    model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # --------------------------
    # CONSTRAINT: realistic limit (important)
    # --------------------------
    model.limit = pyo.Constraint(expr=sum(model.X[s] for s in model.S) <= 30)

    # --------------------------
    # SOLVE
    # --------------------------
    solver = pyo.SolverFactory('highs')
    solver.solve(model)

    selected = [s for s in model.S if pyo.value(model.X[s]) > 0.5]

    return selected


# --------------------------
# RUN
# --------------------------
case1 = solve_case(True)
case2 = solve_case(False)

print("\n===== FINAL RESULTS =====")
print("Case 1 (with tie):", len(case1))
print("Case 2 (no tie):", len(case2))
