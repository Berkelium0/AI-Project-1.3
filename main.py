from sympy import Or, And, Not, Symbol
from pysat.formula import CNF
from pysat.solvers import Solver
from itertools import count

FILENAME = "clues/stripes-1.clues"
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


def exactly_one_true(clauses):
    # Step 1: At least one clause is true (OR all clauses together)
    at_least_one_true = Or(*clauses)

    # Step 2: No two clauses are true simultaneously (AND of pairwise ORs of their negations)
    no_two_true_simultaneously = And(
        *[Or(~clauses[i], ~clauses[j]) for i in range(len(clauses)) for j in range(i + 1, len(clauses))]
    )

    # Final CNF: Combine the two conditions
    cnf_formula = And(at_least_one_true, no_two_true_simultaneously)
    # print(cnf_formula)
    return cnf_formula


variables = []
cells_in_row = {}
cells_in_col = {}
cells_in_x = {}
cells_in_y = {}
cells_in_z = {}


def create_start_args(index, length, axis, hint_numbers, hint_colors, coordinates=None):
    global variables, cells_in_row, cells_in_col
    # print("hint_numbers", hint_numbers, "length", length)
    total_block_length = sum(hint_numbers)
    num_blocks = len(hint_colors)

    minimum_required_spaces = 0
    if colored:
        for i in range(1, num_blocks):
            if i > 0 and hint_colors[i] == hint_colors[i - 1]:
                minimum_required_spaces += 1
    elif not colored:
        minimum_required_spaces = num_blocks - 1  # S

    total_occupied_cells = total_block_length + minimum_required_spaces

    args_that_imply = []
    args_that_fill_cells = []
    def_filled = {}
    def_true = None

    args_that_imply_only_one_start = []
    earliest_start = 0
    latest_start = length - total_occupied_cells + 1
    # print("latest_start", latest_start, "length", length, "total_occupied_cells", total_occupied_cells)

    if len(hint_numbers) == 0:
        empty_cell = []
        if axis == "r":
            for i in range(length):
                empty_cell.append(Not(Symbol(f"x{index}_{i}")))
        elif axis == "c":
            for i in range(length):
                empty_cell.append(Not(Symbol(f"x{i}_{index}")))
        else:
            for x, y, z in coordinates:
                empty_cell.append(Not(Symbol(f"x{x}_{y}_{z}")))

        return And(*empty_cell)

    # indexes to imply cells cant be filled without a start
    if axis == "r":
        cells_in_row.update({f"x{index}_{i}": [] for i in range(length)})
    elif axis == "c":
        cells_in_col.update({f"x{i}_{index}": [] for i in range(length)})
    elif axis == "x":
        for x, y, z in coordinates:
            cells_in_x.update({f"x{x}_{y}_{z}": []})
    elif axis == "y":
        for x, y, z in coordinates:
            cells_in_y.update({f"x{x}_{y}_{z}": []})
    elif axis == "z":
        for x, y, z in coordinates:
            cells_in_z.update({f"x{x}_{y}_{z}": []})

    # print("cells_in_x", cells_in_x)
    # print("cells_in_y", cells_in_y)
    # print("cells_in_z", cells_in_z)

    for block_index, block in enumerate(hint_numbers):
        #  print("block_index", block_index, "block", block)
        if axis == "r":
            for i in range(length):
                def_filled[f"x{index}_{i}"] = []
        elif axis == "c":
            for i in range(length):
                def_filled[f"x{i}_{index}"] = []
        else:
            for x, y, z in coordinates:
                def_filled[f"x{x}_{y}_{z}"] = []

        starts = []
        # Add the block starts
        # print("earliest_start", earliest_start, "latest_start", latest_start, "length", length)
        for j in range(earliest_start, latest_start):
            current_block_start = Symbol(f'{axis}axis_{index}_{j}_{block_index}')
            variables.append(current_block_start)
            starts.append(current_block_start)

            # This start Implies the next start cant be here or after here

            if block_index < len(hint_numbers) - 1:
                next_block_starts = []
                length_depending_on_color = j + block + 1
                if colored:
                    if hint_colors[block_index] != hint_colors[block_index + 1]:
                        length_depending_on_color = j + block

                for i in range(length_depending_on_color):
                    if i <= latest_start:
                        variables.append(Symbol(f'{axis}axis_{index}_{i}_{block_index + 1}'))
                        next_block_starts.append(
                            Or(Not(current_block_start), Not(Symbol(f'{axis}axis_{index}_{i}_{block_index + 1}'))))
                args_that_imply.append(And(*next_block_starts))
            # print("args_that_imply", args_that_imply)

            # This start Implies the cells in it has to be filled
            filled_cells = []
            cell = ""
            for i in range(block):
                if axis == "r":
                    # print(index, j, i, current_block_start, length, earliest_start, latest_start)
                    cell = f'x{index}_{j + i}'
                    cells_in_row[cell].append(current_block_start)
                elif axis == "c":
                    cell = f'x{j + i}_{index}'
                    cells_in_col[cell].append(current_block_start)
                elif axis == "x":
                    cell = f'x{coordinates[j + i][0]}_{coordinates[j + i][1]}_{coordinates[j + i][2]}'
                    cells_in_x[cell].append(current_block_start)
                elif axis == "y":
                    cell = f'x{coordinates[j + i][0]}_{coordinates[j + i][1]}_{coordinates[j + i][2]}'
                    cells_in_y[cell].append(current_block_start)
                elif axis == "z":
                    cell = f'x{coordinates[j + i][0]}_{coordinates[j + i][1]}_{coordinates[j + i][2]}'
                    cells_in_z[cell].append(current_block_start)

                def_filled[cell].append(current_block_start)
                # print("here", current_block_start,cell)
                filled_cells.append(Or(Not(current_block_start), Symbol(cell)))
            # print("filled_cells", filled_cells)

            if len(filled_cells) > 1:
                args_that_fill_cells.append(And(*filled_cells))
            else:
                args_that_fill_cells.append(And(filled_cells[0]))
            # print("args_that_fill_cells", args_that_fill_cells)

        # print("def_filled", def_filled)
        # print("starts", starts)
        def_true = []
        for key, value in def_filled.items():
            if len(value) == len(starts):
                def_true.append(Symbol(key))
        # print("def_true", def_true)

        # Make sure there is only one start type

        args_that_imply_only_one_start.append(exactly_one_true(starts))
        # print("args_that_imply_only_one_start", args_that_imply_only_one_start)

        # Adjusting the latest start based on the next block's color
        if block_index < len(hint_numbers) - 1:  # Ensure we are not at the last block
            if hint_colors[block_index] == hint_colors[block_index + 1]:
                earliest_start += block + 1  # Add 1 space if the previous block has the same color
                latest_start += block + 1
            else:
                earliest_start += block
                latest_start += block
        else:
            earliest_start += block + 1
            latest_start += block + 1  # No next block, just add the current block size

    # for keys, values in cells_in_axis.items():
    #     args_say_cells_have_starts.append(Or(Not(keys), Or(*values)))

    # print(args_that_imply_only_one_start, "\n", args_that_fill_cells, "\n", args_that_imply)
    #  print(And(*args_that_imply_only_one_start, *args_that_fill_cells, *args_that_imply, *def_true))
    return And(*args_that_imply_only_one_start, *args_that_fill_cells, *args_that_imply, *def_true)


