import struct 
import sys 

# Condition codes for ARM instructions
COND_AL = 0xE  # Always (default)
COND_EQ = 0x0  # Equal
COND_NE = 0x1  # Not equal
COND_CS = 0x2  # Carry set
COND_CC = 0x3  # Carry clear
COND_MI = 0x4  # Minus/negative
COND_PL = 0x5  # Plus/positive
COND_VS = 0x6  # Overflow set
COND_VC = 0x7  # Overflow clear
COND_HI = 0x8  # Higher
COND_LS = 0x9  # Lower or same
COND_GE = 0xA  # Greater or equal
COND_LT = 0xB  # Less than
COND_GT = 0xC  # Greater than
COND_LE = 0xD  # Less or equal

# Shift types
SHIFT_LSL = 0x0  # Logical shift left
SHIFT_LSR = 0x1  # Logical shift right
SHIFT_ASR = 0x2  # Arithmetic shift right
SHIFT_ROR = 0x3  # Rotate right
SHIFT_RRX = 0x3  # Rotate right with extend (special case)

class Instruction:
    """Abstract base class for all instructions"""
    def __init__(self, cond=COND_AL):
        self.cond = cond
    
    def encode(self): 
        """Encodes the instruction into 4 bytes (little endian)"""
        raise NotImplementedError("Subclasses must implement encode()")
    
    def __str__(self) -> str:
        """Returns a string representation of the instruction"""
        raise NotImplementedError("Subclasses must implement __str__()")
    
    def _get_cond_suffix(self) -> str:
        """Returns the condition code suffix for the instruction"""
        if self.cond == COND_AL:
            return ""
        
        cond_suffixes = {
            COND_EQ: "EQ", COND_NE: "NE", COND_CS: "CS", COND_CC: "CC",
            COND_MI: "MI", COND_PL: "PL", COND_VS: "VS", COND_VC: "VC",
            COND_HI: "HI", COND_LS: "LS", COND_GE: "GE", COND_LT: "LT",
            COND_GT: "GT", COND_LE: "LE"
        }
        
        return cond_suffixes.get(self.cond, "")
    
    
