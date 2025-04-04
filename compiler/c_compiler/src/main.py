import argparse
import sys
from pathlib import Path
from .lexer.lexer import Lexer
from .parser.parser import Parser
from .codegen.arm_generator import ARMGenerator
from .linker.elf_linker import ELFLinker

def compile_file(input_file: str, output_file: str, generate_elf: bool = False) -> None:
    """
    Compile a C source file to ARM assembly or ELF executable.
    
    Args:
        input_file: Path to the input C source file
        output_file: Path to the output file (assembly or ELF)
        generate_elf: Whether to generate an ELF executable instead of assembly
    """
    try:
        # Read input file
        with open(input_file, 'r') as f:
            source = f.read()
        
        # Lexical analysis
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parsing
        parser = Parser(tokens)
        ast = parser.parse()
        
        if generate_elf:
            # Generate ARM assembly first
            generator = ARMGenerator()
            assembly = generator.generate(ast)
            
            # Create ELF executable
            linker = ELFLinker()
            linker.add_assembly(assembly)
            linker.add_semihosting_exit()  # Add exit syscall
            linker.write_elf(output_file)
        else:
            # Generate ARM assembly
            generator = ARMGenerator()
            assembly = generator.generate(ast)
            
            # Write assembly to file
            with open(output_file, 'w') as f:
                f.write(assembly)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='C to ARM compiler')
    parser.add_argument('input', help='Input C source file')
    parser.add_argument('-o', '--output', help='Output file (defaults to input.s or input.elf)')
    parser.add_argument('--elf', action='store_true', help='Generate ELF executable instead of assembly')
    
    args = parser.parse_args()
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input)
        output_file = str(input_path.with_suffix('.elf' if args.elf else '.s'))
    
    compile_file(args.input, output_file, args.elf)

if __name__ == '__main__':
    main() 