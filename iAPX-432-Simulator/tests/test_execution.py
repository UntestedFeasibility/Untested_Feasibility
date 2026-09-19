"""
Unit tests for iAPX 432 Execution Unit
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cpu import CPU
from src.memory import Memory
from src.execution import ExecutionUnit
from src.decoder import DecodedInstruction, Opcode


def test_nop():
    """Test NOP execution"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    instruction = DecodedInstruction()
    instruction.opcode = Opcode.NOP
    
    result = eu.execute(instruction)
    assert result is True
    print("PASS: test_nop")


def test_halt():
    """Test HALT execution"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    instruction = DecodedInstruction()
    instruction.opcode = Opcode.HALT
    
    result = eu.execute(instruction)
    assert result is False
    assert cpu.halted is True
    print("PASS: test_halt")


def test_push_pop():
    """Test PUSH and POP operations"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    initial_sp = cpu.registers.sp
    
    # Push value
    push_instruction = DecodedInstruction()
    push_instruction.opcode = Opcode.PUSH
    push_instruction.immediate = 42
    
    eu.execute(push_instruction)
    assert cpu.registers.sp == initial_sp + 1
    
    # Pop value
    pop_instruction = DecodedInstruction()
    pop_instruction.opcode = Opcode.POP
    
    eu.execute(pop_instruction)
    assert cpu.registers.sp == initial_sp
    print("PASS: test_push_pop")


def test_add():
    """Test ADD operation"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    initial_sp = cpu.registers.sp
    
    # Push first value
    push1 = DecodedInstruction()
    push1.opcode = Opcode.PUSH
    push1.immediate = 10
    eu.execute(push1)
    
    # Push second value
    push2 = DecodedInstruction()
    push2.opcode = Opcode.PUSH
    push2.immediate = 20
    eu.execute(push2)
    
    # Add
    add_instruction = DecodedInstruction()
    add_instruction.opcode = Opcode.ADD
    eu.execute(add_instruction)
    
    # Check result (should be on stack)
    assert cpu.registers.sp == initial_sp + 1
    print("PASS: test_add")


def test_sub():
    """Test SUB operation"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    initial_sp = cpu.registers.sp
    
    # Push values
    push1 = DecodedInstruction()
    push1.opcode = Opcode.PUSH
    push1.immediate = 30
    eu.execute(push1)
    
    push2 = DecodedInstruction()
    push2.opcode = Opcode.PUSH
    push2.immediate = 10
    eu.execute(push2)
    
    # Sub (30 - 10 = 20)
    sub_instruction = DecodedInstruction()
    sub_instruction.opcode = Opcode.SUB
    eu.execute(sub_instruction)
    
    assert cpu.registers.sp == initial_sp + 1
    print("PASS: test_sub")


def test_and_or_xor():
    """Test bitwise operations"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    initial_sp = cpu.registers.sp
    
    # Push values
    push1 = DecodedInstruction()
    push1.opcode = Opcode.PUSH
    push1.immediate = 0xFF
    eu.execute(push1)
    
    push2 = DecodedInstruction()
    push2.opcode = Opcode.PUSH
    push2.immediate = 0x0F
    eu.execute(push2)
    
    # AND
    and_instruction = DecodedInstruction()
    and_instruction.opcode = Opcode.AND
    eu.execute(and_instruction)
    
    assert cpu.registers.sp == initial_sp + 1
    
    # Push another value
    push3 = DecodedInstruction()
    push3.opcode = Opcode.PUSH
    push3.immediate = 0xF0
    eu.execute(push3)
    
    # OR
    or_instruction = DecodedInstruction()
    or_instruction.opcode = Opcode.OR
    eu.execute(or_instruction)
    
    assert cpu.registers.sp == initial_sp + 1
    print("PASS: test_and_or_xor")


def test_branch():
    """Test branch operations"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    # Push branch target
    push_instruction = DecodedInstruction()
    push_instruction.opcode = Opcode.PUSH
    push_instruction.immediate = 0x100
    eu.execute(push_instruction)
    
    # Unconditional branch
    branch_instruction = DecodedInstruction()
    branch_instruction.opcode = Opcode.BRANCH
    branch_instruction.immediate = 0x100
    result = eu.execute(branch_instruction)
    
    assert cpu.registers.pc == 0x100
    print("PASS: test_branch")


def test_call_return():
    """Test CALL and RETURN operations"""
    cpu = CPU()
    memory = Memory()
    eu = ExecutionUnit(cpu, memory)
    
    initial_sp = cpu.registers.sp
    
    # Set initial PC
    cpu.registers.pc = 0x50
    
    # Call subroutine
    call_instruction = DecodedInstruction()
    call_instruction.opcode = Opcode.CALL
    call_instruction.immediate = 0x200
    eu.execute(call_instruction)
    
    # Check return address was pushed
    assert cpu.registers.sp == initial_sp + 1
    assert cpu.registers.pc == 0x200
    
    # Return
    return_instruction = DecodedInstruction()
    return_instruction.opcode = Opcode.RETURN
    eu.execute(return_instruction)
    
    # Should be back at return address
    assert cpu.registers.pc == 0x54  # 0x50 + 4
    print("PASS: test_call_return")


def test_execute_step():
    """Test step execution"""
    cpu = CPU()
    memory = Memory()
    cpu.initialize(memory)  # Initialize CPU with memory
    eu = ExecutionUnit(cpu, memory)
    
    # Store a HALT instruction in memory (in data segment, which is writable)
    # HALT = 0x1F (5 bits), shifted to correct position
    halt_bits = 0x1F << 7
    address = memory.get_data_base()
    memory.write_word(address, halt_bits)
    
    # Set PC to data segment
    cpu.registers.pc = address
    
    # Execute step
    result = eu.step()
    
    # Should have halted
    assert result is False
    assert cpu.halted is True
    print("PASS: test_execute_step")


if __name__ == '__main__':
    print("Running execution tests...")
    test_nop()
    test_halt()
    test_push_pop()
    test_add()
    test_sub()
    test_and_or_xor()
    test_branch()
    test_call_return()
    test_execute_step()
    print("\nAll execution tests passed!")
