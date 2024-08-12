# Repository for ss24.1.3/team706

**Topic:** SS24 Assignment 1.3: Solve Nonograms

## Hexagonal and Rectangular Grid Puzzle Solver

### Introduction

This Python project implements a solver for puzzles on hexagonal and rectangular grids using logical deduction and SAT (
Boolean satisfiability) solving techniques. The solver can handle puzzles where certain conditions must be met along
rows, columns, or hexagonal lines based on provided hints. The puzzles can be either monochrome or colored.

# Dependencies

# Usage

Running the Solver

# Solving a Nonogram

## Structure and Time Complexities

In this section, we'll describe the structure and purpose of each function in the Nonogram solver, along with their
respective time complexities.

### get_content(filename)

This function reads and parses the Nonogram puzzle configuration from a file. The file is expected to contain the
puzzle's dimensions and the hints for each row and column.

The function opens the file, reads its contents line by line, and constructs the hints in a format suitable for
further processing.

**Time Complexity:**

- File Reading: O(N), where 𝑁 N is the number of lines in the file.
- Hint Parsing:O(M), where 𝑀 M is the number of hints.
- Overall:O(N+M).

### create_hex_board(edge_length)

This function generates the coordinates of a hexagonal grid based on a specified edge length. The hexagonal grid is
used as the board on which the Nonogram puzzle is solved.

The function iterates through all possible x and y coordinates within the range defined by the edge length and computes
the corresponding z coordinate.

**Time Complexity:**

- The number of possible coordinates to check is proportional to O(edge_length^3^).
- Overall: O(edge_length^3^).

### generate_combinations(n, blocks, block_colors)

This function generates all valid combinations for a row (or line) in the Nonogram, adhering to the constraints given
by the blocks and their respective block_colors.

It iterates over all possible positions where blocks can be placed in the row, taking into account the spaces between
them.

**Time Complexity:**

- The function explores all possible placements of blocks within a row, leading to a complexity of O(2^n^), where n is the
  length of the row.
- Overall: O(2^n^).

### tseytin_transformation(expr)

This function converts a given logical expression into Conjunctive Normal Form (CNF) using Tseytin transformation.
The Tseytin transformation introduces auxiliary variables to represent sub-expressions, ensuring the output CNF
remains linear in size relative to the input expression.

**Time Complexity:**

- The complexity depends on the depth and structure of the logical expression. Typically, it's proportional to the
  number of sub-expressions, resulting in O(k), where k is the number of sub-expressions.
- Overall: O(k).

### generate_dnf(shape, hints)

This function generates a Disjunctive Normal Form (DNF) logical expression that represents the constraints of the
Nonogram puzzle based on the provided hints.

It calls generate_combinations() to find all valid row configurations and then constructs the DNF expression
accordingly.

**Time Complexity:**

- The complexity is driven by the row generation process. For each row, generating combinations has a worst-case
  complexity of O(2^n^), and this process is repeated for each row and column.
- Overall: O(m⋅2^n^), where m is the number of rows or columns and n is the number of cells in each row or column.

### sympy_to_cnf(shape, sympy_expr)

This function converts a logical expression from SymPy format into Conjunctive Normal Form (CNF). It also maps the
logical variables to integer IDs for compatibility with the SAT solver.

The CNF conversion is necessary because SAT solvers typically operate on CNF formulas.

**Time Complexity:**

- The process involves iterating over each logical expression, resulting in a complexity of O(k), where k is the size of
  the expression.
- Overall: O(k).

### sat_solver(shape, sympy_expr)

This function uses a SAT solver to determine whether the CNF formula generated from the Nonogram constraints is
satisfiable. If satisfiable, it finds a solution (model) that satisfies all the constraints.
The solver checks if there is an assignment of values (True/False) to the variables that makes the entire CNF formula
true.

**Time Complexity:**

- SAT solving is an NP-complete problem, and its complexity can be exponential in the size of the input formula. The
  time complexity is O(T), where T is the time taken by the SAT solver.
- Overall: O(T), with T potentially being exponential.

### write_model_to_file(model, shape, hints, filename)

This function writes the solution model obtained from the SAT solver to a file. The output format represents the
solved Nonogram grid.

The function iterates over the model (the solution) and translates it into a human-readable format, which is then
written to a file.

**Time Complexity:**

- Writing the model to a file involves iterating over the grid cells, resulting in a complexity of O(V), where V is the
  number of variables (or grid cells).
- Overall:O(V).

#### main()

The main() function is the entry point of the program. It orchestrates the entire process of solving the Nonogram
puzzle, from reading the input to writing the solution.

The function calls all the above functions in sequence: it reads the puzzle configuration, generates the necessary
logical expressions, converts them to CNF, uses a SAT solver to find a solution, and finally writes the solution to a
file.

**Time Complexity:**

- The overall time complexity is dominated by the most expensive operations: generating combinations (generate_dnf())
  and solving the SAT problem (sat_solver()).

- Overall: O(m⋅2^n^+T), where T is the time taken by the SAT solver.

# Additional Information

