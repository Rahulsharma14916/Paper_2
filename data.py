# data.py

nodes = [f"LP{i}" for i in range(1, 39)]
supply_nodes = ["SP1", "SP2", "SP3"]

# Average Load (kW) - RBTS Bus 4
load = {
    "LP1": 535, "LP2": 535, "LP3": 535, "LP4": 566, "LP5": 566, "LP6": 454, "LP7": 454,
    "LP8": 1000, "LP9": 1150, "LP10": 535, "LP11": 535, "LP12": 450, "LP13": 566,
    "LP14": 566, "LP15": 454, "LP16": 454, "LP17": 450, "LP18": 450, "LP19": 450,
    "LP20": 566, "LP21": 566, "LP22": 454
}
# Fill remaining load points with 500kW
for i in range(23, 39):
    load[f"LP{i}"] = 500

# Customer Classification mapping
customer_type = {}
for lp in ["LP1","LP2","LP3","LP10","LP11","LP12","LP17","LP18","LP19"]:
    customer_type[lp] = "residential"
for lp in ["LP8","LP9"]:
    customer_type[lp] = "small"
for lp in ["LP4","LP5","LP13","LP14","LP20","LP21"]:
    customer_type[lp] = "government"
for lp in ["LP6","LP7","LP15","LP16","LP22"]:
    customer_type[lp] = "commercial"
for i in range(23, 39):
    customer_type[f"LP{i}"] = "residential"

# Customer Damage Function ($/kW) - (Switching Cost, Repair Cost)
# Extracted from the RBTS Table I (Standard Values)
cdf_values = {
    "residential": (0.06, 3.16),
    "small":       (2.88, 13.87),
    "commercial":  (21.51, 63.06),
    "government":  (0.25, 2.05)
}

# Failure rate per section (f/yr)
failure_rate = {i: 0.065 for i in range(1, 52)}

# Constants for Optimization
REPAIR_TIME = 5.0
SWITCH_TIME = 0.167 # ~10 minutes
SWITCH_COST = 4700

# Logical Topology Mapping (From/To)
switch_locations = {
    1:("SP1","LP1"), 2:("LP1","LP2"), 3:("LP2","LP3"), 4:("LP3","LP4"),
    5:("LP4","LP5"), 6:("LP5","LP6"), 7:("LP6","LP7"),
    8:("SP1","LP8"), 9:("LP8","LP9"), 10:("LP9","LP10"),
    11:("SP1","LP11"), 12:("LP11","LP12"), 13:("LP12","LP13"),
    14:("LP13","LP14"), 15:("LP14","LP15"),
    16:("SP1","LP16"), 17:("LP16","LP17"), 18:("LP17","LP18"),
    19:("LP18","LP19"), 20:("LP19","LP20"), 21:("LP20","LP21"),
    22:("LP21","LP22"),
    23:("SP2","LP23"), 24:("LP23","LP24"), 25:("LP24","LP25"),
    26:("SP3","LP26"), 27:("LP26","LP27"), 28:("LP27","LP28"),
    29:("SP3","LP29"), 30:("LP29","LP30"), 31:("LP30","LP31"),
    32:("LP31","LP32"), 33:("LP32","LP33"), 34:("LP33","LP34"),
    35:("LP34","LP35"), 36:("LP35","LP36"), 37:("LP36","LP37"),
    38:("LP37","LP38"),
    # Tie-switches (Loop points)
    39:("LP7","LP23"), 40:("LP10","LP26"), 41:("LP15","LP29"),
    42:("LP22","LP32"), 43:("LP5","LP20"), 44:("LP8","LP24"),
    45:("LP12","LP27"), 46:("LP17","LP33"), 47:("LP21","LP35"),
    48:("LP3","LP14"), 49:("LP6","LP18"), 50:("LP9","LP25"),
    51:("LP11","LP28"),
}
