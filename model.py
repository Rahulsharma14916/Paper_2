import pyomo.environ as pyo
from data import *

# --------------------------
# TREND-BASED Sij (SMART APPROX)
# --------------------------

Sij = {}

for i in range(1, 52):
    for j_idx, j in enumerate(nodes):

        # create locality effect (nearby switches matter)
        base = max(1, i - 2)
        end = min(51, i + 2)

        switches = list(range(base, end + 1))

        # reduce influence for far loads (important!)
        if j_idx % 3 == 0:
            switches = switches[:len(switches)//2]

        Sij[(i, j)] = switches


# --------------------------
# MODEL
# --------------------------
def solve_case(with_tie=True):

    model = pyo.ConcreteModel()

    model.S = range(1, 52)
    model.I = range(1, 52)
    model.J = nodes

    model.X = pyo.Var(model.S, domain=pyo.Binary)
    model.Cd = pyo.Var(model.I, model.J, domain=pyo.NonNegativeReals)
    model.delta = pyo.Var(model.I, model.J, domain=pyo.Binary)

    # disable tie switches in Case 2
    if not with_tie:
        for s in range(39, 52):
            model.X[s].fix(0)

    # --------------------------
    # OBJECTIVE
    # --------------------------
    def obj_rule(m):
        ecost = sum(
            failure_rate[i] * m.Cd[i, j] * load[j]
            for i in m.I for j in m.J
        )
        inv = sum(SWITCH_COST * m.X[s] for s in m.S)
        return ecost + inv

    model.obj = pyo.Objective(rule=obj_rule)

    # --------------------------
    # CONSTRAINTS
    # --------------------------
    model.cons = pyo.ConstraintList()

    for i in model.I:
        for j in model.J:

            typ = customer_type[j]
            c_sw, c_rep = cdf_values[typ]

            switches = Sij[(i, j)]

            # switching possible only if switch exists
            model.cons.add(
                model.delta[i, j] <= sum(model.X[s] for s in switches)
            )

            # Case 2: reduce switching effectiveness
            if not with_tie:
                model.cons.add(model.delta[i, j] <= 0.3)

            # switching cost
            model.cons.add(
                model.Cd[i, j] >= c_sw * model.delta[i, j]
            )

            # repair cost
            model.cons.add(
                model.Cd[i, j] >= c_rep * (1 - sum(model.X[s] for s in switches)/len(switches))
            )

    # --------------------------
    # LIMIT (prevents 30 switches issue)
    # --------------------------
    model.limit = pyo.Constraint(expr=sum(model.X[s] for s in model.S) <= 25)

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
c1 = solve_case(True)
c2 = solve_case(False)

print("\nFINAL RESULTS")
print("Case 1:", len(c1))
print("Case 2:", len(c2))
