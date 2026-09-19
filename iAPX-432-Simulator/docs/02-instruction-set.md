# iAPX 432 Instruction Set Reference

## Overview

The iAPX 432 uses a variable-length bit-level instruction encoding. Instructions can start at any bit boundary and range from ~10 to 300+ bits. This document describes the complete instruction format and operation set.

## Instruction Format

Every iAPX 432 instruction consists of up to four fields:

```
┌─────────────┬─────────────┬──────────────────┬─────────────┐
│ Class Field │ Format Field│ Reference Fields  │ Opcode Field│
│  (4-6 bits) │  (0-4 bits) │ (variable length) │  (0-5 bits) │
└─────────────┴─────────────┴──────────────────┴─────────────┘
```

### Class Field (4-6 bits)

Specifies the number of operands and their primitive types.

**4-bit Primary Encoding:**

| Binary | Dec | Operands | Types |
|--------|-----|----------|-------|
| 0000 | 0 | 0 refs | No operands |
| 0001 | 1 | 1 ref | Word operand |
| 0010 | 2 | 2 refs | Word operands |
| 0011 | 3 | 3 refs | Word operands |
| 0100 | 4 | 1 ref | Byte operand |
| 0101 | 5 | 1 ref + 1 word | Mixed |
| 0110 | 6 | 2 refs | Byte operands |
| 0111 | 7 | 3 refs | Byte operands |
| 1000 | 8 | Extended class | See below |
| 1001-1111 | 9-15 | Object ops | Object/class operations |

**Extended Class (when bits = 1000):**

Additional 4 bits follow for more operand combinations.

### Format Field (0-4 bits)

Specifies how operands are referenced (stack vs. explicit).

| Binary | Meaning |
|--------|---------|
| 000 | All operands on stack |
| 001 | 1 explicit, rest on stack |
| 010 | 2 explicit, rest on stack |
| 011 | 3 explicit (all) |
| 100 | 1 explicit with double use |
| 101 | 2 explicit with double use |

**Double Use:** A single reference can serve as both source and destination.

### Reference Fields (variable)

Each explicit reference contains:

```
┌──────────────────┬─────────────────────┐
│ Access Selection │ Displacement        │
│    (4-5 bits)    │   (7-16 bits)       │
└──────────────────┴─────────────────────┘
```

**Access Selection Modes:**

| Code | Mode | Description |
|------|------|-------------|
| 0000 | Direct | AD is in register/context |
| 0001 | Indirect | AD is in memory |
| 0010 | Stack | Operand on stack |
| 0011 | Relative | Relative to current segment |
| 0100 | Indexed | Array element access |
| 0101 | Double Indirect | AD pointer to AD |
| 0110 | Top of Stack | Peek at stack top |
| 0111 | Reserved | — |

### Opcode Field (0-5 bits)

Specifies the operation to perform.

| Code | Operation |
|------|-----------|
| 00000 | NOP |
| 00001 | LOAD |
| 00010 | STORE |
| 00011 | ADD |
| 00100 | SUB |
| 00101 | MUL |
| 00110 | DIV |
| 00111 | AND |
| 01000 | OR |
| 01001 | XOR |
| 01010 | NOT |
| 01011 | SHIFT |
| 01100 | COMPARE |
| 01101 | BRANCH |
| 01110 | BRANCHEQ |
| 01111 | BRANCHNE |
| 10000 | PUSH |
| 10001 | POP |
| 10010 | CALL |
| 10011 | RETURN |
| 10100 | CREATE |
| 10101 | DESTROY |
| 10110 | CHECKRIGHTS |
| 10111 | DOMAINSWITCH |
| 11000 | CHLOAD |
| 11001 | CHSTORE |
| 11010 | CHCOMPARE |
| 11011 | GETAD |
| 11100 | PUTAD |
| 11101 | GETTYPE |
| 11110 | SETTYPE |
| 11111 | HALT |

## Instruction Categories

### 1. Data Movement Instructions

#### LOAD
```
Format: LOAD <reference>
Stack:  ( -- value )
Effect: Push value from memory onto stack
```

#### STORE
```
Format: STORE <reference>
Stack:  ( value -- )
Effect: Pop value from stack, store to memory
```

#### PUSH
```
Format: PUSH <immediate>
Stack:  ( -- imm )
Effect: Push immediate value onto stack
```

#### POP
```
Format: POP
Stack:  ( value -- )
Effect: Remove top of stack
```

### 2. Arithmetic Instructions

#### ADD
```
Format: ADD
Stack:  ( a b -- sum )
Effect: Push a + b
```

#### SUB
```
Format: SUB
Stack:  ( a b -- diff )
Effect: Push a - b
```

#### MUL
```
Format: MUL
Stack:  ( a b -- product )
Effect: Push a * b
```

#### DIV
```
Format: DIV
Stack:  ( a b -- quotient )
Effect: Push a / b
Error:  Division by zero
```

### 3. Logical Instructions

#### AND
```
Format: AND
Stack:  ( a b -- result )
Effect: Push a & b (bitwise)
```

#### OR
```
Format: OR
Stack:  ( a b -- result )
Effect: Push a | b (bitwise)
```

#### XOR
```
Format: XOR
Stack:  ( a b -- result )
Effect: Push a ^ b (bitwise)
```

#### NOT
```
Format: NOT
Stack:  ( a -- result )
Effect: Push ~a (bitwise complement)
```

### 4. Shift Instructions

#### SHIFT
```
Format: SHIFT <direction> <count>
Stack:  ( value -- result )
Effect: Shift value by count bits
        direction: 0=left, 1=right
```

