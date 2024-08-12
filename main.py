from sympy import symbols, Or, And, Not, Symbol
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import combinations
from itertools import count

FILENAME = "clues/trees-1.clues"
colored = False


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

    global colored
    if len(color) > 2:
        colored = True

    return shape, color, hints


class Hex:
    def __init__(self, x, y, z):
        assert x + y + z == 0, "Invalid cube coordinates!"
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Hex(x={self.x}, y={self.y}, z={self.z})"


def create_hex_board(edge_length):
    board = {}
    number = count(1)
    for x in range(-edge_length, edge_length + 1):
        for y in range(-edge_length, edge_length + 1):
            z = -x - y
            if -edge_length <= z <= edge_length and abs(x) + abs(y) + abs(z) <= 2 * edge_length - 1:
                board[(x, y, z)] = next(number)
    return board


def generate_combinations(n, blocks, block_colors):
    global colored
    # If blocks list is empty, return an array of all zeros of length n
    if not blocks:
        return [[0] * n]

    # Total length of all blocks combined
    total_block_length = sum(blocks)  # k
    num_blocks = len(blocks)  # L

    minimum_required_spaces = 0
    if colored:
        for i in range(1, num_blocks):
            if i > 0 and block_colors[i] == block_colors[i - 1]:
                minimum_required_spaces += 1
    elif not colored:
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
            # print(gaps_arr)
            yield gaps_arr

    # Generate all possible combinations
    results = []
    for gap_distribution in distribute_cells(remaining_cells, gap_positions):
        row = []
        previous_color = None

        for i, (gap, block, color) in enumerate(zip(gap_distribution, blocks + [0], block_colors + [''])):
            if i > 0 and previous_color == color:
                # Add mandatory gap if previous block color is the same as the current block's color
                row.extend([0])  # Mandatory gap between same-color blocks
            row.extend([0] * gap)  # Add gap cells
            row.extend([1] * block)  # Add block cells
            previous_color = color

        # print(blocks, row)
        results.append(row[:n])  # Trim the row to length n, if necessary
    # print(results)
    return results


counter = count(start=1)  # Helper variable counter
helper_vars = []


def get_helper_var():
    h = Symbol(f'H_{next(counter)}')
    helper_vars.append(h)
    return h


def tseytin_transformation(expr):
    """
    Convert a logical expression to CNF using Tseytin transformation.

    Parameters:
    - expr: The SymPy logical expression to convert.

    Returns:
    - List of CNF clauses.
    """
    clauses = []  # List to store the resulting CNF clauses

    def transform(expression):
        if isinstance(expression, Symbol):
            return expression  # Base case: variable

        if isinstance(expression, Or):
            # Create a new helper variable
            # h_var = get_helper_var()
            h_vars = []
            for sub_expr in expression.args:
                # Recursively process each sub-expression
                sub_expr_transformed = transform(sub_expr)
                h_vars.append(sub_expr_transformed)
                # clauses.append(Or(h_var, Not(sub_expr_transformed)))

            clauses.append(Or(*h_vars))  # h_var <=> (A1 OR A2 OR ...)
            # return h_var

        elif isinstance(expression, And):
            # print(expression)
            # Create a new helper variable
            h_var = get_helper_var()
            not_sub_exprs = []
            for sub_expr in expression.args:
                not_sub_exprs.append(Not(sub_expr))
                # Recursively process each sub-expression
                sub_expr_transformed = transform(sub_expr)
                clauses.append(Or(Not(h_var), sub_expr_transformed))
            clauses.append(Or(h_var, *not_sub_exprs))  # (A1 AND A2 AND ...) => h_var
            return h_var

        elif isinstance(expression, Not):
            # Handle negation by recursively transforming the inner expression
            sub_expr_transformed = transform(expression.args[0])
            return Not(sub_expr_transformed)

        else:
            raise ValueError(f"Unsupported expression type: {type(expression)}")

    # Transform the given expression
    transform(expr)
    return clauses