class MovInstruction(Instruction):
    """
    MOV instruction: Move a value into a register
    Example: MOV Rn, #imm (Rn = register, imm = immediate value)
    """
    def __init__(self, rd: int, imm: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.rd = rd
        self.imm = imm
        
    def encode(self):
        # ARM MOV instruction encoding
        # 31-28: Condition code
        # 27-25: 000
        # 24-21: 1101 (MOV opcode)
        # 20: 0 (not S bit)
        # 19-16: 0000 (not used)
        # 15-12: Rd (destination register)
        # 11-8: 0000 (not used)
        # 7-0: Immediate value (8 bits)
        
        # Check if immediate value fits in 8 bits
        if self.imm > 0xFF:
            raise ValueError(f"Immediate value {self.imm} is too large for MOV instruction (max 8 bits)")
        
        # Construct the instruction
        instruction = 0x3A00000  # Base encoding for MOV (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        instruction |= self.imm & 0xFF  # Set immediate value
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"MOV{self._get_cond_suffix()} R{self.rd}, #{self.imm}"


class AddInstruction(Instruction):
    """
    ADD instruction: Add two values and store in a register
    Example: ADD Rn, Rm, #imm (Rn = destination, Rm = source, imm = immediate value)
    """
    def __init__(self, rd: int, rn: int, imm: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.rd = rd
        self.rn = rn
        self.imm = imm
        
    def encode(self):
        # ARM ADD instruction encoding
        # 31-28: Condition code
        # 27-25: 000
        # 24-21: 0100 (ADD opcode)
        # 20: 0 (not S bit)
        # 19-16: Rn (first operand register)
        # 15-12: Rd (destination register)
        # 11-8: 0000 (not used)
        # 7-0: Immediate value (8 bits)
        
        # Check if immediate value fits in 8 bits
        if self.imm > 0xFF:
            raise ValueError(f"Immediate value {self.imm} is too large for ADD instruction (max 8 bits)")
        
        # Construct the instruction
        instruction = 0x2800000  # Base encoding for ADD (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rn & 0xF) << 16  # Set Rn
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        instruction |= self.imm & 0xFF  # Set immediate value
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"ADD{self._get_cond_suffix()} R{self.rd}, R{self.rn}, #{self.imm}"


class SubInstruction(Instruction):
    """
    SUB instruction: Subtract a value from a register
    Example: SUB Rn, Rm, #imm (Rn = destination, Rm = source, imm = immediate value)
    """
    def __init__(self, rd: int, rn: int, imm: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.rd = rd
        self.rn = rn
        self.imm = imm
        
    def encode(self):
        # ARM SUB instruction encoding
        # 31-28: Condition code
        # 27-25: 000
        # 24-21: 0010 (SUB opcode)
        # 20: 0 (not S bit)
        # 19-16: Rn (first operand register)
        # 15-12: Rd (destination register)
        # 11-8: 0000 (not used)
        # 7-0: Immediate value (8 bits)
        
        # Check if immediate value fits in 8 bits
        if self.imm > 0xFF:
            raise ValueError(f"Immediate value {self.imm} is too large for SUB instruction (max 8 bits)")
        
        # Construct the instruction
        instruction = 0x2400000  # Base encoding for SUB (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rn & 0xF) << 16  # Set Rn
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        instruction |= self.imm & 0xFF  # Set immediate value
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"SUB{self._get_cond_suffix()} R{self.rd}, R{self.rn}, #{self.imm}"


class LdrInstruction(Instruction):
    """
    LDR instruction: Load a value from memory into a register
    Example: LDR Rn, [Rm, #offset] (Rn = destination, Rm = base register, offset = immediate value)
    """
    def __init__(self, rd: int, rn: int, offset: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.rd = rd
        self.rn = rn
        self.offset = offset
        
    def encode(self):
        # ARM LDR instruction encoding
        # 31-28: Condition code
        # 27-25: 010
        # 24-21: 1101 (LDR opcode)
        # 20: 1 (U bit, 1 for positive offset)
        # 19-16: Rn (base register)
        # 15-12: Rd (destination register)
        # 11-0: Immediate value (12 bits)
        
        # Check if offset fits in 12 bits
        if self.offset > 0xFFF:
            raise ValueError(f"Offset {self.offset} is too large for LDR instruction (max 12 bits)")
        
        # Construct the instruction
        instruction = 0x4100000  # Base encoding for LDR (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rn & 0xF) << 16  # Set Rn
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        instruction |= self.offset & 0xFFF  # Set offset
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"LDR{self._get_cond_suffix()} R{self.rd}, [R{self.rn}, #{self.offset}]"


class StrInstruction(Instruction):
    """
    STR instruction: Store a value from a register into memory
    Example: STR Rn, [Rm, #offset] (Rn = source, Rm = base register, offset = immediate value)
    """
    def __init__(self, rd: int, rn: int, offset: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.rd = rd
        self.rn = rn
        self.offset = offset
        
    def encode(self):
        # ARM STR instruction encoding
        # 31-28: Condition code
        # 27-25: 010
        # 24-21: 1100 (STR opcode)
        # 20: 1 (U bit, 1 for positive offset)
        # 19-16: Rn (base register)
        # 15-12: Rd (source register)
        # 11-0: Immediate value (12 bits)
        
        # Check if offset fits in 12 bits
        if self.offset > 0xFFF:
            raise ValueError(f"Offset {self.offset} is too large for STR instruction (max 12 bits)")
        
        # Construct the instruction
        instruction = 0x4000000  # Base encoding for STR (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rn & 0xF) << 16  # Set Rn
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        instruction |= self.offset & 0xFFF  # Set offset
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"STR{self._get_cond_suffix()} R{self.rd}, [R{self.rn}, #{self.offset}]"


class BranchInstruction(Instruction):
    """
    B instruction: Branch to a label
    Example: B label (label = target address)
    """
    def __init__(self, target: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.target = target
        
    def encode(self):
        # ARM B instruction encoding
        # 31-28: Condition code
        # 27-25: 101
        # 24: 0 (not L bit)
        # 23-0: Signed 24-bit offset (shifted left by 2)
        
        # Construct the instruction
        instruction = 0xA000000  # Base encoding for B (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        
        # The target is a 24-bit signed offset, shifted left by 2
        # We need to convert the target to a relative offset
        offset = self.target & 0xFFFFFF
        instruction |= offset & 0xFFFFFF
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"B{self._get_cond_suffix()} {self.target}"


class BranchLinkInstruction(Instruction):
    """
    BL instruction: Branch with link (subroutine call)
    Example: BL label (label = target address)
    """
    def __init__(self, target: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.target = target
        
    def encode(self):
        # ARM BL instruction encoding
        # 31-28: Condition code
        # 27-25: 101
        # 24: 1 (L bit)
        # 23-0: Signed 24-bit offset (shifted left by 2)
        
        # Construct the instruction
        instruction = 0xB000000  # Base encoding for BL (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        
        # The target is a 24-bit signed offset, shifted left by 2
        # We need to convert the target to a relative offset
        offset = self.target & 0xFFFFFF
        instruction |= offset & 0xFFFFFF
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        return f"BL{self._get_cond_suffix()} {self.target}"


class ShiftedRegisterInstruction(Instruction):
    """
    Base class for instructions that use shifted register operands
    """
    def __init__(self, rd: int, rn: int, rm: int, shift_type: int, shift_amount: int, cond=COND_AL) -> None:
        super().__init__(cond)
        self.rd = rd
        self.rn = rn
        self.rm = rm
        self.shift_type = shift_type
        self.shift_amount = shift_amount
        
    def _encode_shifted_operand(self) -> int:
        """
        Encode the shifted register operand
        Returns the encoded operand as an integer
        """
        # Check if shift amount fits in 5 bits
        if self.shift_amount > 0x1F:
            raise ValueError(f"Shift amount {self.shift_amount} is too large (max 5 bits)")
        
        # Encode the shifted register operand
        operand = 0x0  # Register operand (not immediate)
        operand |= (self.rm & 0xF)  # Set Rm
        operand |= (self.shift_type & 0x3) << 5  # Set shift type
        operand |= (self.shift_amount & 0x1F) << 7  # Set shift amount
        
        return operand


class AddRegInstruction(ShiftedRegisterInstruction):
    """
    ADD instruction with register operand: Add two registers and store in a register
    Example: ADD Rn, Rm, Rk, LSL #2 (Rn = destination, Rm = first operand, Rk = second operand, LSL = shift type, 2 = shift amount)
    """
    def encode(self):
        # ARM ADD instruction encoding with register operand
        # 31-28: Condition code
        # 27-25: 000
        # 24-21: 0100 (ADD opcode)
        # 20: 0 (not S bit)
        # 19-16: Rn (first operand register)
        # 15-12: Rd (destination register)
        # 11-4: 00000000 (not used)
        # 3-0: Rm (second operand register)
        
        # Construct the instruction
        instruction = 0x2800000  # Base encoding for ADD (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rn & 0xF) << 16  # Set Rn
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        
        # Add the shifted register operand
        operand = self._encode_shifted_operand()
        instruction |= operand
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        shift_names = {SHIFT_LSL: "LSL", SHIFT_LSR: "LSR", SHIFT_ASR: "ASR", SHIFT_ROR: "ROR"}
        shift_name = shift_names.get(self.shift_type, "??")
        return f"ADD{self._get_cond_suffix()} R{self.rd}, R{self.rn}, R{self.rm}, {shift_name} #{self.shift_amount}"


class SubRegInstruction(ShiftedRegisterInstruction):
    """
    SUB instruction with register operand: Subtract a register from another register
    Example: SUB Rn, Rm, Rk, LSL #2 (Rn = destination, Rm = first operand, Rk = second operand, LSL = shift type, 2 = shift amount)
    """
    def encode(self):
        # ARM SUB instruction encoding with register operand
        # 31-28: Condition code
        # 27-25: 000
        # 24-21: 0010 (SUB opcode)
        # 20: 0 (not S bit)
        # 19-16: Rn (first operand register)
        # 15-12: Rd (destination register)
        # 11-4: 00000000 (not used)
        # 3-0: Rm (second operand register)
        
        # Construct the instruction
        instruction = 0x2400000  # Base encoding for SUB (without condition code)
        instruction |= (self.cond & 0xF) << 28  # Set condition code
        instruction |= (self.rn & 0xF) << 16  # Set Rn
        instruction |= (self.rd & 0xF) << 12  # Set Rd
        
        # Add the shifted register operand
        operand = self._encode_shifted_operand()
        instruction |= operand
        
        return struct.pack("<I", instruction)  # Pack as little-endian 32-bit integer
    
    def __str__(self) -> str:
        shift_names = {SHIFT_LSL: "LSL", SHIFT_LSR: "LSR", SHIFT_ASR: "ASR", SHIFT_ROR: "ROR"}
        shift_name = shift_names.get(self.shift_type, "??")
        return f"SUB{self._get_cond_suffix()} R{self.rd}, R{self.rn}, R{self.rm}, {shift_name} #{self.shift_amount}"

