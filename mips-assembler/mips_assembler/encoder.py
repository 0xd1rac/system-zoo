from typing import List, Dict
from .parser import Instruction, RTypeInstruction, ITypeInstruction, JTypeInstruction

class EncoderError(Exception):
    """Custom exception for encoder errors"""
    def __init__(self, message: str, instruction: Instruction):
        self.message = message
        self.instruction = instruction
        super().__init__(f"{message} for instruction at line {instruction.line}")

class MIPSEncoder:
    """Encoder for MIPS instructions"""
    


    ASSEMBLY_NAME_2_NUMBER: Dict[str, int] = {
        '$zero': 0, 
        '$at': 1,
        '$v0': 2, '$v1': 3,
        '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
        '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
        '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
        '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
        '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
        '$t8': 24, '$t9': 25,
        '$k0': 26, '$k1': 27,
        '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31
    }
    
    REGISTER_2_NUMBER = {f'$r{i}': i for i in range(32)}

    REGISTERS: Dict[str, int] = ASSEMBLY_NAME_2_NUMBER | REGISTER_2_NUMBER

    
    # Opcode mapping for instructions
    OPCODES: Dict[str, int] = {
        # R-type instructions
        'add': 0x00, 'sub': 0x00, 'and': 0x00, 'or': 0x00,
        'slt': 0x00, 'sll': 0x00, 'srl': 0x00, 'nop': 0x00,
        
        # I-type instructions
        'addi': 0x08, 'lw': 0x23, 'sw': 0x2B,
        'beq': 0x04, 'bne': 0x05,
        
        # J-type instructions
        'j': 0x02, 'jal': 0x03
    }
    
    # Function codes for R-type instructions
    FUNCTS: Dict[str, int] = {
        'add': 0x20, 'sub': 0x22, 'and': 0x24, 'or': 0x25,
        'slt': 0x2A, 'sll': 0x00, 'srl': 0x02, 'nop': 0x00
    }

    def __init__(self):
        """Initialize the encoder"""
        pass

    def encode(self, instructions: List[Instruction]) -> List[int]:
        """
        Encode a list of instructions into their binary machine code representation
        
        Args:
            instructions: List of Instruction objects
            
        Returns:
            List of 32-bit machine code instructions
        """
        return [self._encode_instruction(instr) for instr in instructions]

    def _encode_instruction(self, instruction: Instruction) -> int:
        """
        Encode a single instruction into its binary machine code representation
        
        Args:
            instruction: The instruction to encode
            
        Returns:
            32-bit machine code instruction
        """
        if isinstance(instruction, RTypeInstruction):
            return self._encode_r_type(instruction)
        elif isinstance(instruction, ITypeInstruction):
            return self._encode_i_type(instruction)
        elif isinstance(instruction, JTypeInstruction):
            return self._encode_j_type(instruction)
        else:
            raise EncoderError("Unknown instruction type", instruction)

    def _encode_r_type(self, instruction: RTypeInstruction) -> int:
        """Encode an R-type instruction"""
        opcode = self.OPCODES[instruction.mnemonic]
        funct = self.FUNCTS[instruction.mnemonic]
        
        # Get register numbers
        rd = self._get_register_number(instruction.rd)
        rs = self._get_register_number(instruction.rs) if instruction.rs else 0
        rt = self._get_register_number(instruction.rt) if instruction.rt else 0
        
        # Handle special cases
        if instruction.mnemonic in ['sll', 'srl']:
            shamt = int(instruction.shamt)
            return (opcode << 26) | (0 << 21) | (rt << 16) | (rd << 11) | (shamt << 6) | funct
        elif instruction.mnemonic == 'nop':
            return 0  # nop is all zeros
        else:
            return (opcode << 26) | (rs << 21) | (rt << 16) | (rd << 11) | (0 << 6) | funct

    def _encode_i_type(self, instruction: ITypeInstruction) -> int:
        """Encode an I-type instruction"""
        opcode = self.OPCODES[instruction.mnemonic]
        rt = self._get_register_number(instruction.rt)
        rs = self._get_register_number(instruction.rs)
        
        # Handle different immediate formats
        if instruction.mnemonic in ['lw', 'sw']:
            # For load/store, immediate is the offset
            immediate = int(instruction.immediate)
        elif instruction.mnemonic in ['beq', 'bne']:
            # For branches, immediate is the offset in words
            immediate = int(instruction.immediate)
        else:
            # For addi, immediate is the value
            immediate = int(instruction.immediate)
            
        # Sign extend immediate to 16 bits
        immediate = immediate & 0xFFFF
        
        return (opcode << 26) | (rs << 21) | (rt << 16) | immediate

    def _encode_j_type(self, instruction: JTypeInstruction) -> int:
        """Encode a J-type instruction"""
        opcode = self.OPCODES[instruction.mnemonic]
        address = int(instruction.address)
        
        # For J-type, address is word-aligned, so we use the upper 26 bits
        # and shift right by 2 (since addresses are word-aligned)
        target = (address >> 2) & 0x3FFFFFF
        
        return (opcode << 26) | target

    def _get_register_number(self, reg: str) -> int:
        """Get the register number from a register name"""
        if reg not in self.REGISTERS:
            raise EncoderError(f"Invalid register: {reg}", None)
        return self.REGISTERS[reg]

# Example usage
if __name__ == '__main__':
    from parser import MIPSParser
    
    code = """
    loop:   add $t0, $t1, $t2   # This is a comment
            lw $s1, 0($sp)
            beq $t0, $zero, end
    end:    nop
    """
    
    # Parse the code
    parser = MIPSParser()
    instructions = parser.parse(code)
    
    # Encode the instructions
    encoder = MIPSEncoder()
    machine_code = encoder.encode(instructions)
    
    # Print the machine code in hex
    for i, code in enumerate(machine_code):
        print(f"Instruction {i}: 0x{code:08X}") 