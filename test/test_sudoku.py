from unittest import TestCase
import pytest

from sudoku import Sudoku


def solve_puzzle_from_file(filename: str) -> tuple[int, bool]:
    sudoku = Sudoku()
    sudoku.load(filename)
    num_solutions = sudoku.solve()
    is_solved = sudoku.is_solved()
    return num_solutions, is_solved


class TestSudoku(TestCase):
    def test_filenotfound_exception(self):
        sudoku = Sudoku()
        with pytest.raises(FileNotFoundError) as exc_info:
            sudoku.load("doesnotexist.txt")
        exception_raised = exc_info.value
        print(exception_raised)

    def test_wrong_dim_exception_1(self):
        with pytest.raises(ValueError) as exc_info:
            _ = Sudoku(25)
        exception_raised = exc_info.value
        self.assertEqual(
            "Invalid dimension. Expected 4, 9, or 16, actual 25.",
            exception_raised.__str__(),
        )

    def test_wrong_dim_exception_2(self):
        with pytest.raises(ValueError) as exc_info:
            _ = Sudoku(10)
        exception_raised = exc_info.value
        self.assertEqual("Invalid value. 9 != 10.", exception_raised.__str__())

    def test_verbose(self):
        sudoku = Sudoku(verbose=True)
        sudoku.load("../examples/easy_001.txt")
        sudoku.reset()
        sudoku.solve()
        sudoku.is_solved()

    def test_reset(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_001.txt")
        grid1 = sudoku._copy_grid(sudoku.grid)
        sudoku.solve()
        sudoku.reset()
        grid2 = sudoku._copy_grid(sudoku.grid)
        for i in range(len(grid1)):
            for j in range(len(grid1[i])):
                self.assertEqual(grid1[i][j], grid2[i][j])

    def test_init_repr_(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_001.txt")
        out = sudoku.__repr__()
        self.assertTrue(isinstance(out, str))
        self.assertTrue("." in out)

    def test_solved_repr_(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_001.txt")
        sudoku.solve()
        out = sudoku.__repr__()
        self.assertTrue(isinstance(out, str))
        self.assertFalse("." in out)

    def test_message_line(self):
        sudoku = Sudoku()
        out = sudoku.message_line("123")
        self.assertTrue(isinstance(out, str))
        self.assertEqual(len(out), 80)
        out = sudoku.message_line("1234567890")
        self.assertEqual(len(out), 80)

    def test_grid(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_003.txt")
        self.assertEqual(sudoku.grid[0][0], 5)
        self.assertEqual(sudoku.grid[0][1], 3)
        self.assertEqual(sudoku.grid[8][4], 8)
        self.assertEqual(sudoku.grid[4][8], 1)

    def test_possible_true(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_003.txt")
        status = sudoku._possible(4, 4, 5)
        self.assertTrue(status)

    def test_possible_false(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_003.txt")
        status = sudoku._possible(4, 4, 3)
        self.assertFalse(status)

    def test_cell_possible_true(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_003.txt")
        status = sudoku._possible(0, 7, 1)
        self.assertTrue(status)

    def test_cell_possible_false(self):
        sudoku = Sudoku()
        sudoku.load("../examples/easy_003.txt")
        status = sudoku._possible(5, 1, 8)
        self.assertFalse(status)

    def test_easy(self):
        filenames = [
            "../examples/easy_001.txt",
            "../examples/easy_002.txt",
            "../examples/easy_003.txt",
        ]
        for filename in filenames:
            num_solutions, is_solved = solve_puzzle_from_file(filename)
            self.assertEqual(num_solutions, 1)
            self.assertTrue(is_solved)

    def test_medium(self):
        filenames = [
            "../examples/medium_001.txt",
            "../examples/medium_002.txt",
        ]
        for filename in filenames:
            num_solutions, is_solved = solve_puzzle_from_file(filename)
            self.assertEqual(num_solutions, 1)
            self.assertTrue(is_solved)

    def test_hard(self):
        filenames = [
            "../examples/hard_001.txt",
            "../examples/hard_002.txt",
        ]
        for filename in filenames:
            num_solutions, is_solved = solve_puzzle_from_file(filename)
            self.assertEqual(num_solutions, 1)
            self.assertTrue(is_solved)

    def test_expert(self):
        filenames = [
            "../examples/expert_001.txt",
            "../examples/expert_002.txt",
        ]
        for filename in filenames:
            num_solutions, is_solved = solve_puzzle_from_file(filename)
            self.assertEqual(num_solutions, 1)
            self.assertTrue(is_solved)

    def test_evil(self):
        filenames = [
            "../examples/evil_001.txt",
            "../examples/evil_002.txt",
        ]
        for filename in filenames:
            num_solutions, is_solved = solve_puzzle_from_file(filename)
            self.assertEqual(num_solutions, 1)
            self.assertTrue(is_solved)

    def test_non_unique(self):
        filenames = [
            "../examples/non_unique_001.txt",
            "../examples/non_unique_002.txt",
        ]
        for filename in filenames:
            num_solutions, is_solved = solve_puzzle_from_file(filename)
            self.assertGreater(num_solutions, 1)
            self.assertTrue(is_solved)
