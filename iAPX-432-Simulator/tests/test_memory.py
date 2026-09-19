"""
Unit tests for iAPX 432 Memory System
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.memory import Memory, Segment, SegmentType


def test_memory_creation():
    """Test memory initialization"""
    memory = Memory()
    
    assert memory.total_size == 0x200000  # 2MB
    assert len(memory.segments) > 0
    
    print("PASS: test_memory_creation")


def test_read_write_byte():
    """Test byte read/write operations"""
    memory = Memory()
    
    # Write byte to data segment
    address = memory.get_data_base() + 100
    memory.write_byte(address, 0x42)
    
    # Read it back
    value = memory.read_byte(address)
    assert value == 0x42
    
    print("PASS: test_read_write_byte")


def test_read_write_word():
    """Test word read/write operations"""
    memory = Memory()
    
    # Write word to data segment
    address = memory.get_data_base() + 200
    memory.write_word(address, 0xDEADBEEF)
    
    # Read it back
    value = memory.read_word(address)
    assert value == 0xDEADBEEF
    
    print("PASS: test_read_write_word")


def test_read_write_string():
    """Test string read/write operations"""
    memory = Memory()
    
    # Write string
    address = memory.get_data_base() + 300
    memory.write_string(address, "Hello, iAPX 432!")
    
    # Read it back
    string = memory.read_string(address)
    assert string == "Hello, iAPX 432!"
    
    print("PASS: test_read_write_string")


def test_segment_creation():
    """Test segment creation"""
    memory = Memory()
    
    # Create new segment
    seg_id = memory.create_segment(
        SegmentType.DATA_RW,
        0x100000,
        0x10000,
        rights=0x03
    )
    
    assert seg_id > 0
    segment = memory.get_segment(seg_id)
    assert segment is not None
    assert segment.base == 0x100000
    assert segment.size == 0x10000
    
    print("PASS: test_segment_creation")


def test_segment_protection():
    """Test segment protection"""
    memory = Memory()
    
    # Create read-only segment
    seg_id = memory.create_segment(
        SegmentType.INSTRUCTION,
        0x50000,
        0x1000,
        rights=0x04  # Execute only
    )
    
    segment = memory.get_segment(seg_id)
    
    # Write should fail
    success = segment.write(0, 0x42)
    assert success is False
    
    print("PASS: test_segment_protection")


def test_find_segment():
    """Test segment lookup by address"""
    memory = Memory()
    
    # Find data segment
    data_base = memory.get_data_base()
    result = memory.find_segment(data_base)
    
    assert result is not None
    seg_id, segment = result
    assert segment.type == SegmentType.DATA_RW
    
    print("PASS: test_find_segment")


def test_memory_dump():
    """Test memory dump output"""
    memory = Memory()
    
    # Write some data
    address = memory.get_data_base()
    memory.write_byte(address, 0x41)  # 'A'
    memory.write_byte(address + 1, 0x42)  # 'B'
    memory.write_byte(address + 2, 0x43)  # 'C'
    
    # Dump
    dump = memory.dump(address, 16)
    assert "41 42 43" in dump
    
    print("PASS: test_memory_dump")


def test_invalid_address():
    """Test invalid address handling"""
    memory = Memory()
    
    # Read from invalid address
    value = memory.read_byte(-1)
    assert value is None
    
    value = memory.read_byte(memory.total_size + 1)
    assert value is None
    
    # Write to invalid address
    success = memory.write_byte(-1, 0x42)
    assert success is False
    
    print("PASS: test_invalid_address")


def test_segment_contains():
    """Test segment address containment check"""
    memory = Memory()
    
    # Create segment
    seg_id = memory.create_segment(
        SegmentType.DATA_RW,
        0x100000,
        0x1000,
        rights=0x03
    )
    
    segment = memory.get_segment(seg_id)
    
    # Test addresses
    assert segment.contains(0x100000) is True
    assert segment.contains(0x100FFF) is True
    assert segment.contains(0x101000) is False
    assert segment.contains(0x0FFFFF) is False
    
    print("PASS: test_segment_contains")


if __name__ == '__main__':
    print("Running memory tests...")
    test_memory_creation()
    test_read_write_byte()
    test_read_write_word()
    test_read_write_string()
    test_segment_creation()
    test_segment_protection()
    test_find_segment()
    test_memory_dump()
    test_invalid_address()
    test_segment_contains()
    print("\nAll memory tests passed!")