run_counter = 0


def generate_cnf(shape, hints):
    global variables, cells_in_row, cells_in_col

    def generator(index, hint_numbers, hint_colors, axis, is_rect):
        global run_counter
        run_counter += 1
        print("run_counter", run_counter)
        if is_rect:
            if axis == "r":
                rect_args = create_start_args(index, n, axis, hint_numbers, hint_colors)
            else:
                rect_args = create_start_args(index, m, axis, hint_numbers, hint_colors)

            return rect_args

        elif not is_rect:
            coordinates = []
            line_length = 0
            for x, y, z in board.keys():
                if axis == "x":
                    if x == index:
                        line_length += 1
                        coordinates.append((x, y, z))
                elif axis == "y":
                    if y == index:
                        line_length += 1
                        coordinates.append((x, y, z))
                    q = []
                    q.extend(hint_numbers)
                    hint_numbers = q[::-1]
                    r = []
                    r.extend(hint_colors)
                    hint_colors = r[::-1]

                elif axis == "z":
                    if z == index:
                        line_length += 1
                        coordinates.append((x, y, z))

            # print(axis, coordinates)
            hex_args = create_start_args(index, line_length, axis, hint_numbers, hint_colors, coordinates)

            return hex_args

    args = []
    cell_args = []

    if shape[0] == "rect":
        m = int(shape[1])  # Number of rows
        n = int(shape[2])  # Number of columns

        # coordinates
        for i in range(m):
            for j in range(n):
                variables.append(Symbol(f'x{i}_{j}'))

        # Parse the row and column hints
        row_hints = hints[:m]
        col_hints = hints[m:m + n]
        row_args = [generator(i, hint_numbers, hint_colors, "r", True) for i, (hint_numbers, hint_colors) in
                    enumerate(row_hints)]
        col_args = [generator(j, hint_numbers, hint_colors, "c", True) for j, (hint_numbers, hint_colors) in
                    enumerate(col_hints)]

        # print("variables", variables)
        # print(len(variables))

        # print(row_args, "\n", col_args)
        args = [*row_args, *col_args]

        for keys, values in cells_in_row.items():
            if values:
                cell_args.append(Or(Not(keys), Or(*values)))

        for keys, values in cells_in_col.items():
            if values:
                cell_args.append(Or(Not(keys), Or(*values)))

    elif shape[0] == "hex":
        edge = int(shape[1])  # Number of rows

        # coordinates
        board = create_hex_board(edge)
        for x, y, z in board.keys():
            variables.append(Symbol(f'x{x}_{y}_{z}'))
        # print("variables", variables)

        hint_length = edge + edge - 1
        x_hints = hints[:hint_length]
        z_hints = hints[hint_length * 2:]
        y_hints = hints[hint_length:hint_length * 2]
        row_count = range(-edge + 1, edge)

        x_args = [generator(i, x_hints[i + edge - 1][0], x_hints[i + edge - 1][1], "x", False) for i in row_count]
        y_args = [generator(i, y_hints[i + edge - 1][0], y_hints[i + edge - 1][1], "y", False) for i in row_count]
        z_args = [generator(i, z_hints[i + edge - 1][0], z_hints[i + edge - 1][1], "z", False) for i in row_count]

        # # print(len(variables))
        #
        # # print(row_args, "\n", col_args)
        args = [*x_args, *y_args, *z_args]

    for keys, values in cells_in_x.items():
        if values:
            cell_args.append(Or(Not(Symbol(keys)), Or(*values)))

    for keys, values in cells_in_y.items():
        if values:
            cell_args.append(Or(Not(Symbol(keys)), Or(*values)))

    for keys, values in cells_in_z.items():
        if values:
            cell_args.append(Or(Not(Symbol(keys)), Or(*values)))

    # print("cell_args", cell_args)
    args.append(And(*cell_args))
    # print("keys", args)

    # print(And(*args))
    # dnf_to_cnf(args)

    return And(*args)


def sympy_to_cnf(sympy_expr):
    # print("in")
    # print(sympy_expr)
    # Extract dimensions
    global variables
    variable_map = {}

    for i, item in enumerate(variables):
        variable_map[str(item)] = i + 1

        # print(variable_map)

    #        print("variable_map", variable_map["c001"])

    # print(variable_map)

    # print(variable_map)

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


def sat_solver(sympy_expr):
    # Convert SymPy expression to CNF format for PySAT
    cnf_clauses = sympy_to_cnf(sympy_expr)
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
            # print("Satisfiable with model:", model)
            print("Satisfiable")
            return model
        else:
            print("Unsatisfiable")
            print(solver.accum_stats())

            # print("Proof", solver.get_proof())
            print('and the unsatisfiable core is:', solver.get_core())


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
    cnf_formula = generate_cnf(shape, hints)
    # print("cnf_formula", is_cnf(cnf_formula), cnf_formula)
    model = sat_solver(cnf_formula)
    if model:
        write_model_to_file(model, shape, hints, FILENAME)


if __name__ == '__main__':
    main()