### 5. Comparison Instructions

#### COMPARE
```
Format: COMPARE
Stack:  ( a b -- flags )
Effect: Compare a and b, push condition flags
        Flags: LT(-1), EQ(0), GT(1)
```

### 6. Branch Instructions

#### BRANCH
```
Format: BRANCH <target>
Effect: Unconditional jump to target
```

#### BRANCHEQ
```
Format: BRANCHEQ <target>
Stack:  ( flag -- )
Effect: Jump if flag == 0
```

#### BRANCHNE
```
Format: BRANCHNE <target>
Stack:  ( flag -- )
Effect: Jump if flag != 0
```

### 7. Subroutine Instructions

#### CALL
```
Format: CALL <target>
Stack:  ( -- return_addr )
Effect: Push return address, jump to target
```

#### RETURN
```
Format: RETURN
Stack:  ( return_addr -- )
Effect: Pop return address, jump to it
```

### 8. Object Instructions

#### CREATE
```
Format: CREATE <type>
Stack:  ( -- ad )
Effect: Create new object of type, push AD
```

#### DESTROY
```
Format: DESTROY
Stack:  ( ad -- )
Effect: Destroy object referenced by AD
```

#### CHECKRIGHTS
```
Format: CHECKRIGHTS <rights>
Stack:  ( ad -- flag )
Effect: Check if AD has required rights
        Push 1 if has rights, 0 otherwise
```

#### DOMAINSWITCH
```
Format: DOMAINSWITCH
Stack:  ( domain_ad -- )
Effect: Switch to specified domain
```

### 9. Character Instructions

#### CHLOAD
```
Format: CHLOAD
Stack:  ( ad offset -- char )
Effect: Load character from object
```

#### CHSTORE
```
Format: CHSTORE
Stack:  ( ad offset char -- )
Effect: Store character to object
```

#### CHCOMPARE
```
Format: CHCOMPARE
Stack:  ( ad1 off1 ad2 off2 -- flag )
Effect: Compare two characters
```

### 10. Access Descriptor Instructions

#### GETAD
```
Format: GETAD <selector>
Stack:  ( -- ad )
Effect: Get access descriptor by selector
```

#### PUTAD
```
Format: PUTAD <selector>
Stack:  ( ad -- )
Effect: Put access descriptor to selector
```

### 11. Type Instructions

#### GETTYPE
```
Format: GETTYPE
Stack:  ( ad -- type )
Effect: Get object type from AD
```

#### SETTYPE
```
Format: SETTYPE
Stack:  ( ad type -- )
Effect: Set object type
```

### 12. Control Instructions

#### HALT
```
Format: HALT
Effect: Stop processor execution
```

## Instruction Encoding Examples

### Example 1: Simple Integer Add

```
Binary: 0011 011 0011
         │   │   │
         │   │   └── Opcode: ADD (0011)
         │   └────── Format: 3 explicit operands (011)
         └────────── Class: 2 word operands (0011)

Encoding: 10 bits total
```

### Example 2: Load with Displacement

```
Binary: 0001 001 0001 00000100 0011
         │   │   │       │      │
         │   │   │       │      └── Opcode: LOAD (00001)
         │   │   │       └───────── Displacement: 4
         │   │   └───────────────── Access: Direct (0001)
         │   └───────────────────── Format: 1 explicit (001)
         └───────────────────────── Class: 1 word operand (0001)

Encoding: 22 bits total
```

### Example 3: Branch if Equal

```
Binary: 01110 010 000000110010
          │    │        │
          │    │        └── Target offset: 50
          │    └─────────── Format: 1 explicit (010)
          └──────────────── Opcode: BRANCHEQ (01110)

Encoding: 18 bits total
```

## Execution Semantics

### Stack Operations

All arithmetic and logical operations use the operand stack:

```
Before:     Stack: [bottom] ... [a] [b] [top]
                         └──older──┘ └─newer─┘

ADD:        Stack: [bottom] ... [result]
                            └──older──┘

Effect:     Pop a and b, compute a + b, push result
```

### Memory Access

Memory operations use Access Descriptors:

```
LOAD with AD:
1. Fetch AD from specified location
2. Check AD exists in current domain
3. Check AD has READ rights
4. Check type matches operation
5. Compute physical address from AD
6. Fetch value from memory
7. Push value onto stack
```

### Domain Switching

```
DOMAINSWITCH:
1. Pop domain AD from stack
2. Check AD has DOMAIN_SWITCH rights
3. Save current context
4. Load new domain's context
5. Resume execution in new domain
```

## Instruction Timing

| Instruction Type | Cycles | Notes |
|-----------------|--------|-------|
| Stack operations | 1 | PUSH, POP |
| Arithmetic | 2 | ADD, SUB, MUL, DIV |
| Memory access | 3+ | Depends on cache hits |
| Branch (taken) | 3 | Pipeline flush |
| Branch (not taken) | 1 | No flush |
| Domain switch | 10+ | Full context save/restore |
| Object create | 5+ | Memory allocation |

## Fault Conditions

Instructions can generate faults:

| Fault | Cause | Handler |
|-------|-------|---------|
| Access Violation | AD not found or wrong rights | Trap to OS |
| Type Mismatch | Wrong object type | Trap to OS |
| Stack Overflow | Push when stack full | Trap to OS |
| Stack Underflow | Pop when stack empty | Trap to OS |
| Bounds Error | Memory access out of range | Trap to OS |
| Invalid Opcode | Unknown instruction | Trap to OS |
| Division by Zero | DIV with zero divisor | Trap to OS |
