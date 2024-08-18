# Repository for ss24.1.3/team706

**Topic:** SS24 Assignment 1.3: Solve Nonograms

## Hexagonal and Rectangular Grid Puzzle Solver

This Python project implements a solver for puzzles on hexagonal and rectangular grids using logical deduction and SAT (
Boolean satisfiability) solving techniques. The solver can handle puzzles where certain conditions must be met along
rows, columns, or hexagonal lines based on provided hints. The puzzles can be either monochrome or colored.

## Dependencies

To run this Nonogram solver, you need to set up the environment with the necessary dependencies. The project is built
using Python and relies on several external libraries. Below are the details of the required dependencies and how to
install them:

### Programming Language

- **Python**: The project is compatible with Python 3.8 or later.

### External Libraries

The project uses the following Python libraries:

+ **itertools Library**

    - **Description**: The itertools library is a standard Python module that provides a collection of fast,
      memory-efficient tools for creating iterators for various looping and combinatorial tasks.
    - **Usage in the Project**:

        - **`count`**: The `count` function from `itertools` creates an iterator that generates consecutive integers,
          starting from a specified number. In this project, `count` is used to generate sequences of indices or other
          counting purposes, which are helpful in iterating over puzzle rows, columns, or coordinates.

        - **`combinations` (imported as `itertools_combinations`)**: The `combinations` function generates all possible
          combinations of a specified length from the input iterable. In this project, `itertools_combinations` is used
          to generate possible placements of blocks within the puzzle rows or columns, which is essential for
          determining valid configurations based on the given hints.

    - **Installation**: No installation is required, as `itertools` is a built-in Python module.

+ **SymPy**

    - **Description**: SymPy is a Python library for symbolic mathematics. It provides tools for algebraic manipulation,
      equation solving, and logical expression handling.
    - **Usage in the Project**: SymPy is used to construct and manipulate logical expressions required for the Nonogram
      solver. Specifically, it helps in converting these expressions into Conjunctive Normal Form (CNF) for use with SAT
      solvers.
    - **Installation**: Run `pip install sympy`

+ **PySAT (Python SAT Solver)**

    - **Description**: PySAT is a library for SAT solving that interfaces with various SAT solvers. SAT solvers are used
      to determine the satisfiability of Boolean expressions, which is essential for solving constraints in puzzles.
    - **Usage in the Project**: PySAT is used to solve the CNF formula generated from the Nonogram constraints. It helps
      determine if there is a valid assignment of values that satisfies all the puzzle’s conditions.
    - **Installation**: Run `pip install python-sat`

### Installing Dependencies

To install all the required libraries, you can use the following `pip` command:

```bash
pip install sympy python-sat
```

## Usage

1. **Set the Puzzle File**: Update the `FILENAME` variable with the path to your desired `.clues` file.

2. **Run the Script**: Execute the script to solve the Nonogram. The solution will be output based on the script's
   settings.

## Different Approaches

For this project, I used two different approaches. My initial approach was to create every possible combination of
blocks, according to the clues and send that to the SAT solver. For small boards this approach worked very well, but
after the size of the board grew larger than 10x10, the time it required became more and more unbearable. My other
approach was to create rules depending on the starting points of the blocks and implement their effects on eachother as
rules, instead of brute-forcing by calculating every possible combination. In the end, this approach was exponantially
faster and clues that took over an hour to solve with the combination approach was being solved in mere minutes. Here is
what I did and learned while implementing both of the approaches:

### Combinations Approach

In both approaches I start by getting the board info from the `.clues` file. Then, I send the shape, color and hints
information to the `generate_dnf`function. There, the board is created depending on the shape info and each cell are
added to the `variables`list. After that, the hints are seperated depending on its axis ("row","col,"x","y","z") and
then sent o the `generate_combinations`function, which creates every possible combination that row can have. It does
this by calculating some variables first.

+ `total_block_length`= sum of all the block clues.
+ `num_blocks`= length of the block clues list, tells how many blocks there are.
+ `minimum_requred_spaces` = required space count between the blocks. Depends if colored or not. If not colored, it is
  num_blocks - 1 because a space has to seperate each block. else, it is +1 for each block of the same color that are
  next to eachother.
+ `total_occupied_cells` = this is the minimum number of cells that has to be filled stated by the clue. its calculated
  with `total_block_length` + `minimum_required_spaces`.
+ `remaining_cells` = the number of "free" spaces that we can move around and create the combinations. it
  is `length_of_the_row` - `total_occupied_cells`
+ `gap_positions` = this is the number of gaps where free spaces can be put in. these gaps are between each block and at
  the start and the end, which means their number is `num_blocks`+ 1

Given this setup, the function uses combinatorial selection to generate all valid configurations:

**Combinatorial Selection:** The code selects gaps − 1 positions from a total of cells + gaps − 1 possible positions. This
is mathematically expressed as:

\[
\binom{\text{cells} + \text{gaps} - 1}{\text{gaps} - 1}
\]

This binomial coefficient represents the number of ways to choose positions for the gaps within the sequence of cells.

**Gap Size Calculation**: Once the positions of the gaps are selected, the code calculates the size of each gap between
the
blocks. If 𝑝<sub>1</sub>, 𝑝<sub>2</sub>, … , 𝑝<sub>𝑔 − 1</sub>
are the chosen positions, the gaps are computed as:

gaps_arr = [ 𝑝<sub>1</sub>, 𝑝<sub>2</sub> − 𝑝<sub>1</sub> − 1 , … , cells + gaps − 2 − 𝑝<sub>𝑔 − 1</sub>]

I initially thought this was caused because of the `to_cnf`function in the sympy library. In its documents, it is stated
that it uses a simple method to convert dnf to cnf. It just multiplies each variable with eachoder to make it cnf (*
PART BETTER DKFJGDLFK**) To solve this issue I implemented the tseytin transformation formula

### Block Start Approach

## Structure and Time Complexities of the Combinations Approach

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

- The number of possible coordinates to check is proportional to O(edge_length<sup>3</sup>).
- Overall: O(edge_length<sup>3</sup>).

### generate_combinations(n, blocks, block_colors)

This function generates all valid combinations for a row (or line) in the Nonogram, adhering to the constraints given
by the blocks and their respective block_colors.

It iterates over all possible positions where blocks can be placed in the row, taking into account the spaces between
them.

**Time Complexity:**

- The function explores all possible placements of blocks within a row, leading to a complexity of O(2<sup>n</sup>),
  where n is the
  length of the row.
- Overall: O(2<sup>n</sup>).

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
  complexity of O(2<sup>n</sup>), and this process is repeated for each row and column.
- Overall: O(m⋅2<sup>n</sup>), where m is the number of rows or columns and n is the number of cells in each row or
  column.

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

- Overall: O(m⋅2<sup>n</sup>+T), where T is the time taken by the SAT solver.

## Additional Information

