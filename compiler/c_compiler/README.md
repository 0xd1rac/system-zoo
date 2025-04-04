# C Compiler in Python

A C compiler written in Python that targets ARM assembly output. This project is designed to demonstrate the fundamentals of compiler design and implementation.

## Project Structure

```
c_compiler/
├── src/
│   ├── lexer/         # Tokenization
│   ├── parser/        # Abstract Syntax Tree
│   ├── semantic/      # Semantic Analysis
│   ├── codegen/       # ARM Assembly Generation
│   └── utils/         # Utility functions
├── tests/             # Test files
├── examples/          # Example C programs
└── docs/             # Documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

To compile a C file:
```bash
python -m c_compiler path/to/your/file.c
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Type checking: `mypy .` 