"""
iAPX 432 Instruction Decoder

Implements the variable-length bit-level instruction decoding
for the iAPX 432 instruction set.
"""

from enum import IntEnum
from typing import Tuple, Optional, List


class Opcode(IntEnum):
    """iAPX 432 Opcodes (5-bit primary)"""
    NOP = 0x00
    LOAD = 0x01
    STORE = 0x02
    ADD = 0x03
    SUB = 0x04
    MUL = 0x05
    DIV = 0x06
    AND = 0x07
    OR = 0x08
    XOR = 0x09
    NOT = 0x0A
    SHIFT = 0x0B
    COMPARE = 0x0C
    BRANCH = 0x0D
    BRANCHEQ = 0x0E
    BRANCHNE = 0x0F
    PUSH = 0x10
    POP = 0x11
    CALL = 0x12
    RETURN = 0x13
    CREATE = 0x14
    DESTROY = 0x15
    CHECKRIGHTS = 0x16
    DOMAINSWITCH = 0x17
    CHLOAD = 0x18
    CHSTORE = 0x19
    CHCOMPARE = 0x1A
    GETAD = 0x1B
    PUTAD = 0x1C
    GETTYPE = 0x1D
    SETTYPE = 0x1E
    HALT = 0x1F


class AccessMode(IntEnum):
    """Reference field access modes"""
    DIRECT = 0x00
    INDIRECT = 0x01
    STACK = 0x02
    RELATIVE = 0x03
    INDEXED = 0x04
    DOUBLE_INDIRECT = 0x05
    TOP_OF_STACK = 0x06
    RESERVED = 0x07


class ReferenceField:
    """Parsed reference field from instruction"""
    
    def __init__(self):
        self.access_mode: AccessMode = AccessMode.DIRECT
        self.displacement: int = 0
        self.access_selector: int = 0
    
    def __repr__(self) -> str:
        return f"Ref(mode={self.access_mode.name}, disp={self.displacement:#x}, sel={self.access_selector:#x})"


class DecodedInstruction:
    """Fully decoded instruction"""
    
    def __init__(self):
        self.class_field: int = 0
        self.format_field: int = 0
        self.references: List[ReferenceField] = []
        self.opcode: Opcode = Opcode.NOP
        self.immediate: int = 0
        self.total_bits: int = 0
        self.num_operands: int = 0
        self.operand_types: List[str] = []
        self.operand_count_from_class: int = 0
    
    def __repr__(self) -> str:
        return f"Instruction({self.opcode.name}, operands={self.num_operands}, bits={self.total_bits})"


class InstructionDecoder:
    """
    iAPX 432 Variable-Length Instruction Decoder
    
    The iAPX 432 uses bit-level instruction encoding.
    Instructions can start at any bit boundary.
    """
    
    CLASS_OPERAND_COUNTS = {
        0: (0, []),
        1: (1, ['word']),
        2: (2, ['word', 'word']),
        3: (3, ['word', 'word', 'word']),
        4: (1, ['byte']),
        5: (2, ['byte', 'word']),
        6: (2, ['byte', 'byte']),
        7: (3, ['byte', 'byte', 'byte']),
    }
    
    def __init__(self):
        pass
    
    def decode(self, instruction_bits: int, bit_offset: int = 0) -> DecodedInstruction:
        """Decode an instruction from bits"""
        result = DecodedInstruction()
        
        # Extract class field (4 bits)
        class_field = (instruction_bits >> bit_offset) & 0xF
        result.class_field = class_field
        bit_offset += 4
        
        # Parse class field
        if class_field < 8:
            num_ops, op_types = self.CLASS_OPERAND_COUNTS.get(class_field, (0, []))
            result.num_operands = num_ops
            result.operand_types = op_types
            result.operand_count_from_class = num_ops
        elif class_field == 8:
            extended = (instruction_bits >> bit_offset) & 0xF
            bit_offset += 4
            result.num_operands = (extended % 3) + 1
            result.operand_types = ['word'] * result.num_operands
            result.operand_count_from_class = result.num_operands
        else:
            result.num_operands = 1
            result.operand_types = ['object']
            result.operand_count_from_class = 1
        
        # Extract format field (3 bits)
        format_field = (instruction_bits >> bit_offset) & 0x7
        result.format_field = format_field
        bit_offset += 3
        
        explicit_count = format_field & 0x3
        
        # Extract reference fields
        for i in range(explicit_count):
            ref = self._decode_reference(instruction_bits, bit_offset)
            result.references.append(ref)
            bit_offset += 10
        
        # Extract opcode field (5 bits)
        opcode_bits = (instruction_bits >> bit_offset) & 0x1F
        try:
            result.opcode = Opcode(opcode_bits)
        except ValueError:
            result.opcode = Opcode.NOP
        bit_offset += 5
        
        result.total_bits = 4 + 3 + (explicit_count * 10) + 5
        
        return result
    
    def _decode_reference(self, instruction_bits: int, bit_offset: int) -> ReferenceField:
        """Decode a single reference field"""
        ref = ReferenceField()
        
        mode_bits = (instruction_bits >> bit_offset) & 0x7
        try:
            ref.access_mode = AccessMode(mode_bits)
        except ValueError:
            ref.access_mode = AccessMode.DIRECT
        bit_offset += 3
        
        ref.access_selector = (instruction_bits >> bit_offset) & 0xF
        bit_offset += 4
        
        ref.displacement = (instruction_bits >> bit_offset) & 0x7
        
        return ref
    
    def get_opcode_name(self, opcode: Opcode) -> str:
        """Get human-readable opcode name"""
        return opcode.name
    
    def get_instruction_size(self, class_field: int, format_field: int, 
                            num_references: int) -> int:
        """Calculate instruction size in bits"""
        size = 4 + 3 + (num_references * 10) + 5
        return size
