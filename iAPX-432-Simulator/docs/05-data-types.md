# iAPX 432 Data Types

## Overview

The iAPX 432 supports multiple data types from 8-bit characters to 80-bit floating point numbers. All operations are performed on an operand stack.

## Primitive Data Types

### Character Types

#### Character (8-bit)
```
┌─────────────────────┐
│   Character         │
│   8 bits            │
│   Range: 0-255      │
│   Encoding: ASCII   │
└─────────────────────┘
```

Used for: Text strings, character I/O, ASCII operations

### Integer Types

#### Short Ordinal (16-bit unsigned)
```
┌─────────────────────────────────────────┐
│   Short Ordinal (16-bit)                │
│   16 bits, unsigned                     │
│   Range: 0 to 65,535                    │
│   Alignment: 16-bit (2 bytes)           │
└─────────────────────────────────────────┘
```

#### Short Integer (16-bit signed)
```
┌─────────────────────────────────────────┐
│   Short Integer (16-bit)                │
│   16 bits, two's complement             │
│   Range: -32,768 to +32,767             │
│   Alignment: 16-bit (2 bytes)           │
└─────────────────────────────────────────┘
```

#### Ordinal (32-bit unsigned)
```
┌─────────────────────────────────────────┐
│   Ordinal (32-bit)                      │
│   32 bits, unsigned                     │
│   Range: 0 to 4,294,967,295             │
│   Alignment: 32-bit (4 bytes)           │
└─────────────────────────────────────────┘
```

#### Integer (32-bit signed)
```
┌─────────────────────────────────────────┐
│   Integer (32-bit)                      │
│   32 bits, two's complement             │
│   Range: -2,147,483,648 to              │
│          +2,147,483,647                  │
│   Alignment: 32-bit (4 bytes)           │
└─────────────────────────────────────────┘
```

### Floating-Point Types

#### Short Real (32-bit IEEE)
```
┌─────────────────────────────────────────┐
│   Short Real (32-bit)                   │
│   IEEE 754 single precision             │
│   Sign: 1 bit                           │
│   Exponent: 8 bits (bias 127)           │
│   Mantissa: 23 bits                     │
│   Range: ±3.4×10^38                     │
│   Precision: ~7 decimal digits          │
└─────────────────────────────────────────┘
```

#### Real (64-bit IEEE)
```
┌─────────────────────────────────────────┐
│   Real (64-bit)                         │
│   IEEE 754 double precision             │
│   Sign: 1 bit                           │
│   Exponent: 11 bits (bias 1023)         │
│   Mantissa: 52 bits                     │
│   Range: ±1.8×10^308                    │
│   Precision: ~15 decimal digits         │
└─────────────────────────────────────────┘
```

#### Temporary Real (80-bit Intel)
```
┌─────────────────────────────────────────┐
│   Temporary Real (80-bit)               │
│   Intel extended precision              │
│   Sign: 1 bit                           │
│   Exponent: 15 bits (bias 16383)        │
│   Mantissa: 64 bits (explicit integer)  │
│   Range: ±1.2×10^4932                   │
│   Precision: ~18 decimal digits         │
└─────────────────────────────────────────┘
```

## Data Representation in Memory

### Byte Ordering

The iAPX 432 uses **little-endian** byte ordering:

```
32-bit Integer 0x12345678 stored at address 0x1000:

Address:  0x1000  0x1001  0x1002  0x1003
Value:      78      56      34      12
            └──LSB──────────────────MSB──┘
```

### Bit Numbering

Bits are numbered from least significant (0) to most significant (31):

```
Bit:      31 30 29 ... 3  2  1  0
Value:     1  0  1  ... 0  1  0  1
           └──MSB──────────────────LSB──┘
```

### Data Alignment

All data types must be naturally aligned:

| Type | Size | Alignment |
|------|------|-----------|
| Character | 1 byte | 1 byte |
| Short | 2 bytes | 2 bytes |
| Integer | 4 bytes | 4 bytes |
| Real | 4 bytes | 4 bytes |
| Double | 8 bytes | 8 bytes |
| Extended | 10 bytes | 2 bytes (on 10-byte boundary) |

## Stack Representation

### Operand Stack

The stack stores 32-bit words:

```
Stack Growth: Low address → High address

┌─────────────────┐
│   Stack Top     │  ← SP (Stack Pointer)
├─────────────────┤
│   Value 2       │
├─────────────────┤
│   Value 1       │
├─────────────────┤
│   ...           │
├─────────────────┤
│   Stack Bottom  │  ← Base of stack segment
└─────────────────┘
```

### Stack Operations

```
PUSH value:
  SP = SP + 4
  Memory[SP] = value

POP value:
  value = Memory[SP]
  SP = SP - 4

PEEK:
  return Memory[SP]  (without changing SP)
```

## Type Conversions

### Widening Conversions (safe)

```
Character → Short Integer:  zero-extend
Short Integer → Integer:    sign-extend
Integer → Real:             convert to floating point
```

### Narrowing Conversions (may lose data)

```
Integer → Short Integer:    truncate high bits
Real → Integer:             truncate fractional part
```

### Conversion Instructions

| Instruction | From | To | Notes |
|-------------|------|----|-------|
| CH2SHI | Character | Short Integer | Zero-extend |
| SHI2I | Short Integer | Integer | Sign-extend |
| I2SHI | Integer | Short Integer | Truncate |
| I2R | Integer | Real | Convert |
| R2I | Real | Integer | Truncate |
| R2D | Real | Double | Extend |
| D2R | Double | Real | Truncate |

## Data Structures

### Arrays

Arrays are stored as contiguous data:

```
Array[10] of Integer:

┌───────┬───────┬───────┬─────┬───────┐
│ [0]   │ [1]   │ [2]   │ ... │ [9]   │
│ 4bytes│ 4bytes│ 4bytes│     │ 4bytes│
└───────┴───────┴───────┴─────┴───────┘
Base     Base+4  Base+8       Base+36
```

Access: Base + (index × element_size)

### Records (Structures)

Records are stored with fields in declaration order:

```
Record:
  Field1: Integer (4 bytes)
  Field2: Character (1 byte)
  Field3: Short Integer (2 bytes)

Memory Layout:
┌───────┬───────┬───────┐
│Field1 │Field2 │Field3 │
│ 4bytes│ 1byte │ 2bytes│
└───────┴───────┴───────┘
Offset: 0       4       5
```

### Pointers

Pointers are 32-bit addresses:

```
Pointer (32-bit):
┌─────────────────────────────────────────┐
│   Address (32 bits)                     │
│   Points to start of object/field       │
└─────────────────────────────────────────┘
```

## Special Values

### IEEE 754 Special Values

| Value | Representation | Meaning |
|-------|----------------|---------|
| +Infinity | Sign=0, Exp=all 1s, Mantissa=0 | Positive overflow |
| -Infinity | Sign=1, Exp=all 1s, Mantissa=0 | Negative overflow |
| NaN | Sign=X, Exp=all 1s, Mantissa≠0 | Not a Number |
| +0 | All bits zero | Positive zero |
| -0 | Sign=1, rest zero | Negative zero |

### Integer Special Values

| Value | Representation | Meaning |
|-------|----------------|---------|
| Max Int | 0x7FFFFFFF | Largest positive integer |
| Min Int | 0x80000000 | Largest negative integer |
| Zero | 0x00000000 | Integer zero |

## Simplified Implementation

In this simulator, data types are represented as Python types:

| iAPX 432 Type | Python Type | Notes |
|---------------|-------------|-------|
| Character | int (0-255) | Single byte |
| Short Integer | int (-32768 to 32767) | 16-bit signed |
| Integer | int | Arbitrary precision |
| Real | float | 64-bit double |
| Pointer | int | Memory address |

Type checking is simulated in software rather than hardware.