def dnf_to_cnf(dnf_formula):
    if isinstance(dnf_formula, Or):
        cnf_clauses = tseytin_transformation(dnf_formula)
    else:
        cnf_clauses = [dnf_formula]
    cnf_clause = And(*cnf_clauses)
    # print("DNF Formula:")
    # print(dnf_formula)
    # print("CNF Clauses:")
    # print(cnf_clause)

    return cnf_clause


def generate_hex_line_x(index, e):
    # Returns a list of (i, j) for a given x-line index
    return [(i, index - i) for i in range(e)]


def generate_hex_line_y(index, e):
    # Returns a list of (i, k) for a given y-line index
    return [(i, index - e + i) for i in range(e)]


def generate_hex_line_z(index, e):
    # Returns a list of (j, k) for a given z-line index
    return [(index - e + k, k) for k in range(e)]


def calculate_line_length(index, e):
    if index < e:
        return e + index  # Line length increases as index approaches the center
    else:
        return 3 * e - index - 2  # Line length decreases after the center


run_counter = 0


def generate_dnf(shape, hints):
    # Create variable names dynamically
    variables = []

    def create_dnf(index, hint_numbers, hint_colors, is_row, is_hex):
        global run_counter
        run_counter += 1
        print("run_counter", run_counter)
        if not is_hex:
            m = int(shape[1])  # Number of rows
            n = int(shape[2])  # Number of columns
            is_row = True if is_row == "row" else False

            if is_row:
                all_signs = generate_combinations(n, hint_numbers, hint_colors)
                var_symbols = [symbols(f'x{index}{j}') for j in range(n)]
            else:
                all_signs = generate_combinations(m, hint_numbers, hint_colors)
                var_symbols = [symbols(f'x{j}{index}') for j in range(m)]

            variables.append(var_symbols)
            clause_terms = []
            for signs in all_signs:
                terms = []
                for j, sign in enumerate(signs):
                    var = variables[index][j] if is_row else variables[j][index]
                    if sign == 1:
                        terms.append(var)
                    elif sign == 0:
                        terms.append(Not(var))
                clause_terms.append(And(*terms))
        else:
            coordinates = []
            var_symbols = []
            for (x, y, z) in var_map.values():
                if is_row == "x":
                    if x == index:
                        coordinates.append((x, y, z))
                        var_symbols.append(Symbol(f'x{x}_{y}_{z}'))
                elif is_row == "y":
                    if y == index:
                        coordinates.append((x, y, z))
                        var_symbols.append(Symbol(f'x{x}_{y}_{z}'))
                    q = []
                    q.extend(hint_numbers)
                    hint_numbers = q[::-1]

                elif is_row == "z":
                    if z == index:
                        coordinates.append((x, y, z))
                        var_symbols.append(Symbol(f'x{x}_{y}_{z}'))

            # print("coordinates", coordinates)
            # print("var_symbols", var_symbols)

            line_length = len(coordinates)

            all_signs = generate_combinations(line_length, hint_numbers, hint_colors)  # Updated to hex logic
            clause_terms = []

            for signs in all_signs:
                terms = []
                for j, sign in enumerate(signs):
                    var = var_symbols[j]
                    if sign == 1:
                        terms.append(var)
                    elif sign == 0:
                        terms.append(Not(var))
                clause_terms.append(And(*terms))
        # print(hint_numbers, clause_terms)
        return dnf_to_cnf(Or(*clause_terms))

    if shape[0] == "rect":
        m = int(shape[1])  # Number of rows
        n = int(shape[2])  # Number of columns

        # Parse the row and column hints
        row_hints = hints[:m]
        col_hints = hints[m:m + n]

        row_cnfs = [create_dnf(i, hint_numbers, hint_colors, "row", False) for i, (hint_numbers, hint_colors) in
                    enumerate(row_hints)]
        col_cnfs = [create_dnf(j, hint_numbers, hint_colors, "col", False) for j, (hint_numbers, hint_colors) in
                    enumerate(col_hints)]

        cnf_formulas = [*row_cnfs, *col_cnfs]

        # print(And(*cnf_formulas))
        return And(*cnf_formulas)

    elif shape[0] == "hex":
        e = int(shape[1])
        board = create_hex_board(e)
        var_map = {f'x{x}_{y}_{z}': (x, y, z) for x, y, z in board.keys()}

        hint_length = e + e - 1
        x_hints = hints[:hint_length]
        z_hints = hints[hint_length * 2:]
        y_hints = hints[hint_length:hint_length * 2]
        # z_hints = z_hints_temp[::-1]
        # print(x_hints)
        # print(y_hints)
        # print(z_hints)
        row_count = range(-e + 1, e)

        x_cnfs = [create_dnf(i, x_hints[i + e - 1][0], x_hints[i + e - 1][1], "x", True) for i in row_count]
        y_cnfs = [create_dnf(j, y_hints[j + e - 1][0], y_hints[j + e - 1][1], "y", True) for j in row_count]
        z_cnfs = [create_dnf(k, z_hints[k + e - 1][0], z_hints[k + e - 1][1], "z", True) for k in row_count]
        cnf_formulas = [*x_cnfs, *y_cnfs, *z_cnfs]
        # print(y_cnfs)
        # print(And(*cnf_formulas))
        return And(*cnf_formulas)

    else:
        raise ValueError("The first line must start with 'rect' or 'hex")


