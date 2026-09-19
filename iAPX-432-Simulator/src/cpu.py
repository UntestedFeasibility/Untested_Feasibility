"""
iAPX 432 CPU Module

Implements the core CPU components including registers,
operand stack, and pipeline stages.
"""

from typing import List, Optional


class Registers:
    """
    iAPX 432 CPU Registers
    
    The 432 uses a stack architecture - no general purpose registers.
    Only essential control registers are exposed.
    """
    
    def __init__(self):
        # Program Counter (bit addressable, but we use byte addresses)
        self.pc: int = 0
        
        # Stack Pointer (byte address)
        self.sp: int = 0
        
        # Base Pointer (byte address)
        self.bp: int = 0
        
        # Condition flags
        self.flags: int = 0
        
        # Status register
        self.status: int = 0
        
        # Current context pointer
        self.context_ptr: int = 0
        
        # Current domain pointer
        self.domain_ptr: int = 0
        
        # Instruction register (current instruction bits)
        self.ir: int = 0
        
        # Instruction length in bits
        self.ir_length: int = 0
    
    def reset(self):
        """Reset all registers to initial state"""
        self.pc = 0
        self.sp = 0
        self.bp = 0
        self.flags = 0
        self.status = 0
        self.context_ptr = 0
        self.domain_ptr = 0
        self.ir = 0
        self.ir_length = 0
    
    def set_flag(self, flag: int, value: bool):
        """Set a condition flag"""
        if value:
            self.flags |= (1 << flag)
        else:
            self.flags &= ~(1 << flag)
    
    def get_flag(self, flag: int) -> bool:
        """Get a condition flag"""
        return bool(self.flags & (1 << flag))
    
    def __repr__(self) -> str:
        return (f"Registers(PC={self.pc:#x}, SP={self.sp:#x}, "
                f"BP={self.bp:#x}, Flags={self.flags:#010x})")


class OperandStack:
    """
    iAPX 432 Operand Stack
    
    All arithmetic and logical operations use the operand stack.
    The stack grows toward higher addresses.
    """
    
    def __init__(self, capacity: int = 1024):
        self.capacity = capacity  # In bytes
        self.memory: List[int] = [0] * capacity
        self.base: int = 0
        self.pointer: int = 0  # Points to top of stack
        self.size: int = 0     # Current number of items (not bytes)
    
    def reset(self, base_address: int = 0):
        """Reset stack to initial state"""
        self.base = base_address
        self.pointer = base_address
        self.size = 0
        self.memory = [0] * self.capacity
    
    def push(self, value: int) -> bool:
        """
        Push a value onto the stack
        
        Args:
            value: 32-bit integer to push
            
        Returns:
            True if successful, False if stack overflow
        """
        if self.size >= self.capacity // 4:  # 4 bytes per word
            return False  # Stack overflow
        
        self.memory[self.pointer] = value & 0xFFFFFFFF
        self.pointer += 1
        self.size += 1
        return True
    
    def pop(self) -> Optional[int]:
        """
        Pop a value from the stack
        
        Returns:
            Value popped, or None if stack underflow
        """
        if self.size == 0:
            return None  # Stack underflow
        
        self.pointer -= 1
        self.size -= 1
        return self.memory[self.pointer]
    
    def peek(self) -> Optional[int]:
        """
        Peek at the top of stack without removing
        
        Returns:
            Top value, or None if empty
        """
        if self.size == 0:
            return None
        return self.memory[self.pointer - 1]
    
    def is_empty(self) -> bool:
        """Check if stack is empty"""
        return self.size == 0
    
    def is_full(self) -> bool:
        """Check if stack is full"""
        return self.size >= self.capacity // 4
    
    def get_size(self) -> int:
        """Get number of items on stack"""
        return self.size
    
    def __repr__(self) -> str:
        top = self.peek() if not self.is_empty() else "empty"
        return f"Stack(size={self.size}, top={top})"


class CPU:
    """
    iAPX 432 CPU
    
    Main CPU class containing registers, operand stack,
    and control logic.
    """
    
    def __init__(self):
        self.registers = Registers()
        self.stack = OperandStack()
        
        # Pipeline state
        self.halted = False
        self.cycle_count = 0
        
        # Memory reference (set during initialization)
        self.memory = None
        
        # Current instruction being executed
        self.current_instruction = None
    
    def initialize(self, memory):
        """
        Initialize CPU with memory reference
        
        Args:
            memory: Memory instance for the system
        """
        self.memory = memory
        
        # Set up stack
        stack_base = memory.get_stack_base()
        self.stack.reset(stack_base)
        self.registers.sp = stack_base
        self.registers.bp = stack_base
    
    def reset(self):
        """Reset CPU to initial state"""
        self.registers.reset()
        if self.memory:
            stack_base = self.memory.get_stack_base()
            self.stack.reset(stack_base)
            self.registers.sp = stack_base
            self.registers.bp = stack_base
        self.halted = False
        self.cycle_count = 0
    
    def fetch_instruction(self) -> int:
        """
        Fetch instruction from memory at current PC
        
        Returns:
            Instruction bits
        """
        if self.memory is None:
            return 0
        
        # Read a word from memory at PC
        word = self.memory.read_word(self.registers.pc)
        return word
    
    def increment_pc(self, bits: int):
        """
        Increment program counter by specified bits
        
        Args:
            bits: Number of bits to advance
        """
        # Convert bits to bytes (round up)
        bytes_to_advance = (bits + 7) // 8
        self.registers.pc += bytes_to_advance
    
    def push_stack(self, value: int) -> bool:
        """Push value onto operand stack"""
        result = self.stack.push(value)
        if result:
            self.registers.sp = self.stack.pointer
        return result
    
    def pop_stack(self) -> Optional[int]:
        """Pop value from operand stack"""
        value = self.stack.pop()
        if value is not None:
            self.registers.sp = self.stack.pointer
        return value
    
    def peek_stack(self) -> Optional[int]:
        """Peek at top of stack"""
        return self.stack.peek()
    
    def set_condition(self, result: int):
        """
        Set condition flags based on operation result
        
        Args:
            result: Result of last operation
        """
        # Zero flag
        self.registers.set_flag(0, result == 0)
        # Negative flag
        self.registers.set_flag(1, result < 0)
        # Overflow flag (simplified)
        self.registers.set_flag(2, False)
        # Carry flag (simplified)
        self.registers.set_flag(3, False)
    
    def execute_cycle(self) -> bool:
        """
        Execute one CPU cycle
        
        Returns:
            True if execution continues, False if halted
        """
        if self.halted:
            return False
        
        self.cycle_count += 1
        
        # Fetch instruction
        instruction_bits = self.fetch_instruction()
        
        # Instruction will be decoded and executed by ExecutionUnit
        # This is just the fetch phase
        
        return True
    
    def halt(self):
        """Halt CPU execution"""
        self.halted = True
    
    def get_state(self) -> dict:
        """Get current CPU state as dictionary"""
        return {
            'pc': self.registers.pc,
            'sp': self.registers.sp,
            'bp': self.registers.bp,
            'flags': self.registers.flags,
            'halted': self.halted,
            'cycles': self.cycle_count,
            'stack_size': self.stack.get_size(),
        }
    
    def __repr__(self) -> str:
        return (f"CPU({self.registers}, {self.stack}, "
                f"halted={self.halted}, cycles={self.cycle_count})")
