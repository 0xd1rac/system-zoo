#!/usr/bin/env python3
import argparse
import sys
from .assembler import Assembler

def main():
    """Command-line interface for the ARM assembler"""
    parser = argparse.ArgumentParser(description='ARM Assembler')
    parser.add_argument('input_file', help='Input assembly file')
    parser.add_argument('-o', '--output', help='Output binary file')
    parser.add_argument('-d', '--disassemble', action='store_true', help='Disassemble a binary file')
    
    args = parser.parse_args()
    
    # If no output file is specified, use the input file name with .bin extension
    if not args.output and not args.disassemble:
        args.output = args.input_file.rsplit('.', 1)[0] + '.bin'
    
    try:
        assembler = Assembler()
        
        if args.disassemble:
            # Disassemble the binary file
            instructions = assembler.disassemble_file(args.input_file)
            for instruction in instructions:
                print(instruction)
        else:
            # Assemble the assembly file
            assembler.assemble_file(args.input_file, args.output)
            print(f"Assembled {args.input_file} to {args.output}")
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 