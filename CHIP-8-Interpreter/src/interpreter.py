"""
CHIP-8 Interpreter

Main interpreter class tying CPU, display, and input together.
"""

import time
import sys
from .cpu import CPU
from .display import Display


class Interpreter:
    """CHIP-8 interpreter main loop"""
    
    def __init__(self):
        self.cpu = CPU()
        self.display = Display()
        self.cycles_per_second = 700  # Original CHIP-8 speed
        self.timer_rate = 60  # 60Hz for timers
        self.running = False
    
    def load_rom(self, filepath: str):
        """Load ROM file"""
        with open(filepath, 'rb') as f:
            data = f.read()
        self.cpu.load_rom(data)
        print(f"Loaded {len(data)} bytes from {filepath}")
    
    def run(self, rom_path: str = None):
        """Run interpreter"""
        if rom_path:
            self.load_rom(rom_path)
        
        self.cpu.running = True
        self.running = True
        
        cycle_time = 1.0 / self.cycles_per_second
        timer_time = 1.0 / self.timer_rate
        last_timer = time.time()
        
        print("CHIP-8 Interpreter running. Press Ctrl+C to stop.")
        print("Keys: 1234 / QWERT / ASDFG / ZXCVB (mapped to 0-F)")
        print()
        
        try:
            while self.running and self.cpu.running:
                # CPU cycle
                self.cpu.cycle()
                
                # Update display if needed
                if self.cpu.draw_flag:
                    self.display.render_terminal()
                    self.cpu.draw_flag = False
                
                # Update timers at 60Hz
                now = time.time()
                if now - last_timer >= timer_time:
                    self.cpu.update_timers()
                    if self.cpu.sound_timer > 0:
                        print("\a", end="", flush=True)  # Beep
                    last_timer = now
                
                # Cycle timing
                time.sleep(cycle_time)
                
        except KeyboardInterrupt:
            print("\nStopped.")
        
        self.running = False
    
    def step(self):
        """Execute one step"""
        self.cpu.cycle()
        if self.cpu.draw_flag:
            self.display.render_terminal()
            self.cpu.draw_flag = False
    
    def dump_state(self):
        """Print CPU state"""
        print(self.cpu)
        print(f"V: {[hex(v) for v in self.cpu.v[:8]]}")
        print(f"  {[hex(v) for v in self.cpu.v[8:]]}")
        print(f"I: {self.cpu.i:#06x}")
        print(f"Stack: {[hex(s) for s in self.cpu.stack]}")
