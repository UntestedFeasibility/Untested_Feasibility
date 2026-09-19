# BlackBerry PSI Bytecode Format

## Overview

The BlackBerry COD (Compiled Object Data) format is a proprietary binary container for compiled Java-like bytecode designed for RIM's custom 32-bit ARM virtual machine. This document describes the complete file format, instruction set, and data structures.

**Reference:** Based on reverse engineering analysis and the `bb-tools` project by waltermin.

## External Links

- [bb-tools repository](https://github.com/waltermin/bb-tools) — COD to JAR transpiler
- [HANDOFF.md](https://github.com/waltermin/bb-tools/blob/main/HANDOFF.md) — Comprehensive format documentation

## COD File Structure

A `.cod` file is a **two-layer container**:

```
┌─────────────────────────────────────┐
│         ZIP Archive Container       │
│  (standard ZIP, stored/no compress) │
├─────────────────────────────────────┤
│  base.cod    (segment 0)           │
│  base-1.cod  (segment 1)           │
│  base-2.cod  (segment 2)           │
│  ...                                │
│  base-N.cod  (segment N)           │
└─────────────────────────────────────┘
```

Each inner `.cod` part is limited to ~64KB due to 16-bit internal references.

## Inner COD Format

### Magic Number

```
Offset 0x00: 0xDE C0 FF FF  (little-endian: 0xFFFFC0DE = -16162)
```

### CodHeader (44 bytes)

All fields are **little-endian**:

| Offset | Size | Type | Field | Description |
|--------|------|------|-------|-------------|
| 0x00 | 4 | i32 | `flash_id` | Magic: 0xFFFFC0DE (-16162) |
| 0x04 | 4 | i32 | `sections` | Section count (0 in raw COD) |
| 0x08 | 4 | i32 | `vtable` | Vtable pointer (set at link time) |
| 0x0C | 4 | i32 | `timestamp` | Build timestamp |
| 0x10 | 4 | i32 | `user_version` | User version (often 0) |
| 0x14 | 4 | i32 | `field_refs` | Field reference count |
| 0x18 | 2 | i16 | `max_type_list_size` | Max type-list size |
| 0x1A | 2 | i16 | `reserved` | Reserved (0xFFFF) |
| 0x1C | 4 | i32 | `data_section_ptr` | Data section offset (-1 in raw) |
| 0x20 | 4 | i32 | `module_info_ptr` | Module info offset (-1 in raw) |
| 0x24 | 2 | u16 | `version` | COD format version (79 for OS 7.1) |
| 0x26 | 2 | u16 | `code_size` | Code segment size in bytes |
| 0x28 | 2 | u16 | `data_size` | Data segment size in bytes |
| 0x2A | 2 | u16 | `flags` | Module flags (masked & 0x37) |

### Flag Bits

| Bit | Mask | Meaning |
|-----|------|---------|
| 0 | 0x01 | **IsLibrary** |
| 1 | 0x02 | IsMidlet |
| 2 | 0x04 | **IsParseable** |
| 4 | 0x10 | IsBrittle |
| 5 | 0x20 | IsPlatform |

### File Layout

```
[0x00 .. 0x2C)                          CodHeader (44 bytes)
[0x2C .. 0x2C + code_size)              Code segment
[0x2C + code_size .. 0x2C + code_size + data_size)  Data segment
[0x2C + code_size + data_size .. EOF-128)  Sub-segment trailers
[EOF-128 .. EOF)                        0xF5 fill padding (128 bytes)
```

## Data Section

### Data Section Header (52 bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 1 | `flags` | Data section flags |
| 0x01 | 1 | `version` | Data section version (6) |
| 0x02 | 2 | `icalls_count` | Interface call count |
| 0x04 | 1 | `num_modules` | Module count (local + imported) |
| 0x05 | 1 | `num_class_defs` | Class definition count |
| 0x06 | 2 | `export_strings_offset` | Exported data offset |
| 0x08 | 2 | `data_bytes_offset` | Data bytes pool offset |
| 0x0A | 2 | `init_static_data_offset` | Static initializer offset |
| 0x0C | 2 | `class_defs_offset` | Class definitions offset |
| 0x0E | 2 | `type_lists_offset` | Type lists offset |
| 0x10 | 2 | `interface_refs_offset` | Interface references offset |
| 0x12 | 2 | `class_refs_offset` | Class references offset |
| 0x14 | 2 | `routine_fixups_offset` | Routine fixups offset |
| 0x16 | 2 | `static_routine_fixups_offset` | Static routine fixups offset |
| 0x18 | 2 | `virtual_routine_fixups_offset` | Virtual routine fixups offset |
| 0x1A | 2 | `class_code_fixups_offset` | Class code fixups offset |
| 0x1C | 2 | `class_data_fixups_offset` | Class data fixups offset |
| 0x1E | 2 | `fields_fixups_offset` | Fields fixups offset |
| 0x20 | 2 | `local_fields_fixups_offset` | Local fields fixups offset |
| 0x22 | 2 | `static_fields_fixups_offset` | Static fields fixups offset |
| 0x24 | 2 | `native_routines_offset` | Native routines offset |
| 0x26 | 2 | `static_size` | Total static field size |
| 0x28 | 6 | `entry1` | Entry point 1 |
| 0x2E | 6 | `entry2` | Entry point 2 |

### Data Section Stream Order

1. Class-def offset table: `num_class_defs * u16`
2. Module name offsets: `num_modules * u16`
3. Module version offsets: `num_modules * u16`
4. Module entries (module 0 = local)
5. Exported data records
6. Data-bytes pool (compressed strings)
7. Class definition records
8. Type-list table
9. Interface references
10. Class references (imports)
11. Fixup tables

### Class Definition Record (48 bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 2 | `package_offset` | Package name offset |
| 0x02 | 2 | `class_offset` | Class name offset |
| 0x04 | 1 | `superclass_module` | Superclass module ordinal |
| 0x05 | 1 | `superclass_class` | Superclass class ordinal |
| 0x06 | 2 | `static_start` | Static fields start |
| 0x08 | 2 | `clinit_offset` | Class initializer code offset |
| 0x0A | 2 | `init_offset` | Constructor code offset |
| 0x0C | 2 | `create_size` | Instance allocation size |
| 0x0E | 2 | `secure_index` | Security index |
| 0x10 | 2 | `index` | Global class index |
| 0x12 | 2 | `code_start` | Code range start |
| 0x14 | 2 | `code_end` | Code range end |
| 0x16 | 2 | `attributes` | Class attributes |
| 0x18 | 2 | `virtual_rel` | Virtual method table offset |
| 0x1A | 2 | `nonvirtual_rel` | Non-virtual method table offset |
| 0x1C | 2 | `static_rel` | Static method table offset |
| 0x1E | 2 | `field_defs_rel` | Field definitions offset |
| 0x20 | 2 | `static_field_defs_rel` | Static field definitions offset |
| 0x22 | 2 | `interfaces_rel` | Interface table offset |
| 0x24 | 2 | `field_attrs_rel` | Field attributes offset |
| 0x26 | 2 | `static_field_attrs_rel` | Static field attributes offset |

## String/Identifier Encoding

Names use a **256-entry substring dictionary** compression:

- Each byte selects a common token (e.g., `"rim"`, `"init"`, `"Exception"`)
- Byte `0xFF` is escape for literal ASCII character
- Identifiers are NUL-terminated

### Example Dictionary Entries

| Index | Token | Index | Token |
|-------|-------|-------|-------|
| 1 | "in" | 21 | "rim" |
| 2 | "et" | 22 | "net" |
| 3 | "it" | 23 | "device" |
| 4 | "init" | 46 | "." |
| 10 | "<init>" | 96 | "_" |
| 13 | "<cl" | 135 | "java" |
| 14 | "<clinit>" | 138 | "crypto" |
| 63-88 | "A"-"Z" | 178 | "cldc" |

### Encoding Example

String `"net.rim.device"` encodes as:
```
22 46 21 46 23 00
│  │  │  │  │  └── NUL terminator
│  │  │  │  └───── token 23 = "device"
│  │  │  └──────── token 46 = "."
│  │  └─────────── token 21 = "rim"
│  └────────────── token 46 = "."
└───────────────── token 22 = "net"
```

## Bytecode Instruction Set

The RIM VM is a **register-based, stack-effect virtual machine** with 32-bit word size. Instructions are single opcode byte + operands. Multi-byte operands are **big-endian**.

### Primary Opcode Table (0x00-0xFF)

#### Call/Invoke Instructions (0x00-0x0D)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x00 | `breakpoint` | 1 | Debug breakpoint (also used as NOP) |
| 0x01 | `invokevirtual` | 4 | Virtual method call (intra-module) |
| 0x02 | `invokeinterface` | 6 | Interface method call |
| 0x03 | `invokenonvirtual` | 4 | Non-virtual call |
| 0x04 | `invokenonvirtual_lib` | 5 | Non-virtual call (cross-module) |
| 0x05 | `invokespecial` | 4 | Special call (constructors) |
| 0x06 | `invokespecial_lib` | 5 | Special call (cross-module) |
| 0x07 | `invokestatic` | 4 | Static call |
| 0x08 | `invokestatic_lib` | 5 | Static call (cross-module) |
| 0x09 | `iinvokenative` | 4 | Integer native call |
| 0x0A | `invokenative` | 4 | Native call (void) |
| 0x0B | `linvokenative` | 4 | Long native call |
| 0x0C | `jumpspecial` | 3 | Tail call (intra-module) |
| 0x0D | `jumpspecial_lib` | 4 | Tail call (cross-module) |

**Key:** `_lib` suffix = cross-module call (resolved via fixup tables at install time)

#### Control Flow / Returns (0x0E-0x21)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x0E | `enter` | 1 | Method prologue |
| 0x0F | `xenter` | 1 | Exception handler entry |
| 0x12 | `synch` | 1 | Monitor enter (instance) |
| 0x13 | `synch_static` | 2 | Monitor enter (static) |
| 0x14 | `clinit_wait` | 1 | Wait for class init |
| 0x15 | `ireturn_bipush` | 2 | Return int + bipush fused |
| 0x16 | `ireturn_sipush` | 3 | Return int + sipush fused |
| 0x17 | `ireturn_iipush` | 5 | Return int + iipush fused |
| 0x18 | `ireturn` | 1 | Return int |
| 0x19 | `ireturn_field` | 2 | Return field (int) |
| 0x1B | `areturn` | 1 | Return reference |
| 0x1C | `areturn_field` | 2 | Return field (reference) |
| 0x1E | `lreturn` | 1 | Return long |
| 0x1F | `return` | 1 | Return void |
| 0x20 | `clinit_return` | 1 | Return from static initializer |

#### Constants (0x22-0x2D)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x22 | `aconst_null` | 1 | Push null reference |
| 0x23 | `iconst_0` | 1 | Push int 0 |
| 0x24 | `bipush` | 2 | Push byte (sign-extended) |
| 0x25 | `sipush` | 3 | Push short |
| 0x26 | `iipush` | 5 | Push 32-bit int |
| 0x27 | `lipush` | 9 | Push 64-bit long |
| 0x28 | `ldc` | 3 | Load constant from pool |
| 0x2A | `ldc_unicode` | 5 | Load Unicode constant |
| 0x2C | `iconst_1` | 1 | Push int 1 |
| 0x2D | `arrayinit` | 6 | Array initializer |

#### Local Variable Loads (0x31-0x46)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x31 | `iload` | 2 | Load int from local |
| 0x33 | `aload` | 2 | Load reference from local |
| 0x35 | `lload` | 2 | Load long from local |
| 0x37-0x3E | `iload_0` through `iload_7` | 1 | Load int from local 0-7 |
| 0x3F-0x46 | `aload_0` through `aload_7` | 1 | Load ref from local 0-7 |

#### Local Variable Stores (0x47-0x5E)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x47 | `istore` | 2 | Store int to local |
| 0x49 | `astore` | 2 | Store reference to local |
| 0x4B | `lstore` | 2 | Store long to local |
| 0x4C-0x53 | `istore_0` through `istore_7` | 1 | Store int to local 0-7 |
| 0x54-0x5B | `astore_0` through `astore_7` | 1 | Store ref to local 0-7 |

#### Field Access (0x5C-0x70)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x5C | `putfield_return` | 2 | Fused putfield + return |
| 0x5F | `putfield` | 2 | Store to instance field |
| 0x61 | `lputfield` | 2 | Store long to instance field |
| 0x63 | `getfield` | 2 | Load from instance field |
| 0x65 | `lgetfield` | 2 | Load long from instance field |
| 0x67 | `aload_0_getfield` | 2 | Fused aload_0 + getfield |
| 0x69 | `putstatic` | 4 | Store to static field |
| 0x6A | `putstatic_lib` | 5 | Store to static (cross-module) |
| 0x6D | `getstatic` | 4 | Load from static field |
| 0x6E | `getstatic_lib` | 5 | Load from static (cross-module) |

#### Type Conversions & Arithmetic (0x71-0x8F)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x71 | `i2b` | 1 | int to byte |
| 0x72 | `i2s` | 1 | int to short |
| 0x73 | `i2c` | 1 | int to char |
| 0x74 | `i2l` | 1 | int to long |
| 0x75 | `l2i` | 1 | long to int |
| 0x76 | `ineg` | 1 | negate int |
| 0x77 | `lneg` | 1 | negate long |
| 0x78 | `iinc` | 3 | increment local |
| 0x7A-0x8F | `iadd` through `lushr` | 1 | Standard arithmetic/bitwise ops |

#### Comparisons & Branches (0x90-0xA2)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x90 | `lcmp` | 1 | Compare longs |
| 0x91 | `if_icmpeq` | 2 | Branch if int eq |
| 0x93 | `ifeq` | 2 | Branch if zero |
| 0x9F | `ifnull` | 2 | Branch if null |
| 0xA0 | `ifnonnull` | 2 | Branch if non-null |
| 0xA1 | `goto` | 2 | Unconditional branch (byte) |
| 0xA2 | `goto_w` | 3 | Unconditional branch (word) |

#### Arrays & Objects (0xA3-0xD5)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0xA5 | `newarray` | 2 | New primitive array |
| 0xA6 | `multianewarray` | 4 | Multi-dimensional array |
| 0xAC-0xB7 | `baload` through `lastore` | 1 | Array load/store |
| 0xB8 | `new` | 2 | New object (intra-module) |
| 0xB9 | `new_lib` | 3 | New object (cross-module) |
| 0xBA | `clinit` | 2 | Class init (intra-module) |
| 0xBB | `clinit_lib` | 3 | Class init (cross-module) |
| 0xBC | `athrow` | 1 | Throw exception |
| 0xBE | `instanceof` | 2 | Type check |
| 0xC1 | `checkcast` | 2 | Type cast |
| 0xC3 | `checkcastbranch` | 4 | Check cast + branch |
| 0xCC | `monitorenter` | 1 | Monitor enter |
| 0xCD | `monitorexit` | 1 | Monitor exit |

#### Special Operations (0xD7-0xDF)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0xD7 | `isreal` | 1 | Check if value is real (non-null) |
| 0xD8 | `PREFIX` | 1 | Extended opcode prefix (float page) |
| 0xD9 | `stringlength` | 1 | String length (fused) |
| 0xDA | `stringaload` | 1 | String char load (fused) |
| 0xDB | `invokestaticqc` | 4 | Quick static call |
| 0xDC | `invokestaticqc_lib` | 5 | Quick static call (cross-module) |
| 0xDD | `enter_narrow` | 1 | Narrow method entry |
| 0xDE | `invokevirtual_short` | 2 | Short virtual call |
| 0xDF | `ldc_nullstr` | 1 | Load null string constant |

### Extended Opcodes (0xD8 prefix, effective 0x100-0x11A)

| Opcode | Name | Size | Description |
|--------|------|------|-------------|
| 0x100 | `fadd` | 2 | Float add |
| 0x101 | `dadd` | 2 | Double add |
| 0x102 | `fsub` | 2 | Float subtract |
| 0x103 | `dsub` | 2 | Double subtract |
| 0x104 | `fmul` | 2 | Float multiply |
| 0x105 | `dmul` | 2 | Double multiply |
| 0x106 | `fdiv` | 2 | Float divide |
| 0x107 | `ddiv` | 2 | Double divide |
| 0x108-0x109 | `frem`/`drem` | 2 | Float/double remainder |
| 0x10A-0x10B | `fneg`/`dneg` | 2 | Float/double negate |
| 0x10C-0x111 | `i2f`, `i2d`, `l2f`, `l2d`, `f2i`, `f2l` | 2 | Type conversions |
| 0x112-0x117 | `f2d`, `d2i`, `d2l`, `d2f`, `fcmpl`, `fcmpg` | 2 | Conversions/comparisons |
| 0x118-0x119 | `dcmpl`/`dcmpg` | 2 | Double comparisons |

### Unidentified Opcodes (OS 7.1+)

These opcodes appear in newer BB7 modules but semantics are unknown:
- `D8 1D` (0x11D)
- `D8 1E` (0x11E)
- `D8 20` (0x120)
- `D8 21` (0x121)

## Variable-Length Instructions

### tableswitch (0x2F)

```
u16 count
s32 default
s16 labels[count]   (signed byte offsets relative to instruction)
```

### lookupswitch_short (0xA3)

```
u16 count
(s16 key, s16 label)[count]
s16 default
```

### lookupswitch (0xA4)

```
u16 count
(s32 key, s16 label)[count]
s16 default
```

## Fused Instructions

RIM's compiler fuses common patterns for efficiency:

| Fused Opcode | Equivalent |
|--------------|------------|
| `aload_0_getfield` (0x67) | aload_0 + getfield |
| `putfield_return` (0x5C) | putfield + return |
| `ireturn_bipush` (0x15) | ireturn + bipush |
| `stringlength` (0xD9) | string.length() |
| `stringaload` (0xDA) | string.charAt() |

## Exception Tables

Exception handlers stored as 8-byte entries:

```
[start_pc: u16][end_pc: u16][handler_pc: u16][module: u8][class_idx: u8]
```

- All PCs are absolute code-segment offsets
- `end` is exclusive
- `0xFFFF` terminator
- `(0xFF, 0xFF)` for module + class = catch-all (finally)

## Fixup / Relocation Tables

Cross-module references resolved at install/link time:

| Table | Purpose | Entry Format |
|-------|---------|--------------|
| `routine_fixups` | Method call relocations | MemberRef |
| `static_routine_fixups` | Static method relocations | MemberRef |
| `virtual_routine_fixups` | Virtual method relocations | MemberRef |
| `class_code_fixups` | Class reference relocations | Class-ref + use-sites |
| `fields_fixups` | Field reference relocations | MemberRef |
| `local_fields_fixups` | Cross-module field relocations | MemberRefLocal |
| `static_fields_fixups` | Static field relocations | MemberRef |

### MemberRef Format

```
u16 count
(class-ref-data-offset: u16 + use-sites)[count]
```

### MemberRefLocal Format

Same as MemberRef but:
- Uses `selfClassOrdinal + fieldOrdinal` encoding
- **NOT** 2-byte-aligned (critical implementation detail)

## Cross-Module Resolution Model

```
Intra-module refs:
  - Encoded directly as LE code offsets / slots / field addresses
  - NOT in fixup tables

Cross-module refs (_lib opcodes):
  - Resolved at install time via fixup tables
  - Fixup maps use-site PC+1 to a Ref (class + member ordinal)
```

## Opcode Frequency Analysis

Most common opcodes (from `net_rim_cldc.cod`):

| Opcode | Name | Count | Description |
|--------|------|-------|-------------|
| 0x00 | breakpoint/nop | 3320 | Padding/alignment |
| 0x67 | aload_0_getfield | 2364 | Most common fused instruction |
| 0x01 | invokevirtual | 2073 | Virtual method calls |
| 0x40 | aload_1 | 1973 | Load ref from local 1 |
| 0x05 | invokespecial | 1779 | Special calls (constructors) |
| 0x3F | aload_0 | 1592 | Load ref from local 0 |
| 0x5F | putfield | 863 | Store to instance field |
| 0xDE | invokevirtual_short | 762 | Short virtual call |

## Known Tools

| Tool | Language | Description |
|------|----------|-------------|
| [bb-tools/cod2jar](https://github.com/waltermin/bb-tools) | Rust | COD to JAR transpiler (~96-99% success) |
| [coddec](https://github.com/george-hopkins/coddec) | Java | Original BlackBerry disassembler (2008) |
| VineFlower | Java | Java decompiler for generated JARs |

## Usage Example

```bash
# Install cod2jar
git clone https://github.com/waltermin/bb-tools.git
cd bb-tools
cargo build -p cod2jar --release

# Convert COD to JAR
./target/release/cod2jar \
  --debug-dir /path/to/debug/ \
  mymodule.cod \
  -o output.jar

# Decompile JAR to Java source
java -jar vineflower.jar output.jar -d output/
```

---

*Format documentation based on reverse engineering of BlackBerry OS 7.1.0.318 COD files and the bb-tools project.*