def sympy_to_cnf(shape, sympy_expr):
    # print("in")
    # print(sympy_expr)
    # Extract dimensions
    variable_map = {}
    rev_variable_map = {}
    index = 1

    if shape[0] == "rect":
        rows, cols = int(shape[1]), int(shape[2])

        # Create a mapping of variable names to numbers

        for i in range(rows):
            for j in range(cols):
                var_name = f'x{i}{j}'
                variable_map[var_name] = index
                rev_variable_map[index] = var_name
                index += 1

    elif shape[0] == "hex":
        edge = int(shape[1])
        variable_map = {}
        rev_variable_map = {}
        index = 1
        board = create_hex_board(edge)

        for x, y, z in board.keys():
            var_name = f'x{x}_{y}_{z}'
            variable_map[var_name] = index
            rev_variable_map[index] = var_name
            index += 1

        # print(variable_map)

    # Create a counter to assign numbers to helper variables
    helper_index = count(start=index)

    # print(variable_map)

    # Replace SymPy variable names with integer IDs
    def replace_vars(expr):
        if isinstance(expr, Symbol):
            # Check if it's a helper variable
            if str(expr) in variable_map:
                return Symbol(str(variable_map[str(expr)]))
            else:
                variable_map[str(expr)] = next(helper_index)
            return Symbol(str(variable_map.get(str(expr), helper_index)))
        elif isinstance(expr, And):
            return And(*[replace_vars(arg) for arg in expr.args])
        elif isinstance(expr, Or):
            return Or(*[replace_vars(arg) for arg in expr.args])
        elif isinstance(expr, Not):
            return Not(replace_vars(expr.args[0]))
        else:
            return expr

    # Convert the expression to CNF form
    cnf_expr = replace_vars(sympy_expr)

    # print(variable_map)

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
            return [[int(str(expr).replace('~', '-'))]]

    clauses = expr_to_clauses(cnf_expr)
    # print(clauses)
    # Flatten the list of clauses
    # flat_clauses = [clause for sublist in clauses for clause in (sublist if isinstance(sublist, list) else [sublist])]
    # print(flat_clauses)
    # flat_clauses = [str(num) for num in flat_clauses]
    # Return CNF object for PySAT
    return clauses


def sat_solver(shape, sympy_expr):
    # Convert SymPy expression to CNF format for PySAT
    cnf_clauses = sympy_to_cnf(shape, sympy_expr)
    e = int(shape[1])
    # print(cnf_clauses)
    # print(cnf_clauses)
    # Initialize CNF with the clauses
    cnf = CNF(from_clauses=cnf_clauses)

    # create a SAT solver for this formula:
    with Solver(name='minisat22') as solver:
        solver.append_formula(cnf)
        is_satisfiable = solver.solve()
        if is_satisfiable:
            model = solver.get_model()
            print("Satisfiable with model:", model[:(3 * e * e) - (3 * e) + 1])
            return model
        else:
            print("Unsatisfiable")


