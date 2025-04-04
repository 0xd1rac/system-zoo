# ARM Assembler

An assembler is a program that converts assembly language code into machine code (binary instructions) that a CPU can execute. 

## Overview

This ARM assembler converts ARM assembly code into machine code that can be executed by an ARM processor, and can also disassemble machine code back into assembly language. It supports a comprehensive subset of the ARM instruction set, including:

### Basic Instructions
- MOV: Move a value into a register
- ADD: Add two values and store in a register
- SUB: Subtract a value from a register
- LDR: Load a value from memory into a register
- STR: Store a value from a register into memory

### Branch Instructions
- B: Branch to a label
- BL: Branch with link (subroutine call)
- Supports forward and backward branches
- Automatically calculates branch offsets

### Condition Codes
All instructions can be conditionally executed using these suffixes:
- EQ: Equal
- NE: Not equal
- CS/HS: Carry set/Higher or same
- CC/LO: Carry clear/Lower
- MI: Minus/negative
- PL: Plus/positive
- VS: Overflow set
- VC: Overflow clear
- HI: Higher
- LS: Lower or same
- GE: Greater or equal
- LT: Less than
- GT: Greater than
- LE: Less or equal

### Shift Operations
Supports the following shift types:
- LSL: Logical shift left
- LSR: Logical shift right
- ASR: Arithmetic shift right
- ROR: Rotate right
- RRX: Rotate right with extend

### Register-Shifted Operations
Supports instructions with shifted register operands:
- ADD Rd, Rn, Rm, shift #amount
- SUB Rd, Rn, Rm, shift #amount
Where shift can be LSL, LSR, ASR, or ROR

## Usage

### Command Line

```bash
# Assemble an assembly file
python -m cpu.assembler input.s -o output.bin

# Disassemble a binary file
python -m cpu.assembler -d input.bin -o output.s
```

### Python API

```python
from cpu.assembler import Assembler, Disassembler

# Assembling code
assembler = Assembler()

# Assemble a string of assembly code
assembly_code = """
loop:
    MOV R0, #10
    ADDEQ R1, R0, #5  ; Only execute if equal
    BNE loop          ; Branch if not equal
"""
machine_code = assembler.assemble_string(assembly_code)

# Assemble a file
assembler.assemble_file("input.s", "output.bin")

# Disassembling code
disassembler = Disassembler()

# Disassemble a binary file
assembly_instructions = disassembler.disassemble_file("input.bin")
for instruction in assembly_instructions:
    print(instruction)
```

## Example

Input assembly code (`example_advanced.s`):
```armasm
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
```

The assembler converts this to binary machine code that can be executed by an ARM processor. The disassembler can then convert the binary machine code back into assembly code.

## Implementation Details

The assembler consists of the following components:

1. **Instruction Classes**: Define the encoding for each ARM instruction type
   - Base class with condition code support
   - Specialized classes for each instruction type
   - Support for shifted register operands

2. **Parser**: Parses assembly code and creates instruction objects
   - Handles labels and branch resolution
   - Supports condition codes and shift operations
   - Two-pass assembly for resolving branch targets

3. **Assembler**: Converts instruction objects into machine code
   - Manages the assembly process
   - Handles file I/O
   - Provides both file and string-based interfaces

4. **Disassembler**: Converts machine code back into assembly code
   - Decodes 32-bit instruction words
   - Extracts condition codes, operands, and shift operations
   - Reconstructs assembly language representation
   - Supports all instruction types handled by the assembler

## Limitations

- Limited support for immediate values (8 bits for most instructions)
- No support for floating-point operations
- No support for coprocessor instructions
- No support for system/privileged instructions
- Branch disassembly shows absolute addresses instead of labels

## Future Improvements

- Add support for floating-point operations
- Add support for coprocessor instructions
- Add support for system/privileged instructions
- Enhance disassembly to reconstruct labels
- Add support for more complex addressing modes
- Add support for assembler directives

## Assembly/Disassembly Process

### Assembly:
Input: Code in assembly language (for ARM: MOV R0, #1)
Assembler: Translates each line of assembly into its binary representation
Output: A binary file (e.g., .bin or .obj) containing machine instructions

Example:
```
MOV R0, #1   ; Move 1 into register R0
ADD R1, R0, #2  ; Add 2 to R0, store in R1
```

The assembler converts this to something like:
```
1110 0011 A0000000
1110 0010 B0000001
```

### Disassembly:
Input: Binary machine code
Disassembler: Decodes each 32-bit instruction word
Output: Assembly language representation

Example:
```
1110 0011 A0000000  ->  MOV R0, #1
1110 0010 B0000001  ->  ADD R1, R0, #2
```

