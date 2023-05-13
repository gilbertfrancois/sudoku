#ifndef SUDOKU_H
#define SUDOKU_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include "ndarray.h"

const int STATUS_OK = 0;
const int ERROR_FILEREAD = 1<<0;
const int ERROR_INVALID_SUDOKU = 1<<1;

typedef struct {
    int dim;
    int dim2;
    int dim3;
    NDArray *grid;
    int n_solutions;
    int len_solutions;
    NDArray *solutions;
    double chrono;
} Sudoku;

int sudoku_init(Sudoku *s, char *filename);

void sudoku_free(Sudoku *s); 

void sudoku_solve(Sudoku *s);

void sudoku_print(Sudoku *s, NDArray *a); 

void message_line(char *message);

void _solve(Sudoku *s, int depth);

bool _possible(Sudoku *s, int row, int col, int digit);

int _readfile(char *filename, data_t *buffer, const int buffer_size, int *dim3);

int main(int argc, char *argv[]);

#endif
