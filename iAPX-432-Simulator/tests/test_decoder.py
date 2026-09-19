"""
Unit tests for iAPX 432 Instruction Decoder
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.decoder import (
    InstructionDecoder, DecodedInstruction, ReferenceField,
    Opcode, AccessMode
)


def test_decode_nop():
    """Test NOP instruction decoding"""
    decoder = InstructionDecoder()
    # NOP = 0x00
    instruction_bits = 0x00
    result = decoder.decode(instruction_bits)
    assert result.opcode == Opcode.NOP
    print("PASS: test_decode_nop")


def test_decode_halt():
    """Test HALT instruction decoding"""
    decoder = InstructionDecoder()
    # HALT = 0x1F (5 bits)
    # Format: class(4) + format(3) + opcode(5)
    instruction_bits = 0x1F << 7  # Shift opcode to correct position
    result = decoder.decode(instruction_bits)
    assert result.opcode == Opcode.HALT
    print("PASS: test_decode_halt")


def test_decode_add():
    """Test ADD instruction decoding"""
    decoder = InstructionDecoder()
    # ADD = 0x03
    instruction_bits = 0x03 << 7
    result = decoder.decode(instruction_bits)
    assert result.opcode == Opcode.ADD
    print("PASS: test_decode_add")


def test_reference_field():
    """Test reference field decoding"""
    decoder = InstructionDecoder()
    
    # Create a reference field with DIRECT mode
    ref = ReferenceField()
    ref.access_mode = AccessMode.DIRECT
    ref.access_selector = 0x05
    ref.displacement = 0x10
    
    assert ref.access_mode == AccessMode.DIRECT
    assert ref.access_selector == 0x05
    assert ref.displacement == 0x10
    print("PASS: test_reference_field")


def test_instruction_size():
    """Test instruction size calculation"""
    decoder = InstructionDecoder()
    
    # No references
    size = decoder.get_instruction_size(0, 0, 0)
    assert size == 12  # 4 + 3 + 0 + 5
    
    # One reference
    size = decoder.get_instruction_size(0, 1, 1)
    assert size == 22  # 4 + 3 + 10 + 5
    
    # Two references
    size = decoder.get_instruction_size(0, 2, 2)
    assert size == 32  # 4 + 3 + 20 + 5
    
    print("PASS: test_instruction_size")


def test_opcode_names():
    """Test opcode name lookup"""
    decoder = InstructionDecoder()
    
    assert decoder.get_opcode_name(Opcode.NOP) == "NOP"
    assert decoder.get_opcode_name(Opcode.HALT) == "HALT"
    assert decoder.get_opcode_name(Opcode.ADD) == "ADD"
    assert decoder.get_opcode_name(Opcode.LOAD) == "LOAD"
    assert decoder.get_opcode_name(Opcode.STORE) == "STORE"
    
    print("PASS: test_opcode_names")


def test_class_field_operand_counts():
    """Test class field operand count calculation"""
    decoder = InstructionDecoder()
    
    # Class 0: 0 operands
    assert decoder.CLASS_OPERAND_COUNTS[0] == (0, [])
    
    # Class 1: 1 word operand
    assert decoder.CLASS_OPERAND_COUNTS[1] == (1, ['word'])
    
    # Class 2: 2 word operands
    assert decoder.CLASS_OPERAND_COUNTS[2] == (2, ['word', 'word'])
    
    print("PASS: test_class_field_operand_counts")


def test_access_modes():
    """Test access mode values"""
    assert AccessMode.DIRECT.value == 0
    assert AccessMode.INDIRECT.value == 1
    assert AccessMode.STACK.value == 2
    assert AccessMode.RELATIVE.value == 3
    assert AccessMode.INDEXED.value == 4
    
    print("PASS: test_access_modes")


if __name__ == '__main__':
    print("Running decoder tests...")
    test_decode_nop()
    test_decode_halt()
    test_decode_add()
    test_reference_field()
    test_instruction_size()
    test_opcode_names()
    test_class_field_operand_counts()
    test_access_modes()
    print("\nAll decoder tests passed!")
