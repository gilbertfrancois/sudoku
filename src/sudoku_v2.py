import argparse
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

    def __init__(self, dim: int, max_steps: int = 10000, verbose: bool = False):
        self.dim: int = dim
        self.dim2: int = dim**2
        self.numbers: list[tuple[int, int, int]] = []
        self.grid: list[list[int]] = []
        self.grid_p: list[list[int]] = []
        self.grid_c: list[list[list[int]]] = []
        self.permutate: bool = False
        self.history: list[tuple[int, int, int]] = []
        self.chrono: float = 0.0
        self.max_steps: int = max_steps
        self.num_steps: int = 0
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

    def prefill_numbers(self, numbers: list[tuple[int, int, int]]) -> None:
        """
        Set the initial state of the digits.

        Parameters
        ----------
        numbers: list[tuple[int, int, int]]
            List with tuples, where every tuple denotes the (row, col, digit).

        """
        self.numbers = numbers
        self.reset()

    def solve(self) -> None:
        """
        Attempts to solve the puzzle.

        Returns
        -------
        bool
            True if the puzzle has been solved succesfully.
        """
        for row in range(self.dim2):
            for col in range(self.dim2):
                if self.grid[row][col] == 0:
                    for digit in range(1, self.dim2 + 1):
                        if self.possible(row, col, digit):
                            self.grid[row][col] = digit
                            self.solve()
                            self.grid[row][col] = 0
                        return

    def possible(self, row: int, col: int, digit: int) -> bool:
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

        step = 0
        prev_total_sum = -1
        stuck_count = 0
        all_solved = False
        tic = time.time()
        while step < self.max_steps:
            self._find_candidates()
            self._sole_candidate()
            all_solved, total_sum = self._all_solved()
            if all_solved:
                break
            # No change since last iteration. Do a permutation...
            if total_sum == prev_total_sum:
                self.permutate = True
                stuck_count += 1
            # If permutations don't work in this state, reset and start again.
            if stuck_count > 3:
                stuck_count = 0
                self.reset()
            prev_total_sum = total_sum
            step += 1
        toc = time.time()
        self.chrono = toc - tic
        self.num_steps = step
        return self.is_solved()

    def reset(self):
        """
        Resets the puzzle to its initial state and clears the history.
        """
        if self.verbose:
            print("reset")
        self.grid = self._make_2D_grid()
        self.grid_p = self._make_2D_grid()
        self.grid_c = self._make_3D_grid()
        self.permutate = False
        for i in self.numbers:
            self.grid[i[0] - 1][i[1] - 1] = i[2]
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

    def _make_3D_grid(self):
        grid = [
            [[0 for _ in range(self.dim2)] for _ in range(self.dim2)] for _ in range(9)
        ]
        return grid

    def _count_occurrance(self, value: int, pos: tuple[int, int]):
        count = 0
        for col in range(self.dim2):
            if self.grid[pos[0]][col] == value:
                count += 1
        for row in range(self.dim2):
            if self.grid[row][pos[1]] == value:
                count += 1
        row_min = (pos[0] // self.dim) * self.dim
        row_max = row_min + self.dim
        col_min = (pos[1] // self.dim) * self.dim
        col_max = col_min + self.dim
        for row in range(row_min, row_max):
            for col in range(col_min, col_max):
                if self.grid[row][col] == value:
                    count += 1
        return count

    def _str_3_to_numbers(self, data):
        numbers = []
        for line in data:
            numbers.append((int(line[0]), int(line[1]), int(line[2])))
        self.prefill_numbers(numbers)

    def _str_9_to_numbers(self, data):
        numbers = []
        for row in range(9):
            for col in range(9):
                value = data[row][col]
                if value in [".", "0", "_", "-", "x"]:
                    continue
                numbers.append((row + 1, col + 1, int(value)))
        self.prefill_numbers(numbers)

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
    parser.add_argument(
        "-s",
        "--max-steps",
        required=False,
        default=10000,
        help="Maximum number of steps",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    sudoku = Sudoku(3, max_steps=args.max_steps, verbose=args.verbose)
    sudoku.load(args.filename)
    sudoku.message_line("start")
    print(sudoku)
    status = sudoku.solve()
    if not status:
        print(sudoku.message_line("warning"))
        print("Unable to find a solution.")
    print(sudoku.message_line("solution"))
    print(sudoku)
    if args.verbose:
        print(sudoku.message_line("history"))
        print(sudoku.history)
        print(sudoku.message_line("statistics"))
        print(f"Chrono: {sudoku.chrono:0.3f} seconds")
        print(f"Number of steps: {sudoku.num_steps}")
        print(f"Number of fills: {len(sudoku.history)}")