def write_model_to_file(model, shape, hints, filename):
    # Extract dimensions from the shape
    def get_blocks_and_colors(hints):
        block_lengths = []
        colors = []
        for lengths, cols in hints:
            block_lengths.extend(lengths)
            colors.extend(cols)
        return block_lengths, colors

    block_lengths, colors = get_blocks_and_colors(hints)

    if shape[0] == 'rect':
        rows = int(shape[1])
        cols = int(shape[2])

        # Create a grid to store the results
        grid = [['-' for _ in range(cols)] for _ in range(rows)]

        # Extract the number of grid variables (excluding helper variables)
        num_grid_vars = rows * cols

        # Initialize pointers for block lengths and colors
        block_index = 0
        color_index = 0

        # Assign values based on the model, considering only grid variables
        for value in model:
            if abs(value) <= num_grid_vars:  # Only consider grid variables
                index = abs(value) - 1  # Convert 1-based to 0-based index
                row = index // cols
                col = index % cols
                if value > 0 and block_index < len(block_lengths):
                    grid[row][col] = colors[color_index]
                    block_lengths[block_index] -= 1
                    if block_lengths[block_index] == 0:
                        block_index += 1
                        color_index += 1
                else:
                    grid[row][col] = '-'
    else:
        # Generate the hexagonal board (the dictionary containing (x, y, z) as keys)
        board = create_hex_board(int(shape[1]))

        # Extract hex coordinates from the board
        hex_coords = list(board.keys())

        # Determine unique z levels
        x_levels = sorted(set(x for _, _, x in hex_coords))

        # Create a dictionary to map z levels to their respective rows in the result grid
        row_mapping = {x: [] for x in x_levels}

        # Populate the row_mapping with coordinates for each z level
        for coord in hex_coords:
            x, y, z = coord
            row_mapping[x].append((x, y, z))

        # Initialize the result grid based on z levels
        result_grid = [['-' for _ in range(len(row_mapping[x]))] for x in x_levels]

        # Flattened grid for easier indexing
        flattened_grid = hex_coords

        num_grid_vars = len(flattened_grid)

        # Initialize pointers for block lengths and colors
        block_index = 0
        color_index = 0

        # Populate the result_grid based on the model
        for value in model:
            if abs(value) <= num_grid_vars:  # Only consider grid variables
                index = abs(value) - 1  # Convert to 0-based index
                x, y, z = flattened_grid[index]  # Retrieve coordinates from the flattened grid

                # Find the correct row and column in the result grid
                row_idx = x_levels.index(x)  # Row index based on z level
                col_idx = row_mapping[x].index((x, y, z))  # Column index within the row

                # Determine color based on block_lengths and colors
                if value > 0 and block_index < len(block_lengths):
                    result_grid[row_idx][col_idx] = colors[color_index]
                    block_lengths[block_index] -= 1
                    if block_lengths[block_index] == 0:
                        block_index += 1
                        color_index += 1
                else:
                    result_grid[row_idx][col_idx] = '-'

        # The result_grid now represents the hexagonal grid with correct dimensions and values

        grid = result_grid

    # Write the grid to a file
    with open(filename.replace("clues", "solutions").replace("generated", "generated_solutions"), "w") as file:
        for row in grid:
            file.write("".join(row) + "\n")


def main():
    shape, color, hints = get_content(FILENAME)
    cnf_formula = generate_dnf(shape, hints)
    # cnf_formula = dnf_to_cnf(dnf_formulas)
    model = sat_solver(shape, cnf_formula)
    if model:
        write_model_to_file(model, shape, hints, FILENAME)


if __name__ == '__main__':
    main()
