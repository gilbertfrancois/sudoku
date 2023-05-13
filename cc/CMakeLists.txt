cmake_minimum_required(VERSION 3.18)
project(sudoku)

add_compile_options(-Wall -Werror) 

add_executable(sudoku src/ndarray.c src/sudoku.c)
