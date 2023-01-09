import argparse
import math
import os
import random
import time


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
        self.history: list[tuple[int, int, int]] = []
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

    def _prefill_numbers(self, numbers: list[tuple[int, int, int]]) -> None:
        """
        Set the initial state of the digits.

        Parameters
        ----------
        numbers: list[tuple[int, int, int]]
            List with tuples, where every tuple denotes the (row, col, digit).

        """
        self.numbers = numbers
        self.reset()

    def solve(self) -> bool:
        """
        Attempts to solve the puzzle.

        Returns
        -------
        bool
            True if the puzzle has been solved succesfully.
        """
        tic = time.time()
        status = self._solve(depth=0)
        toc = time.time()
        self.chrono = toc - tic
        return status

    def reset(self):
        """
        Resets the puzzle to its initial state and clears the history.
        """
        if self.verbose:
            print("reset")
        self.grid = self._make_2D_grid()
        for i in self.numbers:
            self.grid[i[0]][i[1]] = i[2]
        self.history = []

    def is_solved(self) -> bool:
        """
        Returns true if the current puzzle has been solved and all digits have been
        filled in.

        Returns
        -------
        bool
            True if the puzzle has been solved.
        """
        all_solved, _ = self._all_solved()
        return all_solved

    def _solve(self, depth) -> bool:
        if self.verbose:
            print(f"Depth: {depth: 4d}")
        for row in range(self.dim2):
            for col in range(self.dim2):
                if self.grid[row][col] == 0:
                    status = False
                    for digit in range(1, self.dim2 + 1):
                        if self._possible(row, col, digit):
                            self.grid[row][col] = digit
                            self.history.append((row, col, digit))
                            status = self._solve(depth + 1)
                            if not status:
                                self.grid[row][col] = 0
                                self.history.append((row, col, 0))
                    return status
        return True

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
        return self._to_str()

    def _to_str(self, show_prob: bool = False) -> str:
        if show_prob:
            grid = self.grid_p
        else:
            grid = self.grid
        out = ""
        for row in range(len(grid)):
            for col in range(len(grid[0])):
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

    def _all_solved(self) -> tuple[bool, int]:
        status = True
        checksum = 0
        for i in range(self.dim2):
            checksum += i + 1
        total_sum = 0
        for row in range(self.dim2):
            row_sum = 0
            for col in range(self.dim2):
                row_sum += self.grid[row][col]
            if row_sum != checksum:
                status = False
            total_sum += row_sum
        return status, total_sum

    def _make_2D_grid(self):
        grid = [[0 for _ in range(self.dim2)] for _ in range(self.dim2)]
        return grid

    def _str_3_to_numbers(self, data):
        numbers = []
        for line in data:
            numbers.append((int(line[0] - 1), int(line[1] - 1), int(line[2])))
        self._prefill_numbers(numbers)

    def _str_9_to_numbers(self, data):
        numbers = []
        for row in range(9):
            for col in range(9):
                value = data[row][col]
                if value in [".", "0", "_", "-", "x"]:
                    continue
                numbers.append((row, col, int(value)))
        self._prefill_numbers(numbers)

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
    sudoku.message_line("start")
    print(sudoku)
    depth = 0
    status = sudoku.solve()
    if not status:
        print(sudoku.message_line("warning"))
        print("Unable to find a solution.")
    print(sudoku.message_line("solution"))
    print(sudoku)
    print(sudoku.message_line("statistics"))
    print(f"Chrono: {sudoku.chrono:0.9f} seconds")
    print(f"Number of steps: {len(sudoku.history)}")
    # if args.verbose:
    #     print(sudoku.message_line("history"))
    #     print(sudoku.history)
