import pyomo.environ as pyo
from data import *

# --------------------------
# LOCALIZED INFLUENCE SET (KEY FIX)
# --------------------------
Sij = {}

for i in range(1, 52):
    for j_idx, j in enumerate(nodes):

        # only a SMALL local set of switches affects (i,j)
        start = max(1, i - 1)
        end = min(51, i + 1)

        # vary influence by load index (important!)
        if j_idx % 2 == 0:
            Sij[(i, j)] = list(range(start, end + 1))
        else:
            Sij[(i, j)] = list(range(start, min(end, i + 1) + 1))


# --------------------------
# MODEL FUNCTION
# --------------------------
def solve_case(with_tie=True):

    model = pyo.ConcreteModel()

    model.S = range(1, 52)
    model.I = range(1, 52)
    model.J = nodes

    # VARIABLES
    model.X = pyo.Var(model.S, domain=pyo.Binary)
    model.Cd = pyo.Var(model.I, model.J, domain=pyo.NonNegativeReals)

    # switching effectiveness
    alpha = 1.0 if with_tie else 0.4

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
    # CONSTRAINTS
    # --------------------------
    model.cons = pyo.ConstraintList()

    for i in model.I:
        for j in model.J:

            typ = customer_type[j]
            c_sw, c_rep = cdf_values[typ]

            switches = Sij[(i, j)]

            influence = sum(model.X[s] for s in switches)

            # switching case
            model.cons.add(
                model.Cd[i, j] >= c_sw * alpha * influence
            )

            # repair case
            model.cons.add(
                model.Cd[i, j] >= c_rep * (1 - alpha * influence / max(1, len(switches)))
            )

    # --------------------------
    # LIMIT (prevents all switches)
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

print("\nFINAL RESULTS")
print("Case 1 (with tie):", len(case1))
print("Case 2 (no tie):", len(case2))
