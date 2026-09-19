# iAPX 432 Memory Model

## Overview

The iAPX 432 uses a sophisticated memory model based on segmented objects with hardware-enforced protection. This document describes the memory organization, address translation, and capability-based access control.

## Memory Organization

### Address Spaces

The iAPX 432 defines three address spaces:

```
┌─────────────────────────────────────────────────────────────┐
│                    Virtual Address Space                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                        │
│  │  Global Space    │  Shared across all domains            │
│  │  (2^40 bytes)   │  Contains system objects               │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  Local Space     │  Per-domain private memory            │
│  │  (variable)     │  Isolated between domains              │
│  └─────────────────┘                                        │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  Temporary Space │  Per-context temporary storage        │
│  │  (small)        │  Stack and scratch data                │
│  └─────────────────┘                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Segments

Memory is divided into segments with hardware-enforced boundaries:

```
┌─────────────────────────────────────────┐
│           Segment                       │
├─────────────────────────────────────────┤
│  Header (64 bits)                       │
│  ┌─────────────────────────────────┐   │
│  │  Type            │  8 bits      │   │
│  │  Reference Count │  8 bits      │   │
│  │  Lock            │  8 bits      │   │
│  │  Access Rights   │  16 bits     │   │
│  │  Data Length     │  16 bits     │   │
│  │  Reserved        │  8 bits      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Data Part (variable length)            │
│  ┌─────────────────────────────────┐   │
│  │  ... segment data ...           │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

## Segment Types

### Instruction Segments

Store executable code:

```
┌─────────────────────────────────────────┐
│        Instruction Segment              │
├─────────────────────────────────────────┤
│  Type: CODE                             │
│  Access: EXECUTE only                   │
│  Max Size: 64K bits (8K bytes)          │
│  Starting Bit: 64 (after header)        │
│                                         │
│  Contains: iAPX 432 instructions        │
│  Bit-addressable (can start anywhere)   │
└─────────────────────────────────────────┘
```

### Data Segments

Store program data:

```
┌─────────────────────────────────────────┐
│           Data Segment                  │
├─────────────────────────────────────────┤
│  Type: DATA                             │
│  Access: READ, WRITE, or READ+WRITE     │
│  Max Size: 64K bytes                    │
│                                         │
│  Contains: Variables, constants,        │
│            object headers, etc.         │
└─────────────────────────────────────────┘
```

### Stack Segments

Used for operand stack:

```
┌─────────────────────────────────────────┐
│          Stack Segment                  │
├─────────────────────────────────────────┤
│  Type: STACK                            │
│  Access: READ+WRITE                     │
│  Max Size: 64K bytes                    │
│                                         │
│  Contains: Operand stack                │
│  Grows toward higher addresses          │
└─────────────────────────────────────────┘
```

### System Segments

Used by the OS for system objects:

```
┌─────────────────────────────────────────┐
│         System Segment                  │
├─────────────────────────────────────────┤
│  Type: SYSTEM                           │
│  Access: Privileged only                │
│  Max Size: Variable                     │
│                                         │
│  Contains: Domain tables, context       │
│            objects, type managers       │
└─────────────────────────────────────────┘
```

## Two-Level Address Translation

### Level 1: Segment Lookup

```
Context Object
      │
      ▼
┌─────────────────────┐
│   Segment Table     │  Array of segment descriptors
│   (in context)      │  Each entry: base + length + rights
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Segment Descriptor │  Physical location of segment
│  (found by index)   │  + access rights check
└──────────┬──────────┘
           │
           ▼
      Segment Base Address
```

### Level 2: Displacement

```
Segment Base + Displacement = Linear Address
```

### Complete Translation

```
Logical Address: [segment_index, displacement]
      │
      ▼
┌─────────────────────────────────────────┐
│  1. Look up segment in context table    │
│  2. Check segment exists                │
│  3. Check displacement < segment length │
│  4. Check access rights                 │
│  5. Compute: base + displacement        │
│  6. Return physical address             │
└─────────────────────────────────────────┘
      │
      ▼
Physical Address
```

## Access Rights

### Rights Bits

Each segment has access rights encoded in 16 bits:

