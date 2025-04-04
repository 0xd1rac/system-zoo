import struct
from typing import List, Dict, Tuple
from .instruction import (
    COND_AL, COND_EQ, COND_NE, COND_CS, COND_CC, COND_MI, COND_PL,
    COND_VS, COND_VC, COND_HI, COND_LS, COND_GE, COND_LT, COND_GT, COND_LE,
    SHIFT_LSL, SHIFT_LSR, SHIFT_ASR, SHIFT_ROR
)

class Disassembler:
    """Disassembler for ARM machine code"""
    
    def __init__(self):
        # Maps condition codes to their string representations
        self.cond_map = {
            COND_AL: "",      # Always (default)
            COND_EQ: "EQ",    # Equal
            COND_NE: "NE",    # Not equal
            COND_CS: "CS",    # Carry set
            COND_CC: "CC",    # Carry clear
            COND_MI: "MI",    # Minus/negative
            COND_PL: "PL",    # Plus/positive
            COND_VS: "VS",    # Overflow set
            COND_VC: "VC",    # Overflow clear
            COND_HI: "HI",    # Higher
            COND_LS: "LS",    # Lower or same
            COND_GE: "GE",    # Greater or equal
            COND_LT: "LT",    # Less than
            COND_GT: "GT",    # Greater than
            COND_LE: "LE"     # Less or equal
        }
        
        # Maps shift types to their string representations
        self.shift_map = {
            SHIFT_LSL: "LSL",  # Logical shift left
            SHIFT_LSR: "LSR",  # Logical shift right
            SHIFT_ASR: "ASR",  # Arithmetic shift right
            SHIFT_ROR: "ROR"   # Rotate right
        }
    
    def disassemble_file(self, input_file: str) -> List[str]:
        """
        Disassemble a binary file into ARM assembly code
        
        Args:
            input_file: Path to the input binary file
            
        Returns:
            A list of assembly instructions
        """
        instructions = []
        
        with open(input_file, 'rb') as f:
            while True:
                # Read 4 bytes (one instruction)
                data = f.read(4)
                if not data or len(data) < 4:
                    break
                
                # Convert bytes to integer (little endian)
                instruction = struct.unpack("<I", data)[0]
                
                # Disassemble the instruction
                asm = self.disassemble_instruction(instruction)
                instructions.append(asm)
        
        return instructions
    
    def disassemble_instruction(self, instruction: int) -> str:
        """
        Disassemble a single instruction
        
        Args:
            instruction: 32-bit instruction word
            
        Returns:
            Assembly language representation of the instruction
        """
        # Extract condition code (bits 31-28)
        cond = (instruction >> 28) & 0xF
        cond_str = self.cond_map.get(cond, "")
        
        # Extract instruction type bits
        op1 = (instruction >> 25) & 0x7  # bits 27-25
        op2 = (instruction >> 21) & 0xF  # bits 24-21
        s_bit = (instruction >> 20) & 0x1  # bit 20
        rn = (instruction >> 16) & 0xF  # bits 19-16
        rd = (instruction >> 12) & 0xF  # bits 15-12
        
        # Data processing instructions
        if op1 == 0b000:
            # Check for MOV instruction
            if op2 == 0b1101:
                imm = instruction & 0xFF
                return f"MOV{cond_str} R{rd}, #{imm}"
            
            # Check for ADD instruction
            elif op2 == 0b0100:
                if instruction & (1 << 25):  # Register with shift
                    rm = instruction & 0xF
                    shift_type = (instruction >> 5) & 0x3
                    shift_amount = (instruction >> 7) & 0x1F
                    shift_str = self.shift_map.get(shift_type, "??")
                    return f"ADD{cond_str} R{rd}, R{rn}, R{rm}, {shift_str} #{shift_amount}"
                else:  # Immediate
                    imm = instruction & 0xFF
                    return f"ADD{cond_str} R{rd}, R{rn}, #{imm}"
            
            # Check for SUB instruction
            elif op2 == 0b0010:
                if instruction & (1 << 25):  # Register with shift
                    rm = instruction & 0xF
                    shift_type = (instruction >> 5) & 0x3
                    shift_amount = (instruction >> 7) & 0x1F
                    shift_str = self.shift_map.get(shift_type, "??")
                    return f"SUB{cond_str} R{rd}, R{rn}, R{rm}, {shift_str} #{shift_amount}"
                else:  # Immediate
                    imm = instruction & 0xFF
                    return f"SUB{cond_str} R{rd}, R{rn}, #{imm}"
        
        # Load/Store instructions
        elif op1 == 0b010:
            offset = instruction & 0xFFF
            if op2 & 0b0001:  # LDR
                return f"LDR{cond_str} R{rd}, [R{rn}, #{offset}]"
            else:  # STR
                return f"STR{cond_str} R{rd}, [R{rn}, #{offset}]"
        
        # Branch instructions
        elif op1 == 0b101:
            offset = instruction & 0xFFFFFF
            # Convert from 2's complement if necessary
            if offset & 0x800000:
                offset = -(0x1000000 - offset)
            # Adjust for PC relative addressing
            offset = (offset << 2) + 8
            
            if instruction & (1 << 24):  # BL
                return f"BL{cond_str} {offset:08x}"
            else:  # B
                return f"B{cond_str} {offset:08x}"
        
        # Unknown instruction
        return f"; Unknown instruction: {instruction:08x}" 