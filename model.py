import pyomo.environ as pyo
from data import *

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

    # --------------------------
    # PARAMETERS (KEY IDEA)
    # --------------------------
    # switching effectiveness differs between cases
    if with_tie:
        alpha = 1.0   # full benefit
    else:
        alpha = 0.3   # reduced benefit

    # --------------------------
    # OBJECTIVE (ECOST + INV)
    # --------------------------
    def obj_rule(m):
        ecost = 0

        for i in m.I:
            for j in m.J:
                typ = customer_type[j]
                c_sw, c_rep = cdf_values[typ]

                ecost += failure_rate[i] * m.Cd[i, j] * load[j]

        inv = sum(SWITCH_COST * m.X[s] for s in m.S)

        return ecost + inv

    model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # --------------------------
    # CONSTRAINTS (PAPER STYLE)
    # --------------------------
    model.cons = pyo.ConstraintList()

    for i in model.I:
        for j in model.J:

            typ = customer_type[j]
            c_sw, c_rep = cdf_values[typ]

            # effective switching influence (simplified Sij)
            influence = sum(model.X[s] for s in model.S) / 51

            # switching constraint
            model.cons.add(
                model.Cd[i, j] >= c_sw * alpha * influence
            )

            # repair constraint
            model.cons.add(
                model.Cd[i, j] >= c_rep * (1 - alpha * influence)
            )

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