```
┌─────────────────────────────────────────┐
│           Access Rights (16 bits)       │
├─────────────────────────────────────────┤
│  Bit 0:  READ                            │
│  Bit 1:  WRITE                           │
│  Bit 2:  EXECUTE                         │
│  Bit 3:  APPEND                          │
│  Bit 4:  DELETE                          │
│  Bit 5:  COPY                            │
│  Bit 6:  DOMAIN_ENTRY                    │
│  Bit 7:  DOMAIN_EXIT                     │
│  Bit 8:  CREATE_OBJECT                   │
│  Bit 9:  DESTROY_OBJECT                  │
│  Bit 10: CHECK_TYPE                      │
│  Bit 11: SET_TYPE                        │
│  Bit 12-15: Reserved                     │
└─────────────────────────────────────────┘
```

### Rights Checking

When accessing a segment:

```
Required Rights:  READ | EXECUTE
Actual Rights:    READ | WRITE | EXECUTE

Check: (Actual & Required) == Required
Result: PASS (has all required rights)
```

### Rights Inheritance

When creating new objects:

```
Parent Domain Rights: READ | WRITE | CREATE_OBJECT
      │
      ▼
New Object Rights: Cannot exceed parent rights
      │
      ▼
Result: New object gets min(parent, requested) rights
```

## Capability-Based Access

### Access Descriptors (ADs)

ADs are the only way to access objects:

```
┌─────────────────────────────────────────┐
│       Access Descriptor (64 bits)       │
├─────────────────────────────────────────┤
│  Object Pointer   │  32 bits            │
│  Access Rights    │  16 bits            │
│  Type Check       │  16 bits            │
└─────────────────────────────────────────┘
```

### AD Resolution

```
AD in Domain:
      │
      ▼
┌─────────────────────────────────────────┐
│  1. Verify AD exists in current domain  │
│  2. Check AD rights include required    │
│  3. Check type matches operation        │
│  4. Follow pointer to object            │
│  5. Perform operation on object         │
└─────────────────────────────────────────┘
```

### AD Storage

ADs are stored in domain objects:

```
Domain Object:
┌─────────────────────────────────────────┐
│  Domain ID        │  32 bits            │
│  AD Count         │  16 bits            │
│  AD Table Pointer │  32 bits            │
│  ...              │                     │
└─────────────────────────────────────────┘
      │
      ▼
AD Table:
┌─────────────────────────────────────────┐
│  AD[0]: [ptr] [rights] [type]          │
│  AD[1]: [ptr] [rights] [type]          │
│  AD[2]: [ptr] [rights] [type]          │
│  ...                                    │
└─────────────────────────────────────────┘
```

## Memory Protection

### Bounds Checking

Every memory access is checked:

```
Access: [segment, offset]
      │
      ▼
┌─────────────────────────────────────────┐
│  Check 1: segment exists                │
│  Check 2: offset < segment.length       │
│  Check 3: access type allowed           │
│  Check 4: type matches operation        │
│                                         │
│  If ANY check fails: FAULT              │
└─────────────────────────────────────────┘
```

### Fault on Violation

When protection is violated:

```
┌─────────────────────────────────────────┐
│           Access Violation              │
├─────────────────────────────────────────┤
│  1. Current instruction aborted         │
│  2. Fault code written to fault area    │
│  3. Fault information saved:            │
│     - Faulting address                  │
│     - Required access                   │
│     - Actual access                     │
│     - Program counter                   │
│  4. Control transfers to fault handler  │
│  5. Handler may:                        │
│     - Fix the problem                   │
│     - Terminate the domain              │
│     - Log the violation                 │
└─────────────────────────────────────────┘
```

## Memory Map Example

```
Physical Memory Layout:
┌─────────────────────────────────────────┐
│  0x00000000 - System Headers            │
│  0x00000100 - Domain Table              │
│  0x00001000 - Context Objects           │
│  0x00010000 - Global Segments           │
│  0x00100000 - Local Segments (Domain 1) │
│  0x00200000 - Local Segments (Domain 2) │
│  0x00300000 - Stack Space               │
│  0x00400000 - Temporary Space           │
│  ...                                    │
│  0x00FFFFFF - End of Memory             │
└─────────────────────────────────────────┘
```

## Simplified Implementation Notes

For this educational simulator, we simplify:

1. **Linear address space** — No full two-level translation
2. **Simulated capabilities** — ADs as Python objects
3. **No real hardware protection** — Software checks only
4. **Fixed-size segments** — Simplified from variable

These simplifications preserve the conceptual model while making the simulator manageable for educational purposes.
