#include "sudoku.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

int sudoku_init(Sudoku *s, char *filename) {
    const int bufsize = 1024;
    data_t *buffer = (data_t *)malloc(bufsize * sizeof(data_t));
    int dim3 = 0;
    int status = _readfile(filename, buffer, bufsize, &dim3);
    if (status > 0)
        exit(status);
    // Check if the file is a valid sudoku puzzle.
    switch (dim3) {
    case 16:
        s->dim = 2;
        break;
    case 81:
        s->dim = 3;
        break;
    default:
        s->dim = 0;
        break;
    }
    if (s->dim == 0) {
        printf("Runtime error: Sudoku file seems inconsistent. Expected size 16, or 81. Actual: %d.", dim3);
        return status + ERROR_INVALID_SUDOKU;
    }
    s->dim2 = s->dim * s->dim;
    s->dim3 = s->dim2 * s->dim2;
    int shape[2] = {s->dim2, s->dim2};
    // Allocate memory for the sudoku grid
    s->grid = (NDArray *)malloc(sizeof(NDArray));
    ndarray_init(s->grid, shape, 2);
    // Copy the values from the buffer into the grid
    memcpy(s->grid->data, buffer, s->dim3 * sizeof(data_t));
    s->n_solutions = 0;
    s->len_solutions = 0;
    s->chrono = 0.0;
    free(buffer);
    return status;
}

void sudoku_append_solution(Sudoku *s) {
    s->n_solutions = s->n_solutions + 1;
    if (s->n_solutions == 1) {
        s->solutions = (NDArray *)malloc(sizeof(NDArray) * s->n_solutions);
    }
    else {
        s->solutions = (NDArray *)realloc(s->solutions, sizeof(NDArray) * s->n_solutions);
    }
    ndarray_copy(&(s->solutions[s->n_solutions - 1]), s->grid);
}

void sudoku_free(Sudoku *s) {
    ndarray_free(s->grid);
    free(s->grid);
    if (s->n_solutions > 0) {
        for (int i = 0; i < s->n_solutions; i++) {
            ndarray_free(&(s->solutions[i]));
        }
        free(s->solutions);
    }
}

void sudoku_solve(Sudoku *s) {
    clock_t tic = clock();
    _solve(s, 0);
    clock_t toc = clock();
    s->chrono = ((double)(toc - tic)) / CLOCKS_PER_SEC;
}

void sudoku_print(Sudoku *s, NDArray *a) {
    for (int i = 0; i < s->dim2; i++) {
        if (i > 0 && i % s->dim == 0)
            printf("\n");
        for (int j = 0; j < s->dim2; j++) {
            if (j > 0 && j % s->dim == 0)
                printf(" ");
            int k = i * a->strides[0] + j * a->strides[1];
            if (a->data[k] == 0)
                printf("%s ", ".");
            else
                printf("%d ", a->data[k]);
        }
        printf("\n");
    }
}

void _solve(Sudoku *s, int depth) {
    for (int row = 0; row < s->dim2; row++) {
        for (int col = 0; col < s->dim2; col++) {
            int k = row * s->grid->strides[0] + col * s->grid->strides[1];
            if (s->grid->data[k] == 0) {
                for (int digit = 1; digit < s->dim2 + 1; digit++) {
                    if (_possible(s, row, col, digit)) {
                        s->grid->data[k] = digit;
                        _solve(s, depth + 1);
                        s->grid->data[k] = 0;
                    }
                }
                return;
            }
        }
    }
    sudoku_append_solution(s);
}

bool _possible(Sudoku *s, int row, int col, int digit) {
    for (int i = 0; i < s->dim2; i++) {
        int k = i * s->grid->strides[0] + col * s->grid->strides[1];
        if (s->grid->data[k] == digit)
            return false;
    }
    for (int j = 0; j < s->dim2; j++) {
        int k = row * s->grid->strides[0] + j * s->grid->strides[1];
        if (s->grid->data[k] == digit)
            return false;
    }
    int row0 = (row / s->dim) * s->dim;
    int col0 = (col / s->dim) * s->dim;
    for (int i = 0; i < s->dim; i++) {
        for (int j = 0; j < s->dim; j++) {
            int k = (row0 + i) * s->grid->strides[0] + (col0 + j) * s->grid->strides[1];
            if (s->grid->data[k] == digit)
                return false;
        }
    }
    return true;
}

int _readfile(char *filename, data_t *buffer, const int buffer_size, int *dim3) {
    FILE *fp;
    fp = fopen(filename, "r");
    if (fp == NULL) {
        printf("Error: File %s not found.\n", filename);
        return ERROR_FILEREAD;
    }
    char c;
    int cursor = 0;
    while ((c = fgetc(fp)) != EOF) {
        // EOF fix for Raspberian.
        if (feof(fp))
            break;
        if (cursor > buffer_size - 2) {
            printf("Reached end of buffer count: %d. Is this a valid sudoku file?\n", cursor);
            return ERROR_FILEREAD;
        }
        if (c > 47 && c < 58) {
            buffer[cursor] = (data_t)atoi(&c);
            cursor++;
        }
        if (c == '.' || c == '_' || c == '-' || c == 'x') {
            buffer[cursor] = (data_t)0;
            cursor++;
        }
    }
    *dim3 = cursor;
    fclose(fp);
    return STATUS_OK;
}

void message_line(char *message) {
    // Prevent buffer overflow.
    if (strlen(message) > 73) {
        return;
    }
    char line[80] = "";
    strcat(line, "\n---[ ");
    strcat(line, message);
    strcat(line, " ]");
    unsigned long line_len = strlen(line);
    for (int i = 0; i < 79 - line_len; i++) {
        strcat(line, "-");
    }
    printf("%s\n\n", line);
}

int main(int argc, char *argv[]) {
    // Parse arguments
    const char options[] = {"h"};
    char *filepath;
    int opt;
    do {
        switch (opt = getopt(argc, argv, options)) {
        case -1:
            filepath = argv[optind];
            break;
        case 'h':
        default:
            printf("Usage: sudoku <filename>\n");
            exit(1);
        }
    } while (opt >= 0);
    // Init Sudoku
    message_line("Sudoku solver, (C) 2023 Gilbert Francois Duivesteijn");
    int status = STATUS_OK;
    Sudoku s;
    status = sudoku_init(&s, filepath);
    if (status > 0)
        exit(status);
    sudoku_print(&s, &s.grid[0]);
    // Solve
    sudoku_solve(&s);
    // Print solution(s)
    if (s.n_solutions == 1) {
        message_line("solution");
        sudoku_print(&s, &s.solutions[0]);
    } else if (s.n_solutions < 10) {
        message_line("solutions");
        for (int i = 0; i < s.n_solutions; i++) {
            sudoku_print(&s, &s.solutions[i]);
        }
    }
    // Show some statistics
    message_line("statistics");
    char *is_unique = (s.n_solutions == 1) ? "yes" : "no";
    printf("Solution is unique: %s\n", is_unique);
    if (s.n_solutions > 1) {
        printf("Number of possible solutions: %d\n", s.n_solutions);
    }
    printf("Chrono: %0.5f seconds\n", s.chrono);
    // Cleanup and exit
    sudoku_free(&s);
    return status;
}
