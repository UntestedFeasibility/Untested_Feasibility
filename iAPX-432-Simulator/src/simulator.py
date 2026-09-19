"""
iAPX 432 Main Simulator

Top-level simulator class that ties together all components.
"""

import sys
from typing import Optional, List
from .cpu import CPU
from .memory import Memory
from .decoder import InstructionDecoder, DecodedInstruction
from .execution import ExecutionUnit
from .objects import ObjectTable, Domain, Context


class Simulator:
    """
    iAPX 432 Simulator
    
    Educational simulator of the Intel iAPX 432
    32-bit capability-based processor.
    """
    
    def __init__(self, memory_size: int = 0x200000):
        """
        Initialize simulator
        
        Args:
            memory_size: Total memory size in bytes (default: 2MB)
        """
        self.cpu = CPU()
        self.memory = Memory(memory_size)
        self.decoder = InstructionDecoder()
        self.execution = ExecutionUnit(self.cpu, self.memory)
        self.object_table = ObjectTable(self.memory)
        
        # State
        self.running = False
        self.cycle_count = 0
        self.max_cycles = 1000000  # Safety limit
        self.verbose = False
        self.trace = False
    
    def reset(self):
        """Reset simulator state"""
        self.cpu.reset()
        self.cycle_count = 0
        self.running = False
    
    def load_program(self, instructions: List[tuple]):
        """
        Load program into memory
        
        Args:
            instructions: List of (address, instruction_bits, length) tuples
        """
        for addr, bits, length in instructions:
            # Convert bits to bytes and store
            byte_length = (length + 7) // 8
            for i in range(byte_length):
                byte_val = (bits >> (i * 8)) & 0xFF
                self.memory.write_byte(addr + i, byte_val)
    
    def load_binary(self, address: int, data: bytes):
        """
        Load binary data into memory
        
        Args:
            address: Starting address
            data: Binary data to load
        """
        for i, byte_val in enumerate(data):
            self.memory.write_byte(address + i, byte_val)
    
    def dump_registers(self):
        """Print current register state"""
        print(self.cpu.registers)
    
    def dump_memory(self, address: int, length: int):
        """Print memory contents"""
        print(self.memory.dump(address, length))
    
    def dump_stack(self, count: int = 8):
        """Print top of stack"""
        print(f"Stack (SP={self.cpu.registers.sp:#x}):")
        for i in range(count):
            addr = self.cpu.registers.sp + (i * 4)
            value = self.memory.read_word(addr)
            if value is not None:
                marker = " <-- SP" if i == 0 else ""
                print(f"  [{addr:#010x}] {value:#010x}{marker}")
    
    def step(self) -> bool:
        """
        Execute one instruction cycle
        
        Returns:
            True if execution continues, False if halted
        """
        if self.cpu.halted:
            return False
        
        if self.cycle_count >= self.max_cycles:
            print(f"ERROR: Cycle limit reached ({self.max_cycles})")
            self.cpu.halt()
            return False
        
        # Fetch instruction
        instruction_bits = self.cpu.fetch_instruction()
        
        # Decode
        instruction = self.decoder.decode(instruction_bits)
        
        # Trace
        if self.trace:
            print(f"PC={self.cpu.registers.pc:#010x}: {instruction.opcode.name}")
        
        # Execute
        result = self.execution.execute(instruction)
        
        self.cycle_count += 1
        
        return result
    
    def run(self, max_cycles: int = None):
        """
        Run simulator until halted
        
        Args:
            max_cycles: Maximum cycles to run (overrides default)
        """
        if max_cycles:
            self.max_cycles = max_cycles
        
        self.running = True
        self.cpu.halted = False
        
        print("Starting execution...")
        
        while self.running and not self.cpu.halted:
            if not self.step():
                break
        
        print(f"\nExecution complete after {self.cycle_count} cycles")
        self.dump_registers()
    
    def run_interactive(self):
        """Run in interactive debug mode"""
        self.running = True
        self.cpu.halted = False
        
        print("iAPX 432 Interactive Debugger")
        print("Commands: run, step, stepN, registers, memory addr len, stack, quit")
        
        while self.running and not self.cpu.halted:
            try:
                cmd = input("\n> ").strip().split()
                if not cmd:
                    continue
                
                if cmd[0] == 'run':
                    self.run(10000)
                elif cmd[0] == 'step':
                    if not self.step():
                        break
                    self.dump_registers()
                elif cmd[0] == 'stepN':
                    n = int(cmd[1]) if len(cmd) > 1 else 10
                    for i in range(n):
                        if not self.step():
                            break
                    self.dump_registers()
                elif cmd[0] == 'registers':
                    self.dump_registers()
                elif cmd[0] == 'memory':
                    addr = int(cmd[1], 16) if len(cmd) > 1 else 0
                    length = int(cmd[2]) if len(cmd) > 2 else 64
                    self.dump_memory(addr, length)
                elif cmd[0] == 'stack':
                    count = int(cmd[1]) if len(cmd) > 1 else 8
                    self.dump_stack(count)
                elif cmd[0] in ('quit', 'exit', 'q'):
                    self.running = False
                else:
                    print(f"Unknown command: {cmd[0]}")
            except KeyboardInterrupt:
                print("\nInterrupted")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
        
        print(f"\nStopped after {self.cycle_count} cycles")
    
    def create_domain(self, parent_domain_id: Optional[int] = None) -> int:
        """Create a new domain"""
        return self.object_table.create_domain(parent_domain_id)
    
    def get_domain(self, domain_id: int) -> Optional[Domain]:
        """Get domain by ID"""
        return self.object_table.get_domain(domain_id)
    
    def __repr__(self) -> str:
        return (f"Simulator(cycles={self.cycle_count}, "
                f"objects={len(self.object_table.objects)}, "
                f"domains={len(self.object_table.domains)})")
