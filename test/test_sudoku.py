from unittest import TestCase

from sudoku import Sudoku


def solve_puzzle_from_file(filename: str) -> tuple[bool, bool]:
    sudoku = Sudoku()
    sudoku.load(filename)
    status = sudoku.solve()
    is_solved = sudoku.is_solved()
    return status, is_solved


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

    def test_examples(self):
        filenames = [
            "../examples/easy_001.txt",
            "../examples/easy_002.txt",
            "../examples/easy_003.txt",
            "../examples/medium_001.txt",
            "../examples/medium_002.txt",
            "../examples/hard_001.txt",
            "../examples/hard_002.txt",
            "../examples/expert_001.txt",
            "../examples/expert_002.txt",
            "../examples/evil_001.txt",
            "../examples/evil_002.txt",
        ]
        for filename in filenames:
            status, is_solved = solve_puzzle_from_file(filename)
            self.assertTrue(status)
            self.assertTrue(is_solved)
