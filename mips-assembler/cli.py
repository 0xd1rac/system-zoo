#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import Optional

from mips_assembler.parser import MIPSParser
from mips_assembler.encoder import MIPSEncoder

def assemble(input_file: Path, output_file: Optional[Path] = None) -> None:
    """
    Assemble a MIPS assembly file into machine code
    
    Args:
        input_file: Path to the input assembly file
        output_file: Path to the output machine code file (optional)
    """
    try:
        # Read input file
        with open(input_file, 'r') as f:
            code = f.read()
        
        # Parse the code
        parser = MIPSParser()
        instructions = parser.parse(code)
        
        # Encode the instructions
        encoder = MIPSEncoder()
        machine_code = encoder.encode(instructions)
        
        # Write output
        if output_file:
            with open(output_file, 'w') as f:
                for code in machine_code:
                    # Convert to 32-bit binary string, padded with leading zeros
                    binary_str = format(code, '032b')
                    f.write(f"{binary_str}\n")
            print(f"Successfully assembled {input_file} to {output_file}")
        else:
            # Print to stdout
            for code in machine_code:
                # Convert to 32-bit binary string, padded with leading zeros
                binary_str = format(code, '032b')
                print(binary_str)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point for the MIPS assembler CLI"""
    parser = argparse.ArgumentParser(description='MIPS Assembler')
    parser.add_argument('input', type=Path, help='Input assembly file')
    parser.add_argument('-o', '--output', type=Path, help='Output machine code file')
    parser.add_argument('-v', '--version', action='version', version='MIPS Assembler 1.0')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not args.input.exists():
        print(f"Error: Input file {args.input} does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Assemble the code
    assemble(args.input, args.output)

if __name__ == '__main__':
    main() 