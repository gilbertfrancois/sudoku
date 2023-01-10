"""
Sudoku Solver
Copyright (C) 2022  Gilbert Francois Duivesteijn

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import math
import os
import time
from typing import Optional


class Sudoku:
    """
    Sudoku solver

    Example
    -------
    >>> sudoku = Sudoku()
    >>> sudoku.load("mydata.txt")
    >>> sudoku.solve()
    >>> print(sudoku)

    """

    def __init__(self, dim2: int = 9, verbose: bool = False):
        _dim = math.sqrt(dim2)
        if int(_dim) ** 2 != dim2:
            raise ValueError(f"Invalid value. {int(_dim)**2} != {dim2}.")
        if dim2 not in [4, 9, 16]:
            raise ValueError(f"Invalid dimension. Expected 4, 9, or 16, actual {dim2}.")
        self.dim: int = int(_dim)
        self.dim2: int = dim2
        self.numbers: list[tuple[int, int, int]] = []
        self.grid: list[list[int]] = []
        self.all_solutions: list[list[list[int]]] = []
        self.chrono: float = 0.0
        self.verbose: bool = verbose
        self.reset()

    def load(self, filepath: str) -> None:
        """
        Loads the data file with the initial state. The data file is a plain text
        file with the initial state written as a grid or as a list of (row, col, digit).
        or list format.

        Example of the grid format:
        ```
        .9. .1. ..7
        ..5 76. ..4
        .2. ... ..6

        .5. .7. 9..
        ... ... ...
        4.. .8. ..1

        ... 2.6 ...
        ..2 ..8 1..
        .8. .5. 3..
        ```

        Example of the list format (of the first 2 rows):
        ```
        # row col digit
        1 2 9
        1 5 1
        1 9 7
        2 3 5
        2 4 7
        2 5 6
        2 9 4
        ```

        Parameters
        ----------
        filepath: str
            File path of the data file.

        """
        if not os.path.exists(filepath):
            raise FileExistsError(f"File {filepath} does not exist.")
        with open(filepath, "r", encoding="utf-8") as file:
            data = file.read()
        data = self._clean_input_data(data)
        if len(data[0]) == 3:
            self._str_3_to_numbers(data)
        elif len(data[0]) == 9:
            self._str_9_to_numbers(data)

    def solve(self) -> int:
        """
        Attempts to solve the puzzle.

        Returns
        -------
        bool
            True if the puzzle has been solved succesfully.
        """
        tic = time.time()
        self._solve(depth=0)
        toc = time.time()
        self.chrono = toc - tic
        return len(self.all_solutions)

    def reset(self, numbers: Optional[list[tuple[int, int, int]]] = None):
        """
        Resets the puzzle to its initial state.

        Parameters
        ----------
        numbers: list[tuple[int, int, int]] or None
            List with tuples, where every tuple denotes the (row, col, digit).

        """
        if numbers is not None:
            self.numbers = numbers
        if self.verbose:
            print("reset")
        self.grid = self._make_2d_grid()
        for i in self.numbers:
            self.grid[i[0]][i[1]] = i[2]

    def is_solved(self) -> bool:
        """
        Returns true if the current puzzle has been solved and all digits have been
        filled in.

        Returns
        -------
        bool
            True if the puzzle has been solved.
        """
        return len(self.all_solutions) > 0

    def message_line(self, message: str) -> str:
        """
        Print a fancy message line, 80 columns wide.

        Parameters
        ----------
        message: str
            Message

        Returns
        -------
        str
            Formatted message as string.
        """
        line = f"\n---[ {message} ]"
        line = line + "-" * (80 - len(line)) + "\n"
        return line

    def _solve(self, depth: int) -> None:
        """
        Recursive function. It searches for an empty cell and
        fills in the first possible digit. Then it calls itself
        to find the next empty cell. When it is stuck and cannot
        fill in a possible digit, it unrolls to the point where it can
        try another digit and starts recursing again from this
        point.

        Parameters
        ----------
        depth: int
            Recursive depth, used for verbose output only.

        """
        if self.verbose:
            print(f"Depth: {depth: 4d}")
        for row in range(self.dim2):
            for col in range(self.dim2):
                if self.grid[row][col] == 0:
                    for digit in range(1, self.dim2 + 1):
                        if self._possible(row, col, digit):
                            self.grid[row][col] = digit
                            self._solve(depth + 1)
                            self.grid[row][col] = 0
                    return
        if self._all_solved():
            self.all_solutions.append(self._copy_grid(self.grid))

    def _possible(self, row: int, col: int, digit: int) -> bool:
        for i in range(self.dim2):
            if self.grid[i][col] == digit:
                return False
        for j in range(self.dim2):
            if self.grid[row][j] == digit:
                return False
        row0 = (row // self.dim) * self.dim
        col0 = (col // self.dim) * self.dim
        for i in range(self.dim):
            for j in range(self.dim):
                if self.grid[row0 + i][col0 + j] == digit:
                    return False
        return True

    def __repr__(self) -> str:
        grid = self.grid
        if len(self.all_solutions) == 1:
            grid = self.all_solutions[0]
        elif len(self.all_solutions) > 1:
            return f"Iterate sudoku.all_grids to see all {len(self.all_solutions)} solutions."
        out = ""
        for row in range(self.dim2):
            for col in range(self.dim2):
                val = grid[row][col]
                val = str(val) if val > 0 else "."
                out += f"{val} "
                if (col + 1) % (self.dim) == 0:
                    out += " "
            if row < 8:
                out += "\n"
            if row < 8 and (row + 1) % (self.dim) == 0:
                out += "\n"
        return out

    def _all_solved(self) -> bool:
        _status = True
        _total_sum = 0
        _checksum = 0
        for i in range(self.dim2):
            _checksum += i + 1
        for row in range(self.dim2):
            row_sum = 0
            for col in range(self.dim2):
                row_sum += self.grid[row][col]
            if row_sum != _checksum:
                _status = False
            _total_sum += row_sum
        return _status

    def _make_2d_grid(self) -> list[list[int]]:
        grid = [[0 for _ in range(self.dim2)] for _ in range(self.dim2)]
        return grid

    def _str_3_to_numbers(self, data):
        numbers = []
        for line in data:
            numbers.append((int(line[0] - 1), int(line[1] - 1), int(line[2])))
        self.reset(numbers)

    def _str_9_to_numbers(self, data):
        numbers = []
        for row in range(9):
            for col in range(9):
                value = data[row][col]
                if value in [".", "0", "_", "-", "x"]:
                    continue
                numbers.append((row, col, int(value)))
        self.reset(numbers)

    def _clean_input_data(self, data: list[str] | str) -> list[str]:
        if isinstance(data, str):
            data = data.split("\n")
        str_lines = []
        for line in data:
            # Clean input and make a compact representation
            line = line.replace("\n", "")
            line = line.replace("\r", "")
            tokens = line.split()
            # Skip empty lines
            if len(tokens) == 0:
                continue
            # Skip comment lines
            if tokens[0] in ["#", "/", "!", "'"]:
                continue
            str_line = "".join(tokens)
            if len(str_line) != 3 and len(str_line) != 9:
                raise RuntimeError("Error reading file format.")
            str_lines.append(str_line)
        return str_lines

    def _copy_grid(self, src: list[list[int]]) -> list[list[int]]:
        dst = self._make_2d_grid()
        for i in range(self.dim2):
            for j in range(self.dim2):
                dst[i][j] = src[i][j]
        return dst


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Sudoku solver",
        description="Attempts to solve your Sudoku.",
    )
    parser.add_argument("filename", help="File path of the input data.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    sudoku = Sudoku(9, verbose=args.verbose)
    sudoku.load(args.filename)
    print(sudoku.message_line("Sudoku solver, (C) 2022 Gilbert Francois Duivesteijn"))
    print(sudoku)
    NUM_SOLUTIONS = sudoku.solve()
    if NUM_SOLUTIONS == 0:
        print(sudoku.message_line("warning"))
        print("Unable to find a solution.")
    print(sudoku.message_line("solution"))
    print(sudoku)
    print(sudoku.message_line("statistics"))
    print(f"Solution is unique: {NUM_SOLUTIONS == 1}")
    if NUM_SOLUTIONS > 1:
        print(f"Number of possible solutions: {NUM_SOLUTIONS}")
    print(f"Chrono: {sudoku.chrono:0.4f} seconds")
