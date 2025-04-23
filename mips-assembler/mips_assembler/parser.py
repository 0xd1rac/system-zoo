from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from .lexer import Token, MIPSLexer

class ParserError(Exception):
    """Custom exception for parser errors"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")

@dataclass
class Instruction:
    """Base class for MIPS instructions"""
    mnemonic: str
    line: int
    column: int

@dataclass
class RTypeInstruction(Instruction):
    """R-type instruction format"""
    rd: str      # Destination register
    rs: str      # Source register 1
    rt: str      # Source register 2
    shamt: Optional[str] = None  # Shift amount
    funct: Optional[int] = None  # Function code

@dataclass
class ITypeInstruction(Instruction):
    """I-type instruction format"""
    rt: str      # Target register
    rs: str      # Source register
    immediate: str  # Immediate value or offset

@dataclass
class JTypeInstruction(Instruction):
    """J-type instruction format"""
    address: str  # Jump target address

class MIPSParser:
    """Parser for MIPS assembly code"""
    
    # MIPS instruction type definitions
    INSTRUCTION_TYPES: Dict[str, Tuple[str, Optional[int]]] = {
        # R-type instructions
        'add': ('R', 0x20),  # funct = 0x20
        'sub': ('R', 0x22),  # funct = 0x22
        'and': ('R', 0x24),  # funct = 0x24
        'or':  ('R', 0x25),  # funct = 0x25
        'slt': ('R', 0x2A),  # funct = 0x2A
        'sll': ('R', 0x00),  # shamt = 0x00
        'srl': ('R', 0x02),  # shamt = 0x02
        'nop': ('R', 0x00),  # nop is sll $zero, $zero, 0
        
        # I-type instructions
        'addi': ('I', None),
        'lw':   ('I', None),
        'sw':   ('I', None),
        'beq':  ('I', None),
        'bne':  ('I', None),
        
        # J-type instructions
        'j':    ('J', None),
        'jal':  ('J', None),
    }

    def __init__(self):
        """Initialize the parser"""
        self.lexer = MIPSLexer()
        self.current_token: Optional[Token] = None
        self.tokens: List[Token] = []
        self.token_index: int = 0
        self.symbol_table: Dict[str, int] = {}  # Maps label names to instruction indices
        self.current_instruction_index: int = 0  # Tracks current instruction position

    def parse(self, code: str) -> List[Instruction]:
        """
        Parse MIPS assembly code into a list of instructions
        
        Args:
            code: The MIPS assembly code to parse
            
        Returns:
            List of Instruction objects
        """
        # First pass: build symbol table
        self.tokens = self.lexer.get_tokens(code)
        self.token_index = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.current_instruction_index = 0
        
        while self.current_token:
            if self.current_token.type == 'LABEL':
                # Store label position in symbol table
                self.symbol_table[self.current_token.value] = self.current_instruction_index
                self.advance()
            elif self.current_token.type == 'INSTR':
                self.current_instruction_index += 1
                self.advance()
            else:
                self.advance()
        
        # Second pass: parse instructions
        self.token_index = 0
        self.current_token = self.tokens[0] if self.tokens else None
        self.current_instruction_index = 0
        
        instructions = []
        while self.current_token:
            if self.current_token.type == 'LABEL':
                # Skip labels (already processed in first pass)
                self.advance()
            elif self.current_token.type == 'INSTR':
                instruction = self.parse_instruction()
                if instruction:
                    instructions.append(instruction)
                    self.current_instruction_index += 1
            else:
                self.advance()
                
        return instructions

    def advance(self) -> None:
        """Move to the next token"""
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def parse_instruction(self) -> Optional[Instruction]:
        """Parse a single instruction"""
        if not self.current_token or self.current_token.type != 'INSTR':
            return None
            
        mnemonic = self.current_token.value
        if mnemonic not in self.INSTRUCTION_TYPES:
            raise ParserError(f"Unknown instruction: {mnemonic}", self.current_token)
            
        instr_type, funct = self.INSTRUCTION_TYPES[mnemonic]
        line = self.current_token.line
        column = self.current_token.column
        
        self.advance()  # Move past the instruction
        
        if instr_type == 'R':
            return self.parse_r_type(mnemonic, funct, line, column)
        elif instr_type == 'I':
            return self.parse_i_type(mnemonic, line, column)
        elif instr_type == 'J':
            return self.parse_j_type(mnemonic, line, column)
            
        return None

    def parse_r_type(self, mnemonic: str, funct: int, line: int, column: int) -> RTypeInstruction:
        """Parse an R-type instruction"""
        if mnemonic == 'nop':
            # nop is a special case - it's sll $zero, $zero, 0
            return RTypeInstruction(mnemonic, line, column, '$zero', '$zero', '$zero', '0', funct)
        elif mnemonic in ['sll', 'srl']:
            # Special case for shift instructions
            rd = self.expect_token('REG').value
            self.expect_token('COMMA')
            rt = self.expect_token('REG').value
            self.expect_token('COMMA')
            shamt = self.expect_token('NUM').value
            return RTypeInstruction(mnemonic, line, column, rd, None, rt, shamt, funct)
        else:
            # Standard R-type format
            rd = self.expect_token('REG').value
            self.expect_token('COMMA')
            rs = self.expect_token('REG').value
            self.expect_token('COMMA')
            rt = self.expect_token('REG').value
            return RTypeInstruction(mnemonic, line, column, rd, rs, rt, None, funct)

    def parse_i_type(self, mnemonic: str, line: int, column: int) -> ITypeInstruction:
        """Parse an I-type instruction"""
        rt = self.expect_token('REG').value
        self.expect_token('COMMA')
        
        if mnemonic in ['lw', 'sw']:
            # Load/store format
            immediate = self.expect_token('NUM').value
            self.expect_token('LPAREN')
            rs = self.expect_token('REG').value
            self.expect_token('RPAREN')
        elif mnemonic in ['beq', 'bne']:
            # Branch instructions use a label as immediate
            rs = self.expect_token('REG').value
            self.expect_token('COMMA')
            label = self.expect_token('LABEL').value
            if label not in self.symbol_table:
                raise ParserError(f"Undefined label: {label}", self.current_token)
            # Calculate branch offset (number of instructions to jump)
            target_index = self.symbol_table[label]
            offset = target_index - (self.current_instruction_index + 1)  # +1 because PC is incremented
            immediate = str(offset)
        else:
            # Standard I-type format
            rs = self.expect_token('REG').value
            self.expect_token('COMMA')
            immediate = self.expect_token('NUM').value
            
        return ITypeInstruction(mnemonic, line, column, rt, rs, immediate)

    def parse_j_type(self, mnemonic: str, line: int, column: int) -> JTypeInstruction:
        """Parse a J-type instruction"""
        label = self.expect_token('LABEL').value
        if label not in self.symbol_table:
            raise ParserError(f"Undefined label: {label}", self.current_token)
        # For J-type, we store the target instruction index
        return JTypeInstruction(mnemonic, line, column, str(self.symbol_table[label]))

    def expect_token(self, expected_type: str) -> Token:
        """Expect a specific token type and return it, or raise an error"""
        if not self.current_token:
            raise ParserError(f"Expected {expected_type} but reached end of input", self.tokens[-1])
            
        if self.current_token.type != expected_type:
            raise ParserError(f"Expected {expected_type} but got {self.current_token.type}", 
                            self.current_token)
                            
        token = self.current_token
        self.advance()
        return token

# Example usage
if __name__ == '__main__':
    code = """
    loop:   add $t0, $t1, $t2   # This is a comment
            lw $s1, 0($sp)
            beq $t0, $zero, end
    end:    nop
    """
    parser = MIPSParser()
    instructions = parser.parse(code)
    
    for instr in instructions:
        print(f"Instruction: {instr.mnemonic}")
        if isinstance(instr, RTypeInstruction):
            print(f"  Type: R-type")
            print(f"  RD: {instr.rd}")
            print(f"  RS: {instr.rs}")
            print(f"  RT: {instr.rt}")
            if instr.shamt:
                print(f"  SHAMT: {instr.shamt}")
            if instr.funct:
                print(f"  FUNCT: {instr.funct:02x}")
        elif isinstance(instr, ITypeInstruction):
            print(f"  Type: I-type")
            print(f"  RT: {instr.rt}")
            print(f"  RS: {instr.rs}")
            print(f"  Immediate: {instr.immediate}")
        elif isinstance(instr, JTypeInstruction):
            print(f"  Type: J-type")
            print(f"  Address: {instr.address}") 
        