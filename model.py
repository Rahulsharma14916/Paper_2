import pyomo.environ as pyo
from data import *

# --------------------------
# BUILD SIMPLIFIED Sij
# (CRITICAL: use logical mapping, not BFS)
# --------------------------

Sij = {}

for i in range(1, 52):
    for j in nodes:
        # simple approximation: nearby switches affect node
        Sij[(i, j)] = [s for s in range(1, 52) if abs(s - i) <= 2]


# --------------------------
# MODEL FUNCTION
# --------------------------
def solve_case(allow_tie=True):

    model = pyo.ConcreteModel()

    model.S = range(1, 52)
    model.I = range(1, 52)
    model.J = nodes

    # VARIABLES
    model.X = pyo.Var(model.S, domain=pyo.Binary)
    model.Cd = pyo.Var(model.I, model.J, domain=pyo.NonNegativeReals)

    # Disable tie switches
    if not allow_tie:
        for s in range(39, 52):
            model.X[s].fix(0)

    # --------------------------
    # OBJECTIVE
    # --------------------------
    def obj_rule(m):
        ecost = 0
        for i in m.I:
            for j in m.J:
                typ = customer_type[j]
                ecost += failure_rate[i] * m.Cd[i, j] * load[j]

        inv = sum(SWITCH_COST * m.X[s] for s in m.S)

        return ecost + inv

    model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # --------------------------
    # CONSTRAINTS (ACTUAL PAPER LOGIC)
    # --------------------------
    model.cons = pyo.ConstraintList()

    for i in model.I:
        for j in model.J:

            typ = customer_type[j]
            c_sw, c_rep = cdf_values[typ]

            switches = Sij[(i, j)]

            # SWITCHING TIME constraint
            model.cons.add(
                model.Cd[i, j] >= c_sw
            )

            # REPAIR constraint (if no switch exists)
            model.cons.add(
                model.Cd[i, j] >= c_rep * (1 - sum(model.X[s] for s in switches))
            )

    # --------------------------
    # SOLVE
    # --------------------------
    solver = pyo.SolverFactory('highs')
    solver.solve(model)

    selected = [s for s in model.S if pyo.value(model.X[s]) > 0.5]
    total_cost = pyo.value(model.obj)

    return selected, total_cost


# --------------------------
# RUN
# --------------------------
case1, cost1 = solve_case(True)
case2, cost2 = solve_case(False)

print("\n===== RESULTS =====")
print("Case 1:", len(case1), "switches", cost1)
print("Case 2:", len(case2), "switches", cost2)
