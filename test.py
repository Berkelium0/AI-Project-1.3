from itertools import combinations


def xor_to_cnf(xvars):
    # Given a list of variables for XOR constraint
    # xvars is a list of variable names, e.g., ['x1', 'x2', 'x3']

    num_vars = len(xvars)
    clauses = []

    # Iterate over all combinations of variables (2^num_vars - 1 combinations)
    for i in range(1, num_vars + 1):
        for comb in combinations(xvars, i):
            # Each combination of size i represents a clause
            clause = list(comb)
            # Add the clause to the list of clauses
            # We need to create a clause where at least one of these variables should be True
            clauses.append(clause)
            # Add the negation clause for XOR, i.e., (¬x1 ∨ ¬x2 ∨ ... ∨ ¬xn) when n is odd

    # Add the clauses to ensure that exactly one of these combinations is true
    for clause in clauses:
        neg_clause = [f"¬{var}" for var in clause]
        clauses.append(neg_clause)

    return clauses


# Example usage
xvars = ['x1', 'x2', 'x3']
cnf_clauses = xor_to_cnf(xvars)

for clause in cnf_clauses:
    print(" OR ".join(clause))

# Example usage
# if __name__ == "__main__":
# Define variables
# A, B, C, D, E, F, G, H, I, F, K, L, M, N, O, P, R, S, T, E, F, G, Q, X1, X2, X3, X4, X5, X6, X7, X8, X9, X0 = 0
# Convert XOR of multiple variables to CNF


# print(
#   xor_to_cnf(
#      (A, B, C, D, E, F, G, H, I, F, K, L, M, N, O, P, R, S, T, E, F, G, Q, X1, X2, X3, X4, X5, X6, X7, X8, X9,
#      X0)))
