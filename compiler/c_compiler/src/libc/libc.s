.section .data
heap_start: .word 0
heap_end: .word 0
heap_initialized: .word 0
rand_seed: .word 1

.section .text
.global malloc
.global free
.global memcpy
.global memset
.global strlen
.global strcmp
.global strcpy
.global printf
.global scanf
.global getchar
.global putchar
.global abs
.global rand
.global srand

# Memory allocation functions

# void* malloc(unsigned int size)
malloc:
    push {r4, r5, r6, lr}
    
    # Check if heap is initialized
    ldr r4, =heap_initialized
    ldr r5, [r4]
    cmp r5, #0
    bne malloc_heap_initialized
    
    # Initialize heap
    # Set heap_start to 0x40000 (256KB)
    ldr r5, =heap_start
    mov r6, #0x40000
    str r6, [r5]
    
    # Set heap_end to heap_start
    ldr r5, =heap_end
    str r6, [r5]
    
    # Mark heap as initialized
    ldr r5, =heap_initialized
    mov r6, #1
    str r6, [r5]
    
malloc_heap_initialized:
    # Align size to 4 bytes
    add r0, r0, #3
    bic r0, r0, #3
    
    # Get current heap_end
    ldr r4, =heap_end
    ldr r5, [r4]
    
    # Calculate new heap_end
    add r6, r5, r0
    
    # Update heap_end
    str r6, [r4]
    
    # Return allocated memory address
    mov r0, r5
    
    pop {r4, r5, r6, lr}
    bx lr

# void free(void* ptr)
free:
    # Simple implementation - no actual freeing
    # In a real implementation, we would track allocated blocks
    # and merge freed blocks
    bx lr

# String operations

# void* memcpy(void* dest, const void* src, unsigned int n)
memcpy:
    push {r4, r5, r6, lr}
    
    # Save dest for return value
    mov r4, r0
    
    # Check if n is 0
    cmp r2, #0
    beq memcpy_done
    
    # Copy byte by byte
memcpy_loop:
    ldrb r5, [r1], #1
    strb r5, [r0], #1
    subs r2, r2, #1
    bne memcpy_loop
    
memcpy_done:
    # Return dest
    mov r0, r4
    
    pop {r4, r5, r6, lr}
    bx lr

# void* memset(void* s, int c, unsigned int n)
memset:
    push {r4, r5, lr}
    
    # Save s for return value
    mov r4, r0
    
    # Check if n is 0
    cmp r2, #0
    beq memset_done
    
    # Set byte by byte
memset_loop:
    strb r1, [r0], #1
    subs r2, r2, #1
    bne memset_loop
    
memset_done:
    # Return s
    mov r0, r4
    
    pop {r4, r5, lr}
    bx lr

# int strlen(const char* s)
strlen:
    push {r4, lr}
    
    # Initialize length to 0
    mov r4, #0
    
strlen_loop:
    # Load byte and check if null
    ldrb r1, [r0, r4]
    cmp r1, #0
    beq strlen_done
    
    # Increment length
    add r4, r4, #1
    b strlen_loop
    
strlen_done:
    # Return length
    mov r0, r4
    
    pop {r4, lr}
    bx lr

# int strcmp(const char* s1, const char* s2)
strcmp:
    push {r4, r5, lr}
    
strcmp_loop:
    # Load bytes from both strings
    ldrb r4, [r0], #1
    ldrb r5, [r1], #1
    
    # Compare bytes
    cmp r4, r5
    bne strcmp_diff
    
    # Check if end of string
    cmp r4, #0
    beq strcmp_equal
    
    b strcmp_loop
    
strcmp_diff:
    # Return difference
    sub r0, r4, r5
    b strcmp_done
    
strcmp_equal:
    # Return 0 (equal)
    mov r0, #0
    
strcmp_done:
    pop {r4, r5, lr}
    bx lr

# char* strcpy(char* dest, const char* src)
strcpy:
    push {r4, lr}
    
    # Save dest for return value
    mov r4, r0
    
strcpy_loop:
    # Load byte from src
    ldrb r2, [r1], #1
    strb r2, [r0], #1
    
    # Check if end of string
    cmp r2, #0
    bne strcpy_loop
    
    # Return dest
    mov r0, r4
    
    pop {r4, lr}
    bx lr

# I/O operations

# int printf(const char* format, ...)
printf:
    # This is handled by the compiler's code generator
    # which converts printf calls to semihosting write calls
    bx lr

# int scanf(const char* format, ...)
scanf:
    # Not implemented - would require semihosting read
    mov r0, #0
    bx lr

# int getchar(void)
getchar:
    # Not implemented - would require semihosting read
    mov r0, #-1
    bx lr

# int putchar(int c)
putchar:
    push {r4, lr}
    
    # Convert character to string
    sub sp, sp, #2
    strb r0, [sp, #0]
    mov r1, #0
    strb r1, [sp, #1]
    
    # Call semihosting write
    mov r0, #1  # stdout
    mov r1, sp  # string address
    mov r2, #1  # string length
    mov r7, #4  # SYS_WRITE
    svc 0
    
    # Restore stack
    add sp, sp, #2
    
    pop {r4, lr}
    bx lr

# Standard library functions

# int abs(int x)
abs:
    cmp r0, #0
    rsblt r0, r0, #0
    bx lr

# int rand(void)
rand:
    push {r4, lr}
    
    # Simple linear congruential generator
    ldr r4, =rand_seed
    ldr r0, [r4]
    mov r1, #1103515245
    mul r0, r0, r1
    add r0, r0, #12345
    and r0, r0, #0x7fffffff
    str r0, [r4]
    
    pop {r4, lr}
    bx lr

# void srand(unsigned int seed)
srand:
    ldr r1, =rand_seed
    str r0, [r1]
    bx lr 