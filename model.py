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
# BFS PATH (returns switches)
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
        Sij[(i, j)] = get_path_switches(u, j)

# --------------------------
# CHECK UPSTREAM/DOWNSTREAM
# --------------------------
def is_upstream(fault_edge, load_node):
    source = "SP1"   # main source assumption
    path = get_path_switches(source, load_node)

    fault_u, fault_v = fault_edge

    for s in path:
        u, v = switch_locations[s]
        if u == fault_u or v == fault_u:
            return True
        if u == fault_v or v == fault_v:
            return False

    return True


# --------------------------
# SOLVER FUNCTION
# --------------------------
def solve_case(allow_tie=True):

    model = pyo.ConcreteModel()

    model.S = range(1, 52)
    model.I = range(1, 52)
    model.J = nodes

    # VARIABLES
    model.X = pyo.Var(model.S, domain=pyo.Binary)
    model.Cd = pyo.Var(model.I, model.J, domain=pyo.NonNegativeReals)

    # Disable tie switches for Case 2
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
    # CON
