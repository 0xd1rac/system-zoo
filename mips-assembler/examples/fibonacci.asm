# Fibonacci sequence calculator
# Calculates fib(n) where n is stored in $a0
# Result is stored in $v0

main:
    addi $a0, $zero, 10    # Calculate fib(10)
    jal fib                # Call fib function
    j end                 # End program

fib:
    # Base cases
    beq $a0, $zero, fib0  # if n == 0, return 0
    addi $t0, $zero, 1
    beq $a0, $t0, fib1    # if n == 1, return 1

    # Save return address and n
    addi $sp, $sp, -8     # Allocate stack space
    sw $ra, 4($sp)        # Save return address
    sw $a0, 0($sp)        # Save n

    # Calculate fib(n-1)
    addi $a0, $a0, -1     # n = n - 1
    jal fib               # Call fib(n-1)
    add $t0, $v0, $zero   # Save result in $t0

    # Calculate fib(n-2)
    lw $a0, 0($sp)        # Restore n
    addi $a0, $a0, -2     # n = n - 2
    jal fib               # Call fib(n-2)

    # Add results and return
    add $v0, $t0, $v0     # fib(n) = fib(n-1) + fib(n-2)
    lw $ra, 4($sp)        # Restore return address
    addi $sp, $sp, 8      # Deallocate stack space
    jr $ra                # Return

fib0:
    add $v0, $zero, $zero # Return 0
    jr $ra

fib1:
    addi $v0, $zero, 1    # Return 1
    jr $ra

end:
    nop                   # End of program 