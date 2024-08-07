from pysat.solvers import Solver
from pysat.formula import CNF

# Define the CNF formula
cnf = CNF()
cnf.extend([
    [1], [3], [4], [1, -6], [2, -7], [2, -9], [4, -10], [5, -6],
    [5, -7], [8, -10], [8, -9], [-1, -7], [-10, -2], [-2, -6],
    [-4, -9], [1, 7, -2], [10, 2, -4], [10, 9, -8], [2, 6, -1],
    [4, 9, -2], [6, 7, -5]
])

# Function to check satisfiability with a fixed value for x2
def check_x2_value(x2_value):
    with Solver(name='glucose4') as solver:
        # Add the CNF formula
        solver.append_formula(cnf)
        # Set x2 to the given value
        if x2_value:
            solver.add_clause([2])  # x2 = True
        else:
            solver.add_clause([-2]) # x2 = False
        # Check satisfiability
        is_satisfiable = solver.solve()
        return is_satisfiable, solver.get_model() if is_satisfiable else None

# Test x2 = True
satisfiable_true, model_true = check_x2_value(True)
print("x2 = True:", "Satisfiable with model:", model_true if satisfiable_true else "Unsatisfiable")

# Test x2 = False
satisfiable_false, model_false = check_x2_value(False)
print("x2 = False:", "Satisfiable with model:", model_false if satisfiable_false else "Unsatisfiable")
