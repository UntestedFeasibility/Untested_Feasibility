"""
iAPX 432 Execution Unit

Implements the ALU, stack operations, and instruction execution.
"""

from typing import Optional
from .cpu import CPU
from .memory import Memory
from .decoder import DecodedInstruction, Opcode


class ExecutionUnit:
    """
    iAPX 432 Execution Unit
    
    Executes decoded instructions, performing arithmetic,
    logic, memory access, and control flow operations.
    """
    
    def __init__(self, cpu: CPU, memory: Memory):
        self.cpu = cpu
        self.memory = memory
    
    def execute(self, instruction: DecodedInstruction) -> bool:
        """
        Execute a decoded instruction
        
        Args:
            instruction: Decoded instruction to execute
            
        Returns:
            True if execution continues, False if halted
        """
        opcode = instruction.opcode
        
        # Dispatch to handler
        handlers = {
            Opcode.NOP: self._nop,
            Opcode.HALT: self._halt,
            Opcode.LOAD: self._load,
            Opcode.STORE: self._store,
            Opcode.PUSH: self._push,
            Opcode.POP: self._pop,
            Opcode.ADD: self._add,
            Opcode.SUB: self._sub,
            Opcode.MUL: self._mul,
            Opcode.DIV: self._div,
            Opcode.AND: self._and,
            Opcode.OR: self._or,
            Opcode.XOR: self._xor,
            Opcode.NOT: self._not,
            Opcode.COMPARE: self._compare,
            Opcode.BRANCH: self._branch,
            Opcode.BRANCHEQ: self._branch_eq,
            Opcode.BRANCHNE: self._branch_ne,
            Opcode.CALL: self._call,
            Opcode.RETURN: self._return,
            Opcode.CREATE: self._create,
            Opcode.DESTROY: self._destroy,
            Opcode.CHECKRIGHTS: self._check_rights,
            Opcode.DOMAINSWITCH: self._domain_switch,
            Opcode.GETAD: self._get_ad,
            Opcode.PUTAD: self._put_ad,
            Opcode.GETTYPE: self._get_type,
            Opcode.SETTYPE: self._set_type,
        }
        
        handler = handlers.get(opcode)
        if handler:
            return handler(instruction)
        else:
            # Unknown opcode - treat as NOP
            return True
    
    def _nop(self, instruction: DecodedInstruction) -> bool:
        """No operation"""
        return True
    
    def _halt(self, instruction: DecodedInstruction) -> bool:
        """Halt processor"""
        self.cpu.halt()
        return False
    
    def _load(self, instruction: DecodedInstruction) -> bool:
        """Load value from memory to stack"""
        if instruction.references:
            ref = instruction.references[0]
            address = self._resolve_address(ref)
            value = self.memory.read_word(address)
            if value is not None:
                self.cpu.push_stack(value)
        return True
    
    def _store(self, instruction: DecodedInstruction) -> bool:
        """Store value from stack to memory"""
        value = self.cpu.pop_stack()
        if value is None:
            return False
        
        if instruction.references:
            ref = instruction.references[0]
            address = self._resolve_address(ref)
            self.memory.write_word(address, value)
        return True
    
    def _push(self, instruction: DecodedInstruction) -> bool:
        """Push immediate value onto stack"""
        # Use immediate field or 0
        value = instruction.immediate
        self.cpu.push_stack(value)
        return True
    
    def _pop(self, instruction: DecodedInstruction) -> bool:
        """Pop value from stack"""
        self.cpu.pop_stack()
        return True
    
    def _add(self, instruction: DecodedInstruction) -> bool:
        """Add top two stack values"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        result = (a + b) & 0xFFFFFFFF
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _sub(self, instruction: DecodedInstruction) -> bool:
        """Subtract: second - top"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        result = (a - b) & 0xFFFFFFFF
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _mul(self, instruction: DecodedInstruction) -> bool:
        """Multiply top two stack values"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        result = (a * b) & 0xFFFFFFFF
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _div(self, instruction: DecodedInstruction) -> bool:
        """Divide: second / top"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        if b == 0:
            # Division by zero - halt
            self.cpu.halt()
            return False
        
        result = (a // b) & 0xFFFFFFFF
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _and(self, instruction: DecodedInstruction) -> bool:
        """Bitwise AND"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        result = a & b
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _or(self, instruction: DecodedInstruction) -> bool:
        """Bitwise OR"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        result = a | b
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _xor(self, instruction: DecodedInstruction) -> bool:
        """Bitwise XOR"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        result = a ^ b
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _not(self, instruction: DecodedInstruction) -> bool:
        """Bitwise NOT"""
        a = self.cpu.pop_stack()
        if a is None:
            return False
        
        result = (~a) & 0xFFFFFFFF
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _compare(self, instruction: DecodedInstruction) -> bool:
        """Compare two values"""
        b = self.cpu.pop_stack()
        a = self.cpu.pop_stack()
        if a is None or b is None:
            return False
        
        if a < b:
            result = -1
        elif a == b:
            result = 0
        else:
            result = 1
        
        self.cpu.push_stack(result)
        self.cpu.set_condition(result)
        return True
    
    def _branch(self, instruction: DecodedInstruction) -> bool:
        """Unconditional branch"""
        if instruction.immediate != 0:
            self.cpu.registers.pc = instruction.immediate
        return True
    
    def _branch_eq(self, instruction: DecodedInstruction) -> bool:
        """Branch if equal (top of stack == 0)"""
        value = self.cpu.pop_stack()
        if value is None:
            return False
        
        if value == 0 and instruction.immediate != 0:
            self.cpu.registers.pc = instruction.immediate
        return True
    
    def _branch_ne(self, instruction: DecodedInstruction) -> bool:
        """Branch if not equal (top of stack != 0)"""
        value = self.cpu.pop_stack()
        if value is None:
            return False
        
        if value != 0 and instruction.immediate != 0:
            self.cpu.registers.pc = instruction.immediate
        return True
    
    def _call(self, instruction: DecodedInstruction) -> bool:
        """Call subroutine"""
        # Push return address
        return_addr = self.cpu.registers.pc + 4
        self.cpu.push_stack(return_addr)
        
        # Jump to target
        if instruction.immediate != 0:
            self.cpu.registers.pc = instruction.immediate
        return True
    
    def _return(self, instruction: DecodedInstruction) -> bool:
        """Return from subroutine"""
        return_addr = self.cpu.pop_stack()
        if return_addr is None:
            return False
        
        self.cpu.registers.pc = return_addr
        return True
    
    def _create(self, instruction: DecodedInstruction) -> bool:
        """Create object (simplified)"""
        # Push dummy AD
        self.cpu.push_stack(0x1000)  # Fake AD address
        return True
    
    def _destroy(self, instruction: DecodedInstruction) -> bool:
        """Destroy object (simplified)"""
        self.cpu.pop_stack()  # Remove AD
        return True
    
    def _check_rights(self, instruction: DecodedInstruction) -> bool:
        """Check access rights (simplified)"""
        ad = self.cpu.pop_stack()
        if ad is None:
            return False
        
        # Always succeed in simplified version
        self.cpu.push_stack(1)  # 1 = has rights
        return True
    
    def _domain_switch(self, instruction: DecodedInstruction) -> bool:
        """Switch domain (simplified)"""
        domain_ad = self.cpu.pop_stack()
        if domain_ad is None:
            return False
        
        # In simplified version, just continue
        return True
    
    def _get_ad(self, instruction: DecodedInstruction) -> bool:
        """Get access descriptor"""
        self.cpu.push_stack(0x1000)  # Fake AD
        return True
    
    def _put_ad(self, instruction: DecodedInstruction) -> bool:
        """Put access descriptor"""
        self.cpu.pop_stack()
        return True
    
    def _get_type(self, instruction: DecodedInstruction) -> bool:
        """Get object type"""
        ad = self.cpu.pop_stack()
        if ad is None:
            return False
        
        self.cpu.push_stack(0x01)  # Type = INSTRUCTION
        return True
    
    def _set_type(self, instruction: DecodedInstruction) -> bool:
        """Set object type"""
        type_val = self.cpu.pop_stack()
        ad = self.cpu.pop_stack()
        # Simplified - just pop values
        return True
    
    def _resolve_address(self, ref) -> int:
        """
        Resolve reference field to memory address
        
        This is a simplified version of the full address resolution.
        """
        mode = ref.access_mode
        
        if mode.value == 0:  # DIRECT
            return ref.displacement
        elif mode.value == 2:  # STACK
            return self.cpu.registers.sp + ref.displacement
        elif mode.value == 3:  # RELATIVE
            return self.cpu.registers.pc + ref.displacement
        else:
            return ref.displacement
    
    def step(self) -> bool:
        """
        Execute one instruction step
        
        Returns:
            True if execution continues, False if halted
        """
        if self.cpu.halted:
            return False
        
        # Fetch instruction word
        instruction_bits = self.cpu.fetch_instruction()
        
        # Decode instruction
        from .decoder import InstructionDecoder
        decoder = InstructionDecoder()
        instruction = decoder.decode(instruction_bits)
        
        # Execute instruction
        return self.execute(instruction)
