"""
CHIP-8 CPU

35 opcodes, 4KB memory, 16 registers, 64x32 display.
Original CHIP-8 from 1977 for COSMAC VIP.
"""

import random
from typing import List, Optional


class CPU:
    """CHIP-8 CPU core"""
    
    def __init__(self):
        # 4KB memory
        self.memory = [0] * 4096
        
        # 16 8-bit registers V0-VF
        self.v = [0] * 16
        
        # 16-bit index register
        self.i = 0
        
        # 16-bit program counter
        self.pc = 0x200  # Programs start at 0x200
        
        # Stack
        self.stack: List[int] = []
        
        # Display (64x32 monochrome)
        self.display = [[0] * 64 for _ in range(32)]
        
        # Timers
        self.delay_timer = 0
        self.sound_timer = 0
        
        # Keypad (0x0-0xF)
        self.keypad = [0] * 16
        
        # Font sprites (0-F, 5 bytes each)
        self.fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
        ]
        
        # Load fonts into memory at 0x000
        for i, byte in enumerate(self.fonts):
            self.memory[i] = byte
        
        # Running state
        self.running = False
        self.draw_flag = False
    
    def reset(self):
        """Reset CPU to initial state"""
        self.memory = [0] * 4096
        self.v = [0] * 16
        self.i = 0
        self.pc = 0x200
        self.stack = []
        self.display = [[0] * 64 for _ in range(32)]
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16
        self.running = False
        self.draw_flag = False
        
        # Reload fonts
        for i, byte in enumerate(self.fonts):
            self.memory[i] = byte
    
    def load_rom(self, data: bytes):
        """Load ROM data into memory starting at 0x200"""
        for i, byte in enumerate(data):
            if 0x200 + i < 4096:
                self.memory[0x200 + i] = byte
    
    def fetch(self) -> int:
        """Fetch 2-byte opcode at PC"""
        if self.pc + 1 >= 4096:
            return 0
        high = self.memory[self.pc]
        low = self.memory[self.pc + 1]
        return (high << 8) | low
    
    def decode_and_execute(self, opcode: int):
        """Decode and execute a single opcode"""
        # Extract nibbles
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        nnn = opcode & 0x0FFF
        nn = opcode & 0x00FF
        n = opcode & 0x000F
        
        # Decode first nibble
        nibble1 = (opcode & 0xF000) >> 12
        
        if opcode == 0x00E0:
            # CLS - Clear display
            self.display = [[0] * 64 for _ in range(32)]
            self.draw_flag = True
            
        elif opcode == 0x00EE:
            # RET - Return from subroutine
            if self.stack:
                self.pc = self.stack.pop()
            else:
                self.pc += 2
                
        elif nibble1 == 0x1:
            # JP addr - Jump to address
            self.pc = nnn
            
        elif nibble1 == 0x2:
            # CALL addr - Call subroutine
            self.stack.append(self.pc + 2)
            self.pc = nnn
            
        elif nibble1 == 0x3:
            # SE Vx, byte - Skip if Vx == nn
            if self.v[x] == nn:
                self.pc += 4
            else:
                self.pc += 2
                
        elif nibble1 == 0x4:
            # SNE Vx, byte - Skip if Vx != nn
            if self.v[x] != nn:
                self.pc += 4
            else:
                self.pc += 2
                
        elif nibble1 == 0x5:
            # SE Vx, Vy - Skip if Vx == Vy
            if self.v[x] == self.v[y]:
                self.pc += 4
            else:
                self.pc += 2
                
        elif nibble1 == 0x6:
            # LD Vx, byte - Set Vx = nn
            self.v[x] = nn
            self.pc += 2
            
        elif nibble1 == 0x7:
            # ADD Vx, byte - Set Vx = Vx + nn
            self.v[x] = (self.v[x] + nn) & 0xFF
            self.pc += 2
            
        elif nibble1 == 0x8:
            self._execute_8xy(opcode, x, y, n)
            self.pc += 2
            
        elif nibble1 == 0x9:
            # SNE Vx, Vy - Skip if Vx != Vy
            if self.v[x] != self.v[y]:
                self.pc += 4
            else:
                self.pc += 2
                
        elif nibble1 == 0xA:
            # LD I, addr - Set I = nnn
            self.i = nnn
            self.pc += 2
            
        elif nibble1 == 0xB:
            # JP V0, addr - Jump to V0 + nnn
            self.pc = self.v[0] + nnn
            
        elif nibble1 == 0xC:
            # RND Vx, byte - Set Vx = random byte AND nn
            self.v[x] = random.randint(0, 255) & nn
            self.pc += 2
            
        elif nibble1 == 0xD:
            # DRW Vx, Vy, n - Draw sprite
            self._draw_sprite(x, y, n)
            self.pc += 2
            
        elif nibble1 == 0xE:
            if nn == 0x9E:
                # SKP Vx - Skip if key Vx is pressed
                if self.keypad[self.v[x]]:
                    self.pc += 4
                else:
                    self.pc += 2
            elif nn == 0xA1:
                # SKNP Vx - Skip if key Vx is NOT pressed
                if not self.keypad[self.v[x]]:
                    self.pc += 4
                else:
                    self.pc += 2
            else:
                self.pc += 2
                
        elif nibble1 == 0xF:
            if nn == 0x07:
                # LD Vx, DT - Set Vx = delay timer
                self.v[x] = self.delay_timer
                self.pc += 2
            elif nn == 0x0A:
                # LD Vx, K - Wait for key press
                key_pressed = False
                for k in range(16):
                    if self.keypad[k]:
                        self.v[x] = k
                        key_pressed = True
                        break
                if not key_pressed:
                    return  # Don't advance PC, wait
                self.pc += 2
            elif nn == 0x15:
                # LD DT, Vx - Set delay timer = Vx
                self.delay_timer = self.v[x]
                self.pc += 2
            elif nn == 0x18:
                # LD ST, Vx - Set sound timer = Vx
                self.sound_timer = self.v[x]
                self.pc += 2
            elif nn == 0x1E:
                # ADD I, Vx - I = I + Vx
                self.i = (self.i + self.v[x]) & 0xFFFF
                self.pc += 2
            elif nn == 0x29:
                # LD F, Vx - Set I = font sprite address for Vx
                self.i = self.v[x] * 5
                self.pc += 2
            elif nn == 0x33:
                # LD B, Vx - Store BCD of Vx at I, I+1, I+2
                val = self.v[x]
                self.memory[self.i] = val // 100
                self.memory[self.i + 1] = (val // 10) % 10
                self.memory[self.i + 2] = val % 10
                self.pc += 2
            elif nn == 0x55:
                # LD [I], Vx - Store V0-Vx in memory starting at I
                for j in range(x + 1):
                    self.memory[self.i + j] = self.v[j]
                self.pc += 2
            elif nn == 0x65:
                # LD Vx, [I] - Load V0-Vx from memory starting at I
                for j in range(x + 1):
                    self.v[j] = self.memory[self.i + j]
                self.pc += 2
            else:
                self.pc += 2
        else:
            # Unknown opcode
            self.pc += 2
    
    def _execute_8xy(self, opcode: int, x: int, y: int, n: int):
        """Execute 8XY_ opcodes"""
        if n == 0x0:
            # LD Vx, Vy
            self.v[x] = self.v[y]
        elif n == 0x1:
            # OR Vx, Vy
            self.v[x] |= self.v[y]
        elif n == 0x2:
            # AND Vx, Vy
            self.v[x] &= self.v[y]
        elif n == 0x3:
            # XOR Vx, Vy
            self.v[x] ^= self.v[y]
        elif n == 0x4:
            # ADD Vx, Vy (with carry)
            result = self.v[x] + self.v[y]
            self.v[0xF] = 1 if result > 0xFF else 0
            self.v[x] = result & 0xFF
        elif n == 0x5:
            # SUB Vx, Vy (with borrow)
            self.v[0xF] = 1 if self.v[x] > self.v[y] else 0
            self.v[x] = (self.v[x] - self.v[y]) & 0xFF
        elif n == 0x6:
            # SHR Vx
            self.v[0xF] = self.v[x] & 0x1
            self.v[x] >>= 1
        elif n == 0x7:
            # SUBN Vx, Vy
            self.v[0xF] = 1 if self.v[y] > self.v[x] else 0
            self.v[x] = (self.v[y] - self.v[x]) & 0xFF
        elif n == 0xE:
            # SHL Vx
            self.v[0xF] = (self.v[x] & 0x80) >> 7
            self.v[x] = (self.v[x] << 1) & 0xFF
    
    def _draw_sprite(self, x: int, y: int, n: int):
        """Draw sprite at (Vx, Vy) with n bytes"""
        vx = self.v[x] % 64
        vy = self.v[y] % 32
        self.v[0xF] = 0  # Reset collision flag
        
        for row in range(n):
            sprite_byte = self.memory[self.i + row]
            for col in range(8):
                if sprite_byte & (0x80 >> col):
                    px = (vx + col) % 64
                    py = (vy + row) % 32
                    if self.display[py][px]:
                        self.v[0xF] = 1  # Collision
                    self.display[py][px] ^= 1
        
        self.draw_flag = True
    
    def update_timers(self):
        """Update delay and sound timers (called at 60Hz)"""
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
    
    def cycle(self):
        """Execute one CPU cycle"""
        if not self.running:
            return
        
        opcode = self.fetch()
        self.decode_and_execute(opcode)
    
    def __repr__(self) -> str:
        return (f"CPU(PC={self.pc:#06x}, I={self.i:#06x}, "
                f"SP={len(self.stack)}, timers=[{self.delay_timer},{self.sound_timer}])")
