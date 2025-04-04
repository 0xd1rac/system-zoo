import re
from typing import List, Tuple, Optional, Dict
from .instruction import (
    Instruction, MovInstruction, AddInstruction, SubInstruction,
    LdrInstruction, StrInstruction, BranchInstruction, BranchLinkInstruction,
    AddRegInstruction, SubRegInstruction,
    COND_AL, COND_EQ, COND_NE, COND_CS, COND_CC, COND_MI, COND_PL,
    COND_VS, COND_VC, COND_HI, COND_LS, COND_GE, COND_LT, COND_GT, COND_LE,
    SHIFT_LSL, SHIFT_LSR, SHIFT_ASR, SHIFT_ROR
)

class Parser:
    """Parser for ARM assembly code"""
    
    def __init__(self):
        # Regular expressions for parsing different instruction formats
        self.label_pattern = re.compile(r'^\s*(\w+):\s*$')
        
        # Condition code pattern (optional)
        self.cond_pattern = r'(?:(?:EQ|NE|CS|CC|MI|PL|VS|VC|HI|LS|GE|LT|GT|LE))?'
        
        # Shift pattern (optional)
        self.shift_pattern = r'(?:,\s*(?:LSL|LSR|ASR|ROR)\s+#\d+)?'
        
        # Instruction patterns with condition codes and shifts
        self.mov_pattern = re.compile(rf'^\s*MOV{self.cond_pattern}\s+R(\d+)\s*,\s*#(\d+)\s*$')
        self.add_pattern = re.compile(rf'^\s*ADD{self.cond_pattern}\s+R(\d+)\s*,\s*R(\d+)\s*,\s*#(\d+)\s*$')
        self.sub_pattern = re.compile(rf'^\s*SUB{self.cond_pattern}\s+R(\d+)\s*,\s*R(\d+)\s*,\s*#(\d+)\s*$')
        self.ldr_pattern = re.compile(rf'^\s*LDR{self.cond_pattern}\s+R(\d+)\s*,\s*\[R(\d+)\s*,\s*#(\d+)\]\s*$')
        self.str_pattern = re.compile(rf'^\s*STR{self.cond_pattern}\s+R(\d+)\s*,\s*\[R(\d+)\s*,\s*#(\d+)\]\s*$')
        self.b_pattern = re.compile(rf'^\s*B{self.cond_pattern}\s+(\w+)\s*$')
        self.bl_pattern = re.compile(rf'^\s*BL{self.cond_pattern}\s+(\w+)\s*$')
        
        # Register-shifted instruction patterns
        self.add_reg_pattern = re.compile(rf'^\s*ADD{self.cond_pattern}\s+R(\d+)\s*,\s*R(\d+)\s*,\s*R(\d+)\s*,\s*(LSL|LSR|ASR|ROR)\s+#(\d+)\s*$')
        self.sub_reg_pattern = re.compile(rf'^\s*SUB{self.cond_pattern}\s+R(\d+)\s*,\s*R(\d+)\s*,\s*R(\d+)\s*,\s*(LSL|LSR|ASR|ROR)\s+#(\d+)\s*$')
        
        # Label and address tracking
        self.labels: Dict[str, int] = {}  # Maps label names to addresses
        self.current_address = 0  # Current instruction address (in bytes)
        self.unresolved_branches: List[Tuple[int, str, Instruction]] = []  # (address, label, instruction)
    
    def _get_condition_code(self, instruction: str) -> int:
        """Extract condition code from instruction string"""
        cond_map = {
            'EQ': COND_EQ, 'NE': COND_NE, 'CS': COND_CS, 'CC': COND_CC,
            'MI': COND_MI, 'PL': COND_PL, 'VS': COND_VS, 'VC': COND_VC,
            'HI': COND_HI, 'LS': COND_LS, 'GE': COND_GE, 'LT': COND_LT,
            'GT': COND_GT, 'LE': COND_LE
        }
        
        for suffix, code in cond_map.items():
            if suffix in instruction:
                return code
        return COND_AL
    
    def _get_shift_type(self, shift_name: str) -> int:
        """Convert shift name to shift type constant"""
        shift_map = {
            'LSL': SHIFT_LSL,
            'LSR': SHIFT_LSR,
            'ASR': SHIFT_ASR,
            'ROR': SHIFT_ROR
        }
        return shift_map.get(shift_name, SHIFT_LSL)
    
    def parse_line(self, line: str) -> Optional[Instruction]:
        """
        Parse a single line of assembly code and return the corresponding instruction
        
        Args:
            line: A line of ARM assembly code
            
        Returns:
            An Instruction object or None if the line is empty or a comment
        """
        # Remove comments
        line = line.split(';')[0].strip()
        
        # Skip empty lines
        if not line:
            return None
        
        # Check for label
        label_match = self.label_pattern.match(line)
        if label_match:
            label = label_match.group(1)
            self.labels[label] = self.current_address
            return None
        
        # Get condition code
        cond = self._get_condition_code(line)
        
        # Try to match each instruction pattern
        mov_match = self.mov_pattern.match(line)
        if mov_match:
            rd = int(mov_match.group(1))
            imm = int(mov_match.group(2))
            return MovInstruction(rd, imm, cond)
        
        add_match = self.add_pattern.match(line)
        if add_match:
            rd = int(add_match.group(1))
            rn = int(add_match.group(2))
            imm = int(add_match.group(3))
            return AddInstruction(rd, rn, imm, cond)
        
        sub_match = self.sub_pattern.match(line)
        if sub_match:
            rd = int(sub_match.group(1))
            rn = int(sub_match.group(2))
            imm = int(sub_match.group(3))
            return SubInstruction(rd, rn, imm, cond)
        
        ldr_match = self.ldr_pattern.match(line)
        if ldr_match:
            rd = int(ldr_match.group(1))
            rn = int(ldr_match.group(2))
            offset = int(ldr_match.group(3))
            return LdrInstruction(rd, rn, offset, cond)
        
        str_match = self.str_pattern.match(line)
        if str_match:
            rd = int(str_match.group(1))
            rn = int(str_match.group(2))
            offset = int(str_match.group(3))
            return StrInstruction(rd, rn, offset, cond)
        
        b_match = self.b_pattern.match(line)
        if b_match:
            label = b_match.group(1)
            # Create a branch instruction with a temporary target
            # We'll resolve it later when we know all label addresses
            instr = BranchInstruction(0, cond)
            self.unresolved_branches.append((self.current_address, label, instr))
            return instr
        
        bl_match = self.bl_pattern.match(line)
        if bl_match:
            label = bl_match.group(1)
            # Create a branch-link instruction with a temporary target
            instr = BranchLinkInstruction(0, cond)
            self.unresolved_branches.append((self.current_address, label, instr))
            return instr
        
        add_reg_match = self.add_reg_pattern.match(line)
        if add_reg_match:
            rd = int(add_reg_match.group(1))
            rn = int(add_reg_match.group(2))
            rm = int(add_reg_match.group(3))
            shift_name = add_reg_match.group(4)
            shift_amount = int(add_reg_match.group(5))
            shift_type = self._get_shift_type(shift_name)
            return AddRegInstruction(rd, rn, rm, shift_type, shift_amount, cond)
        
        sub_reg_match = self.sub_reg_pattern.match(line)
        if sub_reg_match:
            rd = int(sub_reg_match.group(1))
            rn = int(sub_reg_match.group(2))
            rm = int(sub_reg_match.group(3))
            shift_name = sub_reg_match.group(4)
            shift_amount = int(sub_reg_match.group(5))
            shift_type = self._get_shift_type(shift_name)
            return SubRegInstruction(rd, rn, rm, shift_type, shift_amount, cond)
        
        # If no pattern matches, raise an error
        raise ValueError(f"Unrecognized instruction: {line}")
    
    def _resolve_branches(self):
        """Resolve branch targets after all labels are known"""
        for addr, label, instr in self.unresolved_branches:
            if label not in self.labels:
                raise ValueError(f"Undefined label: {label}")
            
            target_addr = self.labels[label]
            offset = target_addr - (addr + 8)  # PC is 8 bytes ahead
            
            # Convert to words and check range
            offset = offset >> 2
            if offset < -0x800000 or offset > 0x7FFFFF:
                raise ValueError(f"Branch target out of range: {label}")
            
            # Update the instruction's target
            instr.target = offset & 0xFFFFFF
    
    def parse_file(self, filename: str) -> List[Instruction]:
        """
        Parse an assembly file and return a list of instructions
        
        Args:
            filename: Path to the assembly file
            
        Returns:
            A list of Instruction objects
        """
        instructions = []
        self.labels.clear()
        self.unresolved_branches.clear()
        self.current_address = 0
        
        # First pass: collect labels and create instructions
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    instruction = self.parse_line(line)
                    if instruction:
                        instructions.append(instruction)
                        self.current_address += 4  # Each instruction is 4 bytes
                except ValueError as e:
                    raise ValueError(f"Error on line {line_num}: {str(e)}")
        
        # Second pass: resolve branch targets
        self._resolve_branches()
        
        return instructions 