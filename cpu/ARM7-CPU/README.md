# ARM7 CPU Implementation

A Verilog implementation of an ARM7 CPU with the following features:

## Architecture

- Basic 3-stage pipeline:
  - Fetch
  - Decode
  - Execute

## Memory Interface
- 1MB SRAM interface
- Memory-mapped I/O support
- Byte-addressable memory access

## Project Structure

```
ARM7-CPU/
├── rtl/                    # RTL implementation
│   ├── core/              # CPU core modules
│   │   ├── fetch.v        # Fetch stage
│   │   ├── decode.v       # Decode stage
│   │   └── execute.v      # Execute stage
│   ├── memory/            # Memory interface
│   │   ├── sram_ctrl.v    # SRAM controller
│   │   └── memory_map.v   # Memory mapping
│   └── top.v              # Top-level module
├── tb/                    # Testbench files
│   ├── tb_top.v          # Top-level testbench
│   └── test_program.hex   # Test program
└── sim/                   # Simulation files
    └── run.do            # Simulation script
```

## Implementation Details

### Pipeline Stages

1. Fetch Stage
   - Program counter management
   - Instruction fetch from memory
   - Branch prediction (simple)

2. Decode Stage
   - Instruction decoding
   - Register file access
   - Control signal generation

3. Execute Stage
   - ALU operations
   - Memory access
   - Branch execution

### Memory Interface

- 1MB SRAM interface (20-bit address)
- Byte-addressable (32-bit data bus)
- Memory-mapped I/O regions
- Wait state support

## Building and Simulation

Requirements:
- Verilog simulator (e.g., ModelSim, Icarus Verilog)
- Synthesis tool (e.g., Vivado, Quartus)

## Testing

- Basic instruction set verification
- Memory interface testing
- Pipeline hazard testing
- Branch prediction testing
