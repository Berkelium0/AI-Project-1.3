from sympy import symbols, Or, And, Not, to_cnf, Symbol
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import combinations

FILENAME = "generated/stripes-010.clues"


def get_content(filename):
    with open(filename, 'r') as file:
        # Read the entire content of the file
        lines = file.readlines()

        # Get the shape
        first_line = lines[0].strip()
        shape = first_line.split()

        # Get the color
        color = lines[1].strip().split()

        # Get the hints
        hints = []
        for line in lines[2:]:
            hint = line.strip()
            hint_parts = hint.split()
            hint_numbers = [int(part[:-1]) for part in hint_parts]  # Remove 'a' from the end
            hint_colors = [part[-1] for part in hint_parts]  # Extract color ('a')
            hints.append((hint_numbers, hint_colors))

    print(shape)
    print(color)
    print(hints)

    return shape, color, hints


def generate_combinations(n, blocks):
    # If blocks list is empty, return an array of all zeros of length n
    if not blocks:
        return [[0] * n]

    # Total length of all blocks combined
    total_block_length = sum(blocks)  # k
    num_blocks = len(blocks)  # L
    minimum_required_spaces = num_blocks - 1  # S

    # Total occupied cells by blocks and the minimum required spaces
    total_occupied_cells = total_block_length + minimum_required_spaces  # T

    # Calculate the remaining cells (empty cells to be placed around blocks)
    remaining_cells = n - total_occupied_cells  # R

    # There are num_blocks + 1 gaps (before, between, and after blocks)
    gap_positions = num_blocks + 1  # g

    # Generate all possible ways to distribute remaining_cells into gap_positions gaps
    def distribute_cells(cells, gaps):
        """Generate all distributions of cells into gaps."""
        for positions in combinations(range(cells + gaps - 1), gaps - 1):
            # Create the gaps array
            gaps_arr = []
            last_index = -1
            for p in positions:
                gaps_arr.append(p - last_index - 1)
                last_index = p
            gaps_arr.append(cells + gaps - 2 - last_index)
            yield gaps_arr

    # Generate all possible combinations
    results = []
    for gap_distribution in distribute_cells(remaining_cells, gap_positions):
        row = []
        for gap, block in zip(gap_distribution, blocks + [0]):  # Add a dummy block at the end
            row.extend([0] * gap)  # Add gap cells
            row.extend([1] * block)  # Add block cells
            row.extend([0])
        results.append(row[:n])  # Trim the row to length n, if necessary
    print(results)
    return results


def generate_dnf(shape, hints):
    if shape[0] == "rect":
        m = int(shape[1])  # Number of rows
        n = int(shape[2])  # Number of columns

        # Create variable names dynamically
        vars = [[symbols(f'x{i}{j}') for j in range(n)] for i in range(m)]
        print(vars)

        # Parse the row and column hints
        row_hints = hints[:m]
        col_hints = hints[m:m + n]

        def create_dnf(index, hint_numbers, is_row):
            all_signs = generate_combinations(n, hint_numbers)

            clause_terms = []
            for signs in all_signs:
                terms = []
                for j, sign in enumerate(signs):
                    var = vars[index][j] if is_row else vars[j][index]
                    if sign == 1:
                        terms.append(var)
                    elif sign == 0:
                        terms.append(Not(var))
                clause_terms.append(And(*terms))

            print(clause_terms, len(clause_terms))
            return Or(*clause_terms)

        row_dnfs = [create_dnf(i, hint_numbers, True) for i, (hint_numbers, _) in enumerate(row_hints)]
        col_dnfs = [create_dnf(j, hint_numbers, False) for j, (hint_numbers, _) in enumerate(col_hints)]

        dnf_formulas = [*row_dnfs, *col_dnfs]

        print(dnf_formulas)
        return dnf_formulas

    elif shape[0] == "hex":
        pass
    else:
        raise ValueError("The first line must start with 'rect' or 'hex")


def dnf_to_cnf(dnf_formulas):
    # Convert DNF to CNF
    cnf_formulas = []
    for dnf_formula in dnf_formulas:
        print(dnf_formula)
        cnf_formulas.append(to_cnf(dnf_formula,simplify=True, force=True))

    cnf_formula = And(*cnf_formulas)
    print("DNF Formula:")
    print(dnf_formulas)
    print("\nCNF Formula:")
    print(cnf_formula)
    return cnf_formula


def sympy_to_cnf(shape, sympy_expr):
    # Extract dimensions
    rows, cols = int(shape[1]), int(shape[2])

    # Create a mapping of variable names to numbers
    variable_map = {}
    rev_variable_map = {}
    index = 1

    for i in range(rows):
        for j in range(cols):
            var_name = f'x{i}{j}'
            variable_map[var_name] = index
            rev_variable_map[index] = var_name
            index += 1

    # Replace SymPy variable names with integer IDs
    def replace_vars(expr):
        if isinstance(expr, Symbol):
            return Symbol(str(variable_map[str(expr)]))
        elif isinstance(expr, And):
            return And(*[replace_vars(arg) for arg in expr.args])
        elif isinstance(expr, Or):
            return Or(*[replace_vars(arg) for arg in expr.args])
        elif isinstance(expr, Not):
            return Not(replace_vars(expr.args[0]))
        else:
            return expr

    # Convert the expression to CNF form
    cnf_expr = to_cnf(replace_vars(sympy_expr))

    # Convert CNF expression to a list of clauses for PySAT
    def expr_to_clauses(expr):
        if isinstance(expr, And):
            clauses = []
            for arg in expr.args:
                clauses.extend(expr_to_clauses(arg))
            return clauses
        elif isinstance(expr, Or):
            # Handle literals
            return [[int(str(lit).replace('~', '-')) for lit in expr.args]]
        elif isinstance(expr, Not):
            return [[-int(str(expr.args[0]).replace('~', '-'))]]
        else:
            print(expr)
            return [[int(str(expr).replace('~', '-'))]]

    clauses = expr_to_clauses(cnf_expr)
    print(clauses)
    # Flatten the list of clauses
    # flat_clauses = [clause for sublist in clauses for clause in (sublist if isinstance(sublist, list) else [sublist])]
    # print(flat_clauses)
    # flat_clauses = [str(num) for num in flat_clauses]
    # Return CNF object for PySAT
    return clauses


def sat_solver(shape, sympy_expr):
    # Convert SymPy expression to CNF format for PySAT
    cnf_clauses = sympy_to_cnf(shape, sympy_expr)

    # Initialize CNF with the clauses
    cnf = CNF(from_clauses=cnf_clauses)

    # create a SAT solver for this formula:
    with Solver(bootstrap_with=cnf) as solver:
        # 1.1 call the solver for this formula:
        print('formula is', f'{"s" if solver.solve() else "uns"}atisfiable')

        # 1.2 the formula is satisfiable and so has a model:
        print('and the model is:', solver.get_model())

        # i.e. an unsatisfiable core can be extracted:
        print('and the unsatisfiable core is:', solver.get_core())

        return solver.get_model()


def write_model_to_file(model, shape, filename):
    # Extract dimensions from the shape
    if shape[0] == 'rect':
        rows = int(shape[1])
        cols = int(shape[2])

    # Create a grid to store the results
    grid = [['-' for _ in range(cols)] for _ in range(rows)]

    # Assign values based on the model
    for value in model:
        index = abs(value) - 1  # Convert 1-based to 0-based index
        row = index // cols
        col = index % cols
        if value > 0:
            grid[row][col] = 'a'
        else:
            grid[row][col] = '-'

    # Write the grid to a file
    with open(filename.replace("clues", "solutions").replace("generated", "generated_solutions"), "w") as file:
        for row in grid:
            file.write("".join(row) + "\n")


def main():
    shape, color, hints = get_content(FILENAME)
    dnf_formulas = generate_dnf(shape, hints)
    cnf_formula = dnf_to_cnf(dnf_formulas)
    model = sat_solver(shape, cnf_formula)
    write_model_to_file(model, shape, FILENAME)


if __name__ == '__main__':
    main()
