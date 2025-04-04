; Example ARM assembly program demonstrating advanced features
; This program calculates the factorial of a number using a loop

; Initialize registers
MOV R0, #5        ; Input number (calculating 5!)
MOV R1, #1        ; Result accumulator
MOV R2, #1        ; Counter

; Main loop
loop:
    CMP R2, R0            ; Compare counter with input
    BGT end              ; If counter > input, branch to end
    
    ; Multiply result by counter (using shifts and adds)
    MOV R3, #0           ; Clear temporary register
    MOV R4, R1           ; Copy current result
    MOV R5, R2           ; Copy counter for multiplication
    
multiply:
    CMP R5, #0           ; Check if multiplier is zero
    BEQ multiply_done    ; If zero, multiplication is done
    
    TST R5, #1           ; Test least significant bit
    BEQ shift            ; If bit is 0, just shift
    
    ADD R3, R3, R4       ; Add current value to result
    
shift:
    LSL R4, R4, #1       ; Shift left multiplicand
    LSR R5, R5, #1       ; Shift right multiplier
    B multiply           ; Continue multiplication loop
    
multiply_done:
    MOV R1, R3           ; Store multiplication result
    ADD R2, R2, #1       ; Increment counter
    B loop               ; Continue main loop

end:
    ; Result is in R1
    ; Store result in memory
    MOV R6, #0x1000      ; Memory address
    STR R1, [R6, #0]     ; Store result

; Example of conditional execution and register shifts
    MOVEQ R7, R1, LSL #1  ; Double result if last comparison was equal
    ADDNE R7, R1, R1      ; Add result to itself if last comparison was not equal
    SUBGT R7, R7, #1      ; Subtract 1 if last comparison was greater than

; Example of register-shifted operations
    ADD R8, R1, R2, LSL #2  ; R8 = R1 + (R2 << 2)
    SUB R9, R8, R3, LSR #1  ; R9 = R8 - (R3 >> 1)
    ADD R10, R9, R4, ASR #2 ; R10 = R9 + (R4 >> 2) with sign extension
    SUB R11, R10, R5, ROR #3 ; R11 = R10 - (R5 rotated right by 3) 