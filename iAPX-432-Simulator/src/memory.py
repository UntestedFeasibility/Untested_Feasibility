"""
iAPX 432 Memory Module

Implements the memory subsystem with linear address space,
segment simulation, and basic protection.
"""

from typing import Dict, Optional, Tuple
from enum import IntEnum


class SegmentType(IntEnum):
    """Memory segment types"""
    NULL = 0x00
    INSTRUCTION = 0x01
    DATA = 0x02
    DATA_RW = 0x03
    STACK = 0x04
    SYSTEM = 0x05


class Segment:
    """Memory segment with protection"""
    
    def __init__(self, seg_type: SegmentType, base: int, size: int, rights: int = 0):
        self.type = seg_type
        self.base = base
        self.size = size
        self.rights = rights  # Bitmask of allowed operations
        self.data = [0] * size
        self.initialized = True
    
    def read(self, offset: int) -> Optional[int]:
        """Read a byte from segment"""
        if offset < 0 or offset >= self.size:
            return None
        return self.data[offset]
    
    def write(self, offset: int, value: int) -> bool:
        """Write a byte to segment"""
        if offset < 0 or offset >= self.size:
            return False
        if not (self.rights & 0x02):  # Check WRITE bit
            return False
        self.data[offset] = value & 0xFF
        return True
    
    def read_word(self, offset: int) -> Optional[int]:
        """Read a 32-bit word from segment"""
        if offset < 0 or offset + 3 >= self.size:
            return None
        word = (self.data[offset] |
                (self.data[offset + 1] << 8) |
                (self.data[offset + 2] << 16) |
                (self.data[offset + 3] << 24))
        return word
    
    def write_word(self, offset: int, value: int) -> bool:
        """Write a 32-bit word to segment"""
        if offset < 0 or offset + 3 >= self.size:
            return False
        if not (self.rights & 0x02):  # Check WRITE bit
            return False
        self.data[offset] = value & 0xFF
        self.data[offset + 1] = (value >> 8) & 0xFF
        self.data[offset + 2] = (value >> 16) & 0xFF
        self.data[offset + 3] = (value >> 24) & 0xFF
        return True
    
    def contains(self, address: int) -> bool:
        """Check if address is within this segment"""
        return self.base <= address < self.base + self.size
    
    def __repr__(self) -> str:
        return (f"Segment(type={self.type.name}, base={self.base:#x}, "
                f"size={self.size:#x}, rights={self.rights:#06x})")


