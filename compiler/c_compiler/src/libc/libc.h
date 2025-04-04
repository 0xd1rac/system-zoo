#ifndef LIBC_H
#define LIBC_H

// Memory allocation
void* malloc(unsigned int size);
void free(void* ptr);

// String operations
void* memcpy(void* dest, const void* src, unsigned int n);
void* memset(void* s, int c, unsigned int n);
int strlen(const char* s);
int strcmp(const char* s1, const char* s2);
char* strcpy(char* dest, const char* src);

// I/O operations
int printf(const char* format, ...);
int scanf(const char* format, ...);
int getchar(void);
int putchar(int c);

// Standard library functions
int abs(int x);
int rand(void);
void srand(unsigned int seed);

#endif // LIBC_H 