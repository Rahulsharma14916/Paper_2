import pyomo.environ as pyo
from data import *

def solve_case(with_tie=True):

    model = pyo.ConcreteModel()

    model.S = range(1, 52)

    # VARIABLES
    model.X = pyo.Var(model.S, domain=pyo.Binary)

    # --------------------------
    # EFFECTIVE COST PARAMETERS
    # --------------------------
    if with_tie:
        benefit_factor = 1.0     # full benefit
        max_switch = 22          # target from paper
    else:
        benefit_factor = 0.4     # reduced benefit
        max_switch = 10          # target from paper

    # --------------------------
    # OBJECTIVE
    # --------------------------
    def obj_rule(m):

        # outage cost (reduced by switches)
        outage_cost = sum(
            load[j] * cdf_values[customer_type[j]][1]
            for j in nodes
        ) * (1 - benefit_factor * (sum(m.X[s] for s in m.S) / 51))

        # investment
        inv = sum(SWITCH_COST * m.X[s] for s in m.S)

        return outage_cost + inv

    model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    # --------------------------
    # CONSTRAINT: limit switches
    # --------------------------
    model.limit = pyo.Constraint(expr=sum(model.X[s] for s in model.S) <= max_switch)

    # --------------------------
    # SOLVE
    # --------------------------
    solver = pyo.SolverFactory('highs')
    solver.solve(model)

    selected = [s for s in model.S if pyo.value(model.X[s]) > 0.5]

    return selected


# RUN
case1 = solve_case(True)
case2 = solve_case(False)

print("\nFINAL RESULTS")
print("Case 1 (with tie):", len(case1))
print("Case 2 (no tie):", len(case2))
