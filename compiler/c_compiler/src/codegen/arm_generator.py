from typing import List, Dict, Any, Optional
from ..parser.ast import Node, Program, Function, Variable, BinaryOp, Call, Literal

class ARMGenerator:
    """Generates ARM assembly code from an AST."""
    
    def __init__(self):
        self.data_section: List[str] = []
        self.text_section: List[str] = []
        self.current_function: Optional[str] = None
        self.variables: Dict[str, int] = {}
        self.string_literals: Dict[str, str] = {}
        self.string_counter = 0
    
    def generate(self, ast: Node) -> str:
        """Generate ARM assembly code from an AST."""
        if isinstance(ast, Program):
            return self.generate_program(ast)
        else:
            raise ValueError(f"Expected Program node, got {type(ast)}")
    
    def generate_program(self, program: Program) -> str:
        """Generate ARM assembly code for a program."""
        # Generate code for each function
        for function in program.functions:
            self.generate_function(function)
        
        # Combine sections
        return "\n".join([
            ".data",
            *self.data_section,
            "",
            ".text",
            ".global _start",
            *self.text_section
        ])
    
    def generate_function(self, function: Function) -> None:
        """Generate ARM assembly code for a function."""
        self.current_function = function.name
        self.variables.clear()
        
        # Function prologue
        self.text_section.extend([
            f"{function.name}:",
            "    push {fp, lr}",
            "    mov fp, sp",
            "    sub sp, sp, #8"  # Space for local variables
        ])
        
        # Generate code for function body
        for statement in function.body:
            self.generate_statement(statement)
        
        # Function epilogue
        self.text_section.extend([
            "    mov sp, fp",
            "    pop {fp, lr}",
            "    bx lr"
        ])
        
        self.current_function = None
    
    def generate_statement(self, statement: Node) -> None:
        """Generate ARM assembly code for a statement."""
        if isinstance(statement, Variable):
            self.generate_variable(statement)
        elif isinstance(statement, BinaryOp):
            self.generate_binary_op(statement)
        elif isinstance(statement, Call):
            self.generate_call(statement)
        elif isinstance(statement, Literal):
            self.generate_literal(statement)
        else:
            raise ValueError(f"Unsupported statement type: {type(statement)}")
    
    def generate_variable(self, variable: Variable) -> None:
        """Generate ARM assembly code for a variable declaration."""
        # Allocate space on stack
        offset = len(self.variables) * 4
        self.variables[variable.name] = offset
        
        # Generate initializer if present
        if variable.initializer:
            self.generate_expression(variable.initializer)
            self.text_section.append(f"    str r0, [fp, #-{offset + 8}]")
    
    def generate_binary_op(self, op: BinaryOp) -> None:
        """Generate ARM assembly code for a binary operation."""
        # Generate operands
        self.generate_expression(op.left)
        self.text_section.append("    mov r1, r0")
        self.generate_expression(op.right)
        self.text_section.append("    mov r2, r0")
        
        # Perform operation
        if op.operator == "+":
            self.text_section.append("    add r0, r1, r2")
        elif op.operator == "-":
            self.text_section.append("    sub r0, r1, r2")
        elif op.operator == "*":
            self.text_section.append("    mul r0, r1, r2")
        elif op.operator == "/":
            self.text_section.append("    sdiv r0, r1, r2")
        else:
            raise ValueError(f"Unsupported operator: {op.operator}")
    
    def generate_call(self, call: Call) -> None:
        """Generate ARM assembly code for a function call."""
        if call.function == "printf":
            # Handle printf specially - convert to semihosting write
            if len(call.arguments) != 1:
                raise ValueError("printf expects exactly one argument")
            
            arg = call.arguments[0]
            if isinstance(arg, Literal) and isinstance(arg.value, str):
                # Add string to data section
                label = f"str_{self.string_counter}"
                self.string_counter += 1
                self.data_section.append(f"{label}: .asciz {arg.value}")
                
                # Generate write syscall
                self.text_section.extend([
                    "    mov r0, #1",  # stdout
                    f"    ldr r1, ={label}",  # string address
                    f"    mov r2, #{len(arg.value)}",  # string length
                    "    mov r7, #4",  # SYS_WRITE
                    "    svc 0"  # semihosting call
                ])
            else:
                raise ValueError("printf argument must be a string literal")
        else:
            # Regular function call
            # Save arguments in registers
            for i, arg in enumerate(call.arguments):
                self.generate_expression(arg)
                if i < 4:  # ARM calling convention uses r0-r3
                    self.text_section.append(f"    mov r{i}, r0")
                else:
                    self.text_section.append(f"    push {{r0}}")
            
            # Call function
            self.text_section.append(f"    bl {call.function}")
            
            # Restore stack if needed
            if len(call.arguments) > 4:
                self.text_section.append(f"    add sp, sp, #{(len(call.arguments) - 4) * 4}")
    
    def generate_expression(self, expr: Node) -> None:
        """Generate ARM assembly code for an expression."""
        if isinstance(expr, Literal):
            self.generate_literal(expr)
        elif isinstance(expr, BinaryOp):
            self.generate_binary_op(expr)
        elif isinstance(expr, Call):
            self.generate_call(expr)
        else:
            raise ValueError(f"Unsupported expression type: {type(expr)}")
    
    def generate_literal(self, literal: Literal) -> None:
        """Generate ARM assembly code for a literal value."""
        if isinstance(literal.value, int):
            self.text_section.append(f"    mov r0, #{literal.value}")
        elif isinstance(literal.value, str):
            # Add string to data section
            label = f"str_{self.string_counter}"
            self.string_counter += 1
            self.data_section.append(f"{label}: .asciz {literal.value}")
            
            # Load string address
            self.text_section.append(f"    ldr r0, ={label}")
        else:
            raise ValueError(f"Unsupported literal type: {type(literal.value)}") 