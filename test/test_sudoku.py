from unittest import TestCase

from sudoku import Sudoku


def solve_puzzle_from_file(filename: str) -> tuple[bool, bool]:
    sudoku = Sudoku()
    sudoku.load(filename)
    num_solutions = sudoku.solve()
    is_solved = sudoku.is_solved()
    return num_solutions, is_solved


class TestSudoku(TestCase):
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
