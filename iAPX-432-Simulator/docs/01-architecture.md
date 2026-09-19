# iAPX 432 Architecture Overview

## System Architecture

The Intel iAPX 432 is a 32-bit object-based processor consisting of multiple VLSI chips working together as a single processor.

### Physical Components

```
┌─────────────────────────────────────────────────────────────┐
│                    iAPX 432 System                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   43201      │    │   43202      │    │   43203      │  │
│  │   (ID)       │◄──►│   (EU)       │◄──►│   (I/O)      │  │
│  │              │    │              │    │              │  │
│  │ Instruction  │    │  Execution   │    │  Interface   │  │
│  │ Decoder      │    │  Unit        │    │  Processor   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         └───────────────────┼───────────────────┘           │
│                             │                               │
│                    ┌────────┴────────┐                      │
│                    │  Processor      │                      │
│                    │  Packet Bus     │                      │
│                    └────────┬────────┘                      │
│                             │                               │
└─────────────────────────────┼───────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Memory System   │
                    │   (up to 16MB)    │
                    └───────────────────┘
```

### Pipeline Stages

The iAPX 432 uses a 3-stage microprogram-controlled pipeline:

```
Stage 1: Instruction Decoder (ID)
  - Fetches instructions from memory
  - Decodes variable-length bit fields
  - Prepares operand references

Stage 2: Microinstruction Sequencer (MS)
  - Sequences microcode
  - Handles branching within microcode
  - Manages pipeline control

Stage 3: Execution Unit (EU)
  - Performs arithmetic/logic operations
  - Accesses memory
  - Manages operand stack
```

## Memory Organization

### Address Spaces

The iAPX 432 supports three distinct address spaces:

1. **Global Space** — Shared across all domains (up to 2^40 bytes virtual)
2. **Local Space** — Per-domain private memory
3. **Temporary Space** — Per-context temporary storage

### Segmented Memory

Memory is organized into segments with hardware-enforced protection:

```
┌─────────────────────────────────────────┐
│          Segment Descriptor             │
├─────────────────────────────────────────┤
│  Base Address    │  24 bits             │
│  Segment Length  │  16 bits             │
│  Access Rights   │  8 bits             │
│  Type           │  4 bits             │
│  Reserved       │  12 bits            │
└─────────────────────────────────────────┘
```

### Two-Level Address Translation

```
Logical Address
      │
      ▼
┌─────────────┐
│   Segment    │  Level 1: Segment lookup
│   Table      │  (in memory, pointed to by context)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Linear     │  Level 2: Offset within segment
│   Address    │  (displacement from segment base)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Physical    │  Final address
│  Address     │  (in real memory)
└─────────────┘
```

## Object-Based Architecture

### Core Concept: Everything is an Object

Unlike traditional processors, the iAPX 432 treats everything as an object:

- Code is in **instruction objects**
- Data is in **data objects**
- Protection states are in **domain objects**
- Execution states are in **context objects**

### Object Structure

Every object has a standard header:

```
┌─────────────────────────────────────────┐
│           Object Header (64 bits)       │
├─────────────────────────────────────────┤
│  Type            │  8 bits              │
│  Reference Count │  8 bits              │
│  Lock            │  8 bits              │
│  Access Rights   │  16 bits            │
│  Data Length     │  16 bits            │
│  Reserved        │  8 bits              │
└─────────────────────────────────────────┘
│           Data Part (variable)          │
└─────────────────────────────────────────┘
```

## Capability-Based Access Control

### Access Descriptors (ADs)

Access to objects is controlled through Access Descriptors (ADs):

```
┌─────────────────────────────────────────┐
│       Access Descriptor (64 bits)       │
├─────────────────────────────────────────┤
│  Object Pointer   │  32 bits            │
│  Access Rights    │  16 bits            │
│  Type Check       │  16 bits            │
└─────────────────────────────────────────┘
```

ADs are the only way to access objects. The hardware checks:
1. Does the AD exist in the current domain?
2. Does the AD have the required access rights?
3. Does the AD's type match the operation?

### Protection Domains

A domain is a protected execution environment:

```
┌─────────────────────────────────────────┐
│           Domain Object                 │
├─────────────────────────────────────────┤
│  Domain ID        │  32 bits            │
│  Access Space     │  Pointer to ADs    │
│  Code Space       │  Pointer to code   │
│  Data Space       │  Pointer to data   │
│  Privilege Level  │  4 bits            │
└─────────────────────────────────────────┘
```

Domains provide:
- **Isolation** — Each domain has its own address space
- **Controlled sharing** — Objects can be shared via ADs
- **Least privilege** — Domains only have access to required objects

## Processor Communication

### The Processor Packet Bus

The 43201 and 43202 communicate via the Processor Packet Bus:

```
┌─────────────────────────────────────────────────────┐
│              Processor Packet Bus                   │
├─────────────────────────────────────────────────────┤
│  ACD[31:0]  │  Address/Control/Data (32 bits)      │
│  BE[3:0]    │  Byte Enable (4 bits)                │
│  PROT       │  Protection Fault                    │
│  ACK        │  Acknowledge                         │
│  BREQ       │  Bus Request                         │
│  BGO        │  Bus Grant Out                       │
│  BGIN       │  Bus Grant In                        │
│  HERR       │  Hardware Error                      │
│  EOP        │  End of Packet                       │
└─────────────────────────────────────────────────────┘
```

## Fault and Exception Handling

The iAPX 432 has comprehensive fault detection:

| Fault Type | Description |
|------------|-------------|
| Access Violation | Unauthorized object access |
| Type Mismatch | Wrong object type for operation |
| Bounds Error | Memory access out of segment bounds |
| Privilege Violation | Insufficient privilege level |
| Stack Overflow | Stack pointer out of bounds |
| Stack Underflow | Pop from empty stack |
| Invalid Opcode | Undefined instruction |
| Hardware Error | FRC mismatch or bus error |

When a fault occurs:
1. Current instruction is aborted
2. Fault information is written to a fault area
3. Control transfers to fault handler
4. Domain may be switched for recovery

## Comparison with x86

| Feature | iAPX 432 | x86 (80286) |
|---------|----------|-------------|
| Architecture | Object-based | Register-based |
| Addressing | Capability-based | Segment:Offset |
| Memory Protection | Hardware-enforced objects | Segment limits |
| Multiprocessing | Transparent | Manual coordination |
| Data Types | Object-oriented | Raw bytes |
| Registers | None (stack-based) | 16 GP registers |
| Performance | ~2 MIPS | ~4 MIPS |
| Complexity | Very high | Moderate |

## Summary

The iAPX 432 represented a radical departure from traditional processor design. While commercially unsuccessful, its innovations in capability-based security and object-oriented hardware influenced modern systems like:

- **CHERI** — Capability Hardware Enhanced RISC Instructions
- **seL4** — Formally verified microkernel with capabilities
- **ARM Morello** — ARM's capability architecture extension
- **WebAssembly** — Sandbox model inspired by capabilities

Understanding the iAPX 432 provides insight into these modern capability-based systems and the fundamental principles of hardware-enforced protection.
