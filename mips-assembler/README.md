# MIPS Assembler

A Python-based MIPS assembler that converts MIPS assembly code into binary machine code.

## Features

- Supports R-type, I-type, and J-type MIPS instructions
- Handles labels and branch targets
- Converts assembly code to 32-bit binary machine code
- Command-line interface for easy use
- Detailed error reporting

## Supported Instructions

### R-type Instructions
- `add`, `sub`, `and`, `or`
- `slt`, `sll`, `srl`
- `nop`

### I-type Instructions
- `addi`
- `lw`, `sw`
- `beq`, `bne`

### J-type Instructions
- `j`, `jal`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mips-assembler.git
cd mips-assembler
```

2. Install the package:
```bash
pip install -e .
```

## Usage

### Basic Usage
```bash
mips-assembler input.asm -o output.bin
```

### Command Line Options
- `input`: Input assembly file (required)
- `-o, --output`: Output binary file (optional, prints to stdout if not specified)
- `-v, --version`: Show version information

### Example

Given an input file `fibonacci.asm`:
```mips
main:
    addi $a0, $zero, 10    # Calculate fib(10)
    jal fib                # Call fib function
    j end                 # End program
```

Run the assembler:
```bash
mips-assembler fibonacci.asm -o fibonacci.bin
```

The output will be a binary file containing the machine code:
```
00000000000000000010000100001000
00001100000000000000000000000101
00001000000000000000000000011000
...
```

## Project Structure

- `mips_assembler/`
  - `lexer.py`: Tokenizes MIPS assembly code
  - `parser.py`: Parses tokens into instruction objects
  - `encoder.py`: Converts instructions to binary machine code
  - `cli.py`: Command-line interface
- `examples/`: Example MIPS assembly programs
- `setup.py`: Package installation script

## Development

### Running Tests
```bash
python -m unittest discover tests
```

### Adding New Instructions
1. Add the instruction to the appropriate dictionaries in `encoder.py`:
   - `OPCODES` for the opcode
   - `FUNCTS` for R-type function codes
2. Update the parser to handle the new instruction format
3. Add test cases in the `examples/` directory

## Error Handling

The assembler provides detailed error messages for:
- Invalid register names
- Undefined labels
- Syntax errors
- Unknown instructions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MIPS Architecture Reference Manual
- Python's built-in libraries for text processing
- The open-source community for inspiration and tools 