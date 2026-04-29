import pyomo.environ as pyo
from collections import defaultdict, deque
from data import *

# --------------------------
# BUILD GRAPH
# --------------------------
graph = defaultdict(list)
for s, (u, v) in switch_locations.items():
    graph[u].append((v, s))
    graph[v].append((u, s))

# --------------------------
# PATH FUNCTION
# --------------------------
def get_path_switches(start, end):
    visited = set()
    queue = deque([(start, [])])

    while queue:
        node, path = queue.popleft()
        if node == end:
            return path

        if node in visited:
            continue
        visited.add(node)

        for neighbor, switch_id in graph[node]:
            queue.append((neighbor, path + [switch_id]))

    return []

# --------------------------
# BUILD Sij
# --------------------------
Sij = {}
for i in range(1, 52):
    u, v = switch_locations[i]

    for j in nodes:
        path = get_path_switches(u, j)
        Sij[(i, j)] = path

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
    model.delta = pyo.Var(model.I, model.J, domain=pyo.Binary)

    # Disable tie switches if Case 2
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
                repair_cost = cdf_values[typ][1]
                ecost += failure_rate[i] * m.Cd[i, j] * load[j] * repair_cost

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

            if len(switches) == 0:
                continue

            # δij only 1 if switch exists
            model.cons.add(
                model.delta[i, j] <= sum(model.X[s] for s in switches)
            )

            # switching case
            model.cons.add(
                model.Cd[i, j] >= c_sw * model.delta[i, j]
            )

            # repair case
            model.cons.add(
                model.Cd[i, j] >= c_rep * (1 - model.delta[i, j])
            )

    # CASE 2: no restoration allowed
    if not allow_tie:
        for i in model.I:
            for j in model.J:
                model.delta[i, j].fix(0)

    # --------------------------
    # SOLVE
    # --------------------------
    solver = pyo.SolverFactory('highs')   # IMPORTANT
    solver.solve(model)

    # --------------------------
    # RESULTS
    # --------------------------
    selected = [s for s in model.S if pyo.value(model.X[s]) > 0.5]
    total_cost = pyo.value(model.obj)

    return selected, total_cost


# --------------------------
# RUN BOTH CASES
# --------------------------
case1_switches, cost1 = solve_case(allow_tie=True)
case2_switches, cost2 = solve_case(allow_tie=False)

print("\n================ RESULTS ================\n")

print("Case 1 (WITH tie lines)")
print("Switch count:", len(case1_switches))
print("Switches:", case1_switches)
print("Total Cost:", cost1)

print("\nCase 2 (NO tie lines)")
print("Switch count:", len(case2_switches))
print("Switches:", case2_switches)
print("Total Cost:", cost2)
