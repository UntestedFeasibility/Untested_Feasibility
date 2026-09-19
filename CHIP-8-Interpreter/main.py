#!/usr/bin/env python3
"""
CHIP-8 Interpreter

Usage:
    python main.py <rom_file>
    python main.py --test    # Run built-in test ROM
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.interpreter import Interpreter


def create_test_rom() -> bytes:
    """Create a simple test ROM that draws 'HI' on screen"""
    rom = bytearray()
    
    # Clear screen
    rom.append(0x00)
    rom.append(0xE0)
    
    # Set I = 0x200 (start of program area for sprite data)
    # We'll use the font sprites already loaded
    
    # Draw 'H' (using font H at 0x240 - but we need to define our own)
    # Let's use a simple approach: draw a pattern
    
    # LD I, 0x200 (we'll store sprite data here)
    rom.append(0xA2)
    rom.append(0x00)
    
    # Actually, let's just use the built-in font for some letters
    # Font A is at index 0x0A * 5 = 0x32
    
    # Draw 'H' - use font H (index 8, address 0x28)
    rom.append(0x60)  # LD V0, 8 (x position)
    rom.append(0x08)
    rom.append(0x61)  # LD V1, 5 (y position)  
    rom.append(0x05)
    rom.append(0xA0)  # LD I, 0x028 (font H)
    rom.append(0x28)
    rom.append(0xD0)  # DRW V0, V1, 5 (draw 5 rows)
    rom.append(0x15)
    
    # Draw 'I' at x=20
    rom.append(0x60)  # LD V0, 20
    rom.append(0x14)
    rom.append(0xA0)  # LD I, 0x02D (font I)
    rom.append(0x2D)
    rom.append(0xD0)  # DRW V0, V1, 5
    rom.append(0x15)
    
    # Draw '!' at x=32
    rom.append(0x60)  # LD V0, 32
    rom.append(0x20)
    rom.append(0xA0)  # LD I, font 1 (for ! we use something simple)
    rom.append(0x05)
    rom.append(0xD0)  # DRW V0, V1, 5
    rom.append(0x15)
    
    # Jump back to self (infinite loop)
    rom.append(0x12)  # JP 0x200
    rom.append(0x00)
    
    return bytes(rom)


def main():
    interp = Interpreter()
    
    if len(sys.argv) < 2:
        print("CHIP-8 Interpreter")
        print(f"Usage: {sys.argv[0]} <rom_file>")
        print(f"       {sys.argv[0]} --test")
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        # Create and load test ROM
        test_rom = create_test_rom()
        test_path = "/tmp/test.ch8"
        with open(test_path, 'wb') as f:
            f.write(test_rom)
        interp.load_rom(test_path)
    else:
        interp.load_rom(sys.argv[1])
    
    interp.run()


if __name__ == "__main__":
    main()
