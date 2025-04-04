; Example ARM assembly program
; This program adds two numbers and stores the result in memory

; Initialize registers
MOV R0, #5    ; R0 = 5
MOV R1, #3    ; R1 = 3

; Add the numbers
ADD R2, R0, R1  ; R2 = R0 + R1

; Store the result in memory
; Assuming we have a memory location at address 0x1000
MOV R3, #0x1000  ; R3 = address 0x1000
STR R2, [R3, #0]  ; Store R2 at address in R3

; Load the result back into R4
LDR R4, [R3, #0]  ; R4 = value at address in R3

; Subtract 1 from the result
SUB R5, R4, #1  ; R5 = R4 - 1 