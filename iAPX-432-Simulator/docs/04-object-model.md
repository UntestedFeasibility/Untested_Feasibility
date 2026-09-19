# iAPX 432 Object Model

## Overview

The iAPX 432 is an object-based processor. Everything in the system—code, data, protection states, execution contexts—is represented as objects. This document describes the object model and how objects are managed.

## Core Concept: Everything is an Object

In the iAPX 432:

- **Code** → Instruction Objects
- **Data** → Data Objects
- **Protection States** → Domain Objects
- **Execution States** → Context Objects
- **Access Rights** → Access Descriptors

This uniformity allows the hardware to enforce consistent protection rules across all system components.

## Object Structure

### Standard Object Header

Every object begins with a 64-bit header:

```
┌─────────────────────────────────────────┐
│           Object Header (64 bits)       │
├─────────────────────────────────────────┤
│  Bits 0-7:   Type                       │
│  Bits 8-15:  Reference Count            │
│  Bits 16-23: Lock                       │
│  Bits 24-39: Access Rights              │
│  Bits 40-55: Data Length                │
│  Bits 56-63: Reserved                   │
└─────────────────────────────────────────┘
```

### Header Fields

| Field | Size | Description |
|-------|------|-------------|
| Type | 8 bits | Object type identifier |
| Reference Count | 8 bits | Number of ADs pointing to this object |
| Lock | 8 bits | Synchronization lock |
| Access Rights | 16 bits | Who can access this object |
| Data Length | 16 bits | Size of data part in bytes |
| Reserved | 8 bits | Must be zero |

## Object Types

### Type Codes

| Code | Type | Description |
|------|------|-------------|
| 0x00 | NULL | Null object (invalid) |
| 0x01 | INSTRUCTION | Code segment |
| 0x02 | DATA | Read-only data |
| 0x03 | DATA_RW | Read-write data |
| 0x04 | STACK | Stack segment |
| 0x05 | DOMAIN | Protection domain |
| 0x06 | CONTEXT | Execution context |
| 0x07 | ACCESS_DESCRIPTOR | Capability to access object |
| 0x08 | TYPE_MANAGER | Type checking manager |
| 0x09 | PROCESS | Process object |
| 0x0A | MESSAGE_PORT | IPC message port |
| 0x0B | STORAGE_POOL | Memory pool |
| 0x0C-0xFF | Reserved | System use |

## Object Types in Detail

### 1. Instruction Objects

Store executable code:

```
┌─────────────────────────────────────────┐
│        Instruction Object               │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: INSTRUCTION (0x01)       │   │
│  │  Length: 8K bytes max           │   │
│  │  Rights: EXECUTE                │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Data Part                              │
│  ┌─────────────────────────────────┐   │
│  │  Bit 64: First instruction      │   │
│  │  ... iAPX 432 instructions ...  │   │
│  │  (bit-addressable, variable len)│   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 2. Data Objects

Store program data:

```
┌─────────────────────────────────────────┐
│           Data Object                   │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: DATA (0x02) or           │   │
│  │        DATA_RW (0x03)           │   │
│  │  Length: variable               │   │
│  │  Rights: READ or READ+WRITE     │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Data Part                              │
│  ┌─────────────────────────────────┐   │
│  │  ... object data ...            │   │
│  │  (bytes, words, structures)     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 3. Domain Objects

Represent protection domains:

```
┌─────────────────────────────────────────┐
│          Domain Object                  │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: DOMAIN (0x05)            │   │
│  │  Rights: DOMAIN_ENTRY           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Domain Data                            │
│  ┌─────────────────────────────────┐   │
│  │  Domain ID       │  32 bits    │   │
│  │  AD Table Ptr    │  32 bits    │   │
│  │  Code Space Ptr  │  32 bits    │   │
│  │  Data Space Ptr  │  32 bits    │   │
│  │  Stack Ptr       │  32 bits    │   │
│  │  Privilege Level │  4 bits     │   │
│  │  AD Count        │  16 bits    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  AD Table                              │
│  ┌─────────────────────────────────┐   │
│  │  AD[0]: [ptr] [rights] [type]  │   │
│  │  AD[1]: [ptr] [rights] [type]  │   │
│  │  ...                           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 4. Context Objects

Represent execution state:

```
┌─────────────────────────────────────────┐
│         Context Object                  │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: CONTEXT (0x06)           │   │
│  │  Rights: READ+WRITE             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Context Data                           │
│  ┌─────────────────────────────────┐   │
│  │  Program Counter │  32 bits    │   │
│  │  Stack Pointer   │  32 bits    │   │
│  │  Base Pointer    │  32 bits    │   │
│  │  Condition Flags │  32 bits    │   │
│  │  Domain Pointer  │  32 bits    │   │
│  │  Status          │  16 bits    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 5. Access Descriptors (ADs)

Capabilities to access objects:

```
┌─────────────────────────────────────────┐
│      Access Descriptor (AD)             │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: ACCESS_DESCRIPTOR (0x07) │   │
│  └─────────────────────────────────┘   │
│                                         │
│  AD Data                                │
│  ┌─────────────────────────────────┐   │
│  │  Object Pointer  │  32 bits    │   │
│  │  Access Rights   │  16 bits    │   │
│  │  Type Check      │  16 bits    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Object Operations

### Creating Objects

```
CREATE <type> <size>
      │
      ▼
┌─────────────────────────────────────────┐
│  1. Allocate memory for object          │
│  2. Initialize header:                  │
│     - Set type                          │
│     - Set reference count to 0          │
│     - Set access rights                 │
│     - Set data length                   │
│  3. Create AD pointing to object        │
│  4. Add AD to current domain            │
│  5. Push AD onto stack                  │
└─────────────────────────────────────────┘
```

### Destroying Objects

```
DESTROY <ad>
      │
      ▼
┌─────────────────────────────────────────┐
│  1. Verify AD has DESTROY rights        │
│  2. Decrement reference count           │
│  3. If ref count == 0:                  │
│     - Free memory                       │
│     - Remove all ADs pointing to it     │
│  4. Remove AD from domain               │
└─────────────────────────────────────────┘
```

### Accessing Objects

```
ACCESS <ad> <operation>
      │
      ▼
┌─────────────────────────────────────────┐
│  1. Verify AD exists in current domain  │
│  2. Check AD rights for operation       │
│  3. Check type matches operation        │
│  4. Follow AD pointer to object         │
│  5. Perform operation                   │
│  6. Return result                       │
└─────────────────────────────────────────┘
```

## Type Managers

Type managers enforce type checking for user-defined types:

```
┌─────────────────────────────────────────┐
│         Type Manager Object             │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: TYPE_MANAGER (0x08)      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Type Manager Data                      │
│  ┌─────────────────────────────────┐   │
│  │  Type ID          │  16 bits   │   │
│  │  Size             │  32 bits   │   │
│  │  Operations       │  array     │   │
│  │  Validation Code  │  pointer   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Type Checking Process

```
Object Access:
      │
      ▼
┌─────────────────────────────────────────┐
│  1. Get object's type from header       │
│  2. Look up type manager for type       │
│  3. Call type manager's validation      │
│  4. If valid: allow access              │
│  5. If invalid: fault                   │
└─────────────────────────────────────────┘
```

## Process Objects

Represent active processes:

```
┌─────────────────────────────────────────┐
│          Process Object                 │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: PROCESS (0x09)           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Process Data                           │
│  ┌─────────────────────────────────┐   │
│  │  Process ID       │  32 bits   │   │
│  │  Domain Pointer   │  32 bits   │   │
│  │  Context Pointer  │  32 bits   │   │
│  │  Priority         │  8 bits    │   │
│  │  State            │  8 bits    │   │
│  │  Message Queue    │  pointer   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Message Passing

Objects communicate via messages:

```
┌─────────────────────────────────────────┐
│        Message Port Object              │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: MESSAGE_PORT (0x0A)      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Message Port Data                      │
│  ┌─────────────────────────────────┐   │
│  │  Port ID          │  32 bits   │   │
│  │  Queue Head       │  pointer   │   │
│  │  Queue Tail       │  pointer   │   │
│  │  Max Messages     │  16 bits   │   │
│  │  Current Count    │  16 bits   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### Message Format

```
┌─────────────────────────────────────────┐
│           Message Object                │
├─────────────────────────────────────────┤
│  Header                                │
│  ┌─────────────────────────────────┐   │
│  │  Type: MESSAGE (0x0B)           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Message Data                           │
│  ┌─────────────────────────────────┐   │
│  │  Sender ID        │  32 bits   │   │
│  │  Receiver ID      │  32 bits   │   │
│  │  Message Type     │  16 bits   │   │
│  │  Data Length      │  16 bits   │   │
│  │  Data             │  variable  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Object Lifetime

### Object States

```
┌─────────────────────────────────────────┐
│           Object Lifecycle              │
├─────────────────────────────────────────┤
│                                         │
│  UNINITIALIZED ──► ALLOCATED            │
│       │               │                 │
│       │               ▼                 │
│       │          INITIALIZED            │
│       │               │                 │
│       │               ▼                 │
│       │           ACTIVE ◄──────┐      │
│       │               │         │      │
│       │               ▼         │      │
│       │          SUSPENDED ─────┘      │
│       │               │                 │
│       │               ▼                 │
│       └──────► DESTROYED               │
│                                         │
└─────────────────────────────────────────┘
```

### Reference Counting

Objects are destroyed when reference count reaches zero:

```
CREATE object → ref_count = 1
CREATE AD to object → ref_count = 2
DESTROY AD → ref_count = 1
DESTROY object → ref_count = 0 → FREE
```

## Simplified Implementation

For this educational simulator, we implement objects as Python classes:

```python
class Object:
    def __init__(self, obj_type, data=None):
        self.type = obj_type
        self.ref_count = 0
        self.lock = 0
        self.access_rights = 0
        self.data = data or []
    
    def add_reference(self):
        self.ref_count += 1
    
    def remove_reference(self):
        self.ref_count -= 1
        return self.ref_count == 0
```

This preserves the conceptual model while being manageable for educational purposes.
