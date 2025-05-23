# Repository for AI Project 1.3

**Assignment:** [Solve Nonograms](https://kwarc.info/teaching/AISysProj/SS24/assignment-1.3.pdf)

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
    - **Usage in the Project**: `combinations` (imported as `itertools_combinations`)**: The `combinations` function
      generates all possible combinations of a specified length from the input iterable. In this
      project, `itertools_combinations` is used to generate possible placements of blocks within the puzzle rows or
      columns.
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

For this project, I experimented with two distinct approaches. Initially, I generated all possible block combinations
based on the clues and passed them to the SAT solver. This method worked well for small boards, but as the board size
grew beyond 10x10, the processing time became increasingly impractical.

To address this, I developed a second approach that focused on creating rules based on the starting positions of the
blocks and their interactions, rather than brute-forcing every possible combination. This rule-based method proved to be
exponentially faster, reducing solving times from over an hour to just a few minutes for larger puzzles. Here's what I
did and learned while implementing both approaches:

### Combinations Approach

In both approaches, I begin by extracting the board information from the `.clues` file. The shape, color, and hints are
then passed to the `generate_dnf` function. Within this function, the board is constructed based on the shape
information,
and each cell is added to the `variables` list. Next, the hints are categorized by their axis ("row", "col", "x", "y", "
z") and sent to the `generate_combinations` function, which calculates necessary variables and generates all possible
combinations for each row.

+ `total_block_length`= sum of all block clues.
+ `num_blocks`= The number of blocks, determined by the length of the block clues list.
+ `minimum_requred_spaces` = The minimum number of spaces required between blocks. If the blocks are not colored, this
  is 'num_blocks - 1' (one space between each block). If colored, it includes additional spaces between adjacent blocks
  of
  the same color.
+ `total_occupied_cells` = The minimum number of cells that must be filled, calculated
  as `total_block_length` + `minimum_required_spaces`.
+ `remaining_cells` = The number of free spaces available for creating combinations, computed
  as `length_of_the_row` - `total_occupied_cells`
+ `gap_positions` = The number of gaps where free spaces can be inserted. This includes gaps between blocks and at the
  start and end, resulting in `num_blocks + 1` gaps

Given this setup, the function uses combinatorial selection to generate all valid configurations:

**Combinatorial Selection:** The code selects gaps − 1 positions from a total of cells + gaps − 1 possible positions.
This is expressed as:

> (cells + gaps - 1, gaps - 1)

This binomial coefficient represents the number of ways to choose positions for the gaps within the sequence of cells.

**Gap Size Calculation**: Once the positions of the gaps are selected, the code calculates the size of each gap between
the blocks. If 𝑝<sub>1</sub>, 𝑝<sub>2</sub>, … , 𝑝<sub>𝑔 − 1</sub> are the chosen positions, the gaps are computed as:

gaps_arr = [𝑝<sub>1</sub>, 𝑝<sub>2</sub> − 𝑝<sub>1</sub> − 1 , … , cells + gaps − 2 − 𝑝<sub>𝑔 − 1</sub>]
The combinations are generated as sequences of 1s and 0s to represent filled and unfilled blocks, and this information
is sent back. In the DNF (Disjunctive Normal Form) stage, cells in the row are marked with Not if they are empty and
combined with `And` operators within each combination, and `Or` operators between different combinations. Once all
combinations are processed, these DNF formulas are converted to CNF (Conjunctive Normal Form) using the `dnf_to_cnf`
function to make them suitable for the SAT solver.

Initially, the `to_cnf` function was used for this conversion, but it became too slow as board sizes increased. This
function's complexity grows exponentially with the number of cells due to its variable distribution method. To address
this, I implemented the Tseytin transformation, which introduces auxiliary variables to manage complexity better. This
allowed the script to handle boards larger than 10x10, but it still struggled with boards approaching 20x20. As the
inefficiencies became evident, alternative approaches were explored for even larger boards.

### Block Start Approach

Initially, I considered finding a more powerful computer to run my code, but after discussing it with Mrs. Schafer, I
realized that wouldn't significantly improve performance. Instead, I implemented a new approach. Rather than generating
every possible combination for each cell, I focused on creating arguments based on the clues for each row, following
four specific rules:

1. **Start Implies No Other Start:**
   If a block starts at a certain location, the next block cannot start in any of the cells from the beginning of the
   row to the end of the current block's length, plus one additional cell if they are the same color.

_(S<sub>i_rc</sub> where i = start number, r = row coordinate, c = column coordinate)_

> S<sub>1_01</sub> ⇒ ~S<sub>2_00</sub> ∧ ~S<sub>2_01</sub> ∧ ~S<sub>3_00</sub> ∧ ~S<sub>3_01</sub> ∧ ... ∧ ~S<sub>
> n_01</sub>

2. **There Can Only Be One Start:**
   Only one start is allowed for each block. Initially, I used XOR, but I learned that XOR allows for an odd number of
   true starts, not just one. Instead, I used the following formula.

> (S<sub>1_00</sub> ∨ S<sub>1_01</sub> ∨ S<sub>1_02</sub>)  ∧ (~S<sub>1_00</sub> ∨ ~S<sub>1_01</sub>) ∧ (~S<sub>
> 1_00</sub> ∨ ~S<sub>1_02</sub>)  ∧ (~S<sub>1_01</sub> ∨ ~S<sub>1_02</sub>)

3. **Start Implies Cells Here:**
   If a block starts at a particular position, all cells that it occupies must be true (filled).

> S<sub>1_01</sub> ⇒ C<sub>01</sub> ∧ C<sub>02</sub> ∧ ... ∧ C<sub>0n</sub>

4. **Cell Here Implies a Start:**
   If a cell is true (filled), it implies that one of the starts covering that cell must be true.

> C<sub>02</sub> ⇒ S<sub>1_00</sub> ∨ S<sub>1_01</sub> ∨ ... ∨ S<sub>n_02</sub>

Implementing these rules, rather than calculating all possible combinations, significantly reduced the complexity. As a
result, the script was able to solve each board in just a matter of minutes.

## Structure and Time Complexities of the Combinations Approach

### get_content(filename)

This function reads and parses the Nonogram puzzle configuration from a file. T

**Time Complexity:** O(N), where N is the number of lines in the file.

### create_hex_board(edge_length)

This function generates the coordinates of a hexagonal grid based on a specified edge length.

**Time Complexity:** O(edge_length<sup>3</sup>).

### generate_combinations(n, blocks, block_colors)

This function generates all valid combinations for a row (or line) in the Nonogram. It iterates over all possible
positions where blocks can be placed in the row, taking into account the spaces between them.

**Time Complexity:** O(2<sup>n</sup>), where n is the length of the row.

### tseytin_transformation(expr)

This function converts a given logical expression into Conjunctive Normal Form (CNF) using Tseytin transformation.
The Tseytin transformation introduces auxiliary variables to represent sub-expressions, ensuring the output CNF
remains linear in size relative to the input expression.

**Time Complexity:** O(k), where k is the number of sub-expressions.

### generate_dnf(shape, hints)

It calls generate_combinations() to find all valid row configurations and then constructs the DNF expression
accordingly.

**Time Complexity:** O(m⋅2<sup>n</sup>), where m is the number of rows or columns and n is the number of cells in each
row or column.

### sympy_to_cnf(shape, sympy_expr)

This function converts a logical expression from SymPy format into Conjunctive Normal Form (CNF). It also maps the
logical variables to integer IDs for compatibility with the SAT solver.

**Time Complexity:** O(k).

### sat_solver(shape, sympy_expr)

This function uses a SAT solver to determine whether the CNF formula generated from the Nonogram constraints is
satisfiable. If satisfiable, it finds a solution (model) that satisfies all the constraints.

SAT solving is an NP-complete problem, and its complexity can be exponential in the size of the input formula. The time
complexity is O(T), where T is the time taken by the SAT solver.

**Time Complexity:** O(T), with T potentially being exponential.

### write_model_to_file(model, shape, hints, filename)

This function writes the solution model obtained from the SAT solver to a file.

**Time Complexity:** :O(V), where V is the number of grid cells.

## Structure and Time Complexities of the Block Start Approach

Here are the two new functions implemented for this approach.

### exactly_one_true(clauses)

This function generates a CNF formula ensuring that exactly one of the given clauses is true. It does this by
creating constraints that at least one clause is true and that no two clauses can be true simultaneously.

**Time Complexity:** O(K²) where K is the number of clauses. The pairwise combination of clauses results in quadratic
complexity.

### create_start_args(index, length, axis, hint_numbers, hint_colors, coordinates=None)

This function generates CNF arguments for a given axis (row, column, or diagonal) based on the provided hints. It
constructs clauses to ensure blocks are placed according to the hints and prevent conflicting placements.

It tracks the variables required by each rule:

+ **Rule 1:** If the block is not the last one, it creates a clause ensuring that the next block cannot start in any of
  the cells up to the end of the current block plus one additional cell.
+ **Rule 2:** It monitors all possible start locations for a block and sends these to the exactly_one_true() function to
  ensure only one start is true.
+ **Rule 3:** It creates clauses to ensure that if a block's start is true, the cells occupied by this block must also
  be true.
+ **Rule 4:** It uses a dictionary to track all cells in the row and adds the start variable to the list of each cell
  that the start covers.

**Time Complexity:** O(L × B × (L + B)) where L is the length of the row/column/axis and B is the number of blocks (or
hints). The complexity arises from iterating over all possible start positions and blocks.
