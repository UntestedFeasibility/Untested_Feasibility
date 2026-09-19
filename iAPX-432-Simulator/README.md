# Intel iAPX 432 Educational Simulator

An educational Python simulator of the Intel iAPX 432 General Data Processor (GDP), implementing a simplified subset of the architecture for learning capability-based security and object-oriented hardware concepts.

*First created: 2021*

## Overview

The Intel iAPX 432 (1981) was a revolutionary but commercially failed processor that pioneered:
- **Object-based architecture** — Hardware-enforced object types
- **Capability-based addressing** — Access descriptors for memory protection
- **Hardware memory management** — Two-level address translation
- **Domain-based protection** — Process isolation in hardware

This simulator implements a simplified educational subset focusing on these core concepts.

## Project Structure

```
iAPX-432-Simulator/
├── docs/                          # Technical reference documentation
│   ├── 01-architecture.md         # System architecture overview
│   ├── 02-instruction-set.md      # ISA reference
│   ├── 03-memory-model.md         # Segmented memory & capabilities
│   ├── 04-object-model.md         # Objects, domains, contexts
│   ├── 05-data-types.md           # Data representations
│   └── 06-historical-context.md   # Why iAPX 432 failed
├── src/                           # Python simulator source
│   ├── __init__.py
│   ├── cpu.py                     # CPU registers, pipeline
│   ├── decoder.py                 # Variable-length instruction decoder
│   ├── execution.py               # ALU, stack operations
│   ├── memory.py                  # Segmented memory model
│   ├── objects.py                 # Access descriptors, domains
│   ├── capabilities.py            # Capability checking logic
│   └── simulator.py               # Main simulator loop
├── programs/                      # Example iAPX 432 programs
│   ├── hello.i432                 # Hello world
│   ├── stack_ops.i432             # Stack manipulation
│   ├── capability_demo.i432       # Capability-based access
│   └── domain_switch.i432         # Domain switching
└── tests/                         # Unit tests
    ├── test_decoder.py
    ├── test_execution.py
    └── test_memory.py
```

## Quick Start

### Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

### Installation

```bash
# Clone the repository
git clone https://github.com/UntestedFeasibility/Untested_Feasibility.git
cd Untested_Feasibility/iAPX-432-Simulator

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies (none required, but good practice)
pip install -r requirements.txt
```

### Running

```bash
# Run the test suite
python -m pytest tests/

# Or run individual test files
python tests/test_decoder.py
python tests/test_execution.py
python tests/test_memory.py

# Interactive mode (coming soon)
python src/simulator.py --interactive
```

## Architecture Summary

### Instruction Format (Variable-Length Bit Encoding)

```
┌─────────────┬─────────────┬──────────────────┬─────────────┐
│ Class Field │ Format Field│ Reference Fields  │ Opcode Field│
│  (4-6 bits) │  (0-4 bits) │ (variable length) │  (0-5 bits) │
└─────────────┴─────────────┴──────────────────┴─────────────┘
```

### Key Concepts Implemented

1. **Operand Stack** — No general-purpose registers; all operations use a stack
2. **Access Descriptors** — Capabilities that control access to objects
3. **Protection Domains** — Isolated execution environments
4. **Type Checking** — Hardware-enforced object types

## Scope

This is an **educational simplification**, not a complete implementation:

| Component | Status | Notes |
|-----------|--------|-------|
| Instruction decoder | Implemented | Variable-length bit encoding |
| Operand stack | Implemented | 32-bit stack operations |
| Integer arithmetic | Implemented | ADD, SUB, MUL, DIV, AND, OR, XOR |
| Character operations | Implemented | LOAD, STORE, COMPARE |
| Branching | Implemented | Conditional/unconditional jumps |
| Memory model | Simplified | Linear address space |
| Capabilities | Simulated | Access descriptors as data structures |
| Domains | Simplified | Protection domains as objects |
| Floating point | Not implemented | Complex, not essential for education |
| Multiprocessing | Not implemented | Too complex for educational version |

## Documentation

See the `docs/` directory for the complete technical reference:

- [Architecture Overview](docs/01-architecture.md)
- [Instruction Set Reference](docs/02-instruction-set.md)
- [Memory Model](docs/03-memory-model.md)
- [Object Model](docs/04-object-model.md)
- [Data Types](docs/05-data-types.md)
- [Historical Context](docs/06-historical-context.md)

## Historical Context

The iAPX 432 was Intel's ambitious attempt to leapfrog the x86 architecture with a processor designed for high-level languages (Ada) and object-oriented programming. Despite its innovative design, it suffered from:

- **Poor performance** — 5-10x slower than contemporary x86
- **Complex microcode** — Large die size, long development
- **Compiler challenges** — Difficult to target effectively
- **Market timing** — Arrived as x86 gained momentum

The architecture was discontinued in 1986, but its ideas influenced modern capability-based systems like CHERI and seL4.

## License

Educational use. Documentation based on publicly available Intel manuals.

## References

- Intel iAPX 432 General Data Processor Architecture Reference Manual (1984)
- Intel iAPX 43201/43202 VLSI General Data Processor Data Sheet (1981)
- Capability-Based Computing (wikipedia.org/wiki/Capability-based_addressing)
