import os
from typing import List, BinaryIO
from .instruction import Instruction
from .parser import Parser

class Assembler:
    """ARM assembler that converts assembly code to machine code"""
    
    def __init__(self):
        self.parser = Parser()
    
    def assemble_file(self, input_file: str, output_file: str) -> None:
        """
        Assemble an ARM assembly file into machine code
        
        Args:
            input_file: Path to the input assembly file
            output_file: Path to the output binary file
        """
        # Parse the assembly file
        instructions = self.parser.parse_file(input_file)
        
        # Write the machine code to the output file
        with open(output_file, 'wb') as f:
            for instruction in instructions:
                f.write(instruction.encode())
    
    def assemble_string(self, assembly_code: str) -> bytes:
        """
        Assemble a string of ARM assembly code into machine code
        
        Args:
            assembly_code: A string containing ARM assembly code
            
        Returns:
            The machine code as a bytes object
        """
        # Split the code into lines
        lines = assembly_code.split('\n')
        
        # Parse each line
        instructions = []
        for line_num, line in enumerate(lines, 1):
            try:
                instruction = self.parser.parse_line(line)
                if instruction:
                    instructions.append(instruction)
            except ValueError as e:
                raise ValueError(f"Error on line {line_num}: {str(e)}")
        
        # Encode each instruction
        machine_code = b''
        for instruction in instructions:
            machine_code += instruction.encode()
        
        return machine_code
    
    def disassemble_file(self, input_file: str) -> List[str]:
        """
        Disassemble a binary file into ARM assembly code
        
        Args:
            input_file: Path to the input binary file
            
        Returns:
            A list of assembly instructions
        """
        # This is a placeholder for a future implementation
        # Disassembly is more complex and requires a more sophisticated approach
        raise NotImplementedError("Disassembly is not yet implemented") 