class Memory:
    """
    iAPX 432 Memory System
    
    Simplified linear memory model for educational purposes.
    In the real 432, memory was segmented with hardware protection.
    """
    
    # Memory layout constants
    SYSTEM_AREA_SIZE = 0x1000      # 4KB for system structures
    STACK_AREA_SIZE = 0x10000      # 64KB for stack
    CODE_AREA_SIZE = 0x100000      # 1MB for code
    DATA_AREA_SIZE = 0x100000      # 1MB for data
    TOTAL_MEMORY = 0x200000        # 2MB total
    
    def __init__(self, total_size: int = None):
        """
        Initialize memory system
        
        Args:
            total_size: Total memory size in bytes (default: 2MB)
        """
        self.total_size = total_size or self.TOTAL_MEMORY
        self.memory = [0] * self.total_size
        
        # Segment table
        self.segments: Dict[int, Segment] = {}
        self.next_segment_id = 1
        
        # Memory map
        self.system_base = 0
        self.code_base = self.SYSTEM_AREA_SIZE
        self.data_base = self.code_base + self.CODE_AREA_SIZE
        self.stack_base = self.data_base + self.DATA_AREA_SIZE
        self.heap_base = self.stack_base + self.STACK_AREA_SIZE
        
        # Initialize default segments
        self._init_default_segments()
    
    def _init_default_segments(self):
        """Initialize default memory segments"""
        # System segment (read-only)
        self.create_segment(
            SegmentType.SYSTEM,
            self.system_base,
            self.SYSTEM_AREA_SIZE,
            rights=0x01  # READ only
        )
        
        # Code segment (execute only)
        self.create_segment(
            SegmentType.INSTRUCTION,
            self.code_base,
            self.CODE_AREA_SIZE,
            rights=0x04  # EXECUTE only
        )
        
        # Data segment (read-write)
        self.create_segment(
            SegmentType.DATA_RW,
            self.data_base,
            self.DATA_AREA_SIZE,
            rights=0x03  # READ + WRITE
        )
        
        # Stack segment (read-write)
        self.create_segment(
            SegmentType.STACK,
            self.stack_base,
            self.STACK_AREA_SIZE,
            rights=0x03  # READ + WRITE
        )
    
    def create_segment(self, seg_type: SegmentType, base: int, 
                       size: int, rights: int = 0) -> int:
        """
        Create a new memory segment
        
        Args:
            seg_type: Type of segment
            base: Base address
            size: Size in bytes
            rights: Access rights bitmask
            
        Returns:
            Segment ID
        """
        seg_id = self.next_segment_id
        self.next_segment_id += 1
        
        self.segments[seg_id] = Segment(seg_type, base, size, rights)
        return seg_id
    
    def get_segment(self, seg_id: int) -> Optional[Segment]:
        """Get segment by ID"""
        return self.segments.get(seg_id)
    
    def find_segment(self, address: int) -> Optional[Tuple[int, Segment]]:
        """Find segment containing address"""
        for seg_id, segment in self.segments.items():
            if segment.contains(address):
                return (seg_id, segment)
        return None
    
    def read_byte(self, address: int) -> Optional[int]:
        """
        Read a byte from memory
        
        Args:
            address: Memory address
            
        Returns:
            Byte value or None if invalid address
        """
        if address < 0 or address >= self.total_size:
            return None
        
        # Find containing segment
        result = self.find_segment(address)
        if result is None:
            return None
        
        seg_id, segment = result
        offset = address - segment.base
        return segment.read(offset)
    
    def write_byte(self, address: int, value: int) -> bool:
        """
        Write a byte to memory
        
        Args:
            address: Memory address
            value: Byte value to write
            
        Returns:
            True if successful, False otherwise
        """
        if address < 0 or address >= self.total_size:
            return False
        
        # Find containing segment
        result = self.find_segment(address)
        if result is None:
            return False
        
        seg_id, segment = result
        offset = address - segment.base
        return segment.write(offset, value)
    
    def read_word(self, address: int) -> int:
        """
        Read a 32-bit word from memory
        
        Args:
            address: Memory address (should be word-aligned)
            
        Returns:
            32-bit word value
        """
        if address < 0 or address + 3 >= self.total_size:
            return 0
        
        # Read 4 bytes and combine (little-endian)
        b0 = self.read_byte(address) or 0
        b1 = self.read_byte(address + 1) or 0
        b2 = self.read_byte(address + 2) or 0
        b3 = self.read_byte(address + 3) or 0
        
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
    
    def write_word(self, address: int, value: int) -> bool:
        """
        Write a 32-bit word to memory
        
        Args:
            address: Memory address (should be word-aligned)
            value: 32-bit word to write
            
        Returns:
            True if successful, False otherwise
        """
        if address < 0 or address + 3 >= self.total_size:
            return False
        
        # Write 4 bytes (little-endian)
        success = True
        success &= self.write_byte(address, value & 0xFF)
        success &= self.write_byte(address + 1, (value >> 8) & 0xFF)
        success &= self.write_byte(address + 2, (value >> 16) & 0xFF)
        success &= self.write_byte(address + 3, (value >> 24) & 0xFF)
        
        return success
    
    def read_string(self, address: int, max_length: int = 256) -> str:
        """
        Read a null-terminated string from memory
        
        Args:
            address: Starting address
            max_length: Maximum string length
            
        Returns:
            String read from memory
        """
        chars = []
        for i in range(max_length):
            byte = self.read_byte(address + i)
            if byte is None or byte == 0:
                break
            chars.append(chr(byte))
        return ''.join(chars)
    
    def write_string(self, address: int, string: str) -> bool:
        """
        Write a string to memory (null-terminated)
        
        Args:
            address: Starting address
            string: String to write
            
        Returns:
            True if successful
        """
        for i, char in enumerate(string):
            if not self.write_byte(address + i, ord(char)):
                return False
        # Write null terminator
        return self.write_byte(address + len(string), 0)
    
    def get_stack_base(self) -> int:
        """Get base address of stack segment"""
        return self.stack_base
    
    def get_code_base(self) -> int:
        """Get base address of code segment"""
        return self.code_base
    
    def get_data_base(self) -> int:
        """Get base address of data segment"""
        return self.data_base
    
    def dump(self, address: int, length: int) -> str:
        """
        Dump memory contents as hex string
        
        Args:
            address: Starting address
            length: Number of bytes to dump
            
        Returns:
            Hex dump string
        """
        lines = []
        for offset in range(0, length, 16):
            hex_chars = []
            ascii_chars = []
            
            for i in range(16):
                if offset + i < length:
                    byte = self.read_byte(address + offset + i)
                    if byte is not None:
                        hex_chars.append(f"{byte:02x}")
                        ascii_chars.append(chr(byte) if 32 <= byte < 127 else '.')
                    else:
                        hex_chars.append("??")
                        ascii_chars.append('?')
                else:
                    hex_chars.append("  ")
                    ascii_chars.append(' ')
            
            hex_str = ' '.join(hex_chars)
            ascii_str = ''.join(ascii_chars)
            lines.append(f"{address + offset:08x}  {hex_str}  |{ascii_str}|")
        
        return '\n'.join(lines)
    
    def __repr__(self) -> str:
        return (f"Memory(total={self.total_size:#x}, segments={len(self.segments)}, "
                f"next_seg_id={self.next_segment_id})")
