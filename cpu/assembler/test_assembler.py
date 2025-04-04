#!/usr/bin/env python3
"""
Test script for the ARM assembler
"""

from assembler import Assembler

def main():
    # Create an assembler instance
    assembler = Assembler()
    
    # Example 1: Assemble a string of assembly code
    assembly_code = """
    MOV R0, #10
    ADD R1, R0, #5
    SUB R2, R1, #3
    """
    
    try:
        # Assemble the code
        machine_code = assembler.assemble_string(assembly_code)
        
        # Print the machine code as hex bytes
        print("Machine code (hex):")
        for i, byte in enumerate(machine_code):
            print(f"{byte:02x}", end=' ')
            if (i + 1) % 4 == 0:
                print()  # New line after each instruction (4 bytes)
        print()
        
        # Example 2: Assemble a file
        print("Assembling example.s...")
        assembler.assemble_file("example.s", "example.bin")
        print("Assembly complete. Output written to example.bin")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 