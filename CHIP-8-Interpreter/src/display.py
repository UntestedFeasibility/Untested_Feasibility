"""
CHIP-8 Display

64x32 monochrome pixel display with terminal rendering.
"""

import os
import sys


class Display:
    """CHIP-8 display with terminal output"""
    
    PIXEL_ON = "██"
    PIXEL_OFF = "  "
    
    def __init__(self, width: int = 64, height: int = 32):
        self.width = width
        self.height = height
        self.pixels = [[0] * width for _ in range(height)]
        self.scale = 10  # For graphical output
    
    def clear(self):
        """Clear display"""
        self.pixels = [[0] * self.width for _ in range(self.height)]
    
    def set_pixel(self, x: int, y: int, value: int) -> int:
        """
        Set pixel value (XOR)
        Returns collision flag
        """
        x = x % self.width
        y = y % self.height
        collision = self.pixels[y][x]
        self.pixels[y][x] ^= value
        return collision
    
    def get_pixel(self, x: int, y: int) -> int:
        """Get pixel value"""
        return self.pixels[y % self.height][x % self.width]
    
    def render_terminal(self):
        """Render display to terminal"""
        # Clear screen
        sys.stdout.write("\033[H\033[J")
        
        # Top border
        print("┌" + "──" * self.width + "┐")
        
        for row in self.pixels:
            line = "│"
            for pixel in row:
                line += self.PIXEL_ON if pixel else self.PIXEL_OFF
            line += "│"
            print(line)
        
        # Bottom border
        print("└" + "──" * self.width + "┘")
    
    def render_text(self):
        """Render display as ASCII art"""
        lines = []
        lines.append("┌" + "─" * self.width + "┐")
        for row in self.pixels:
            line = "│"
            for pixel in row:
                line += "█" if pixel else " "
            line += "│"
            lines.append(line)
        lines.append("└" + "─" * self.width + "┘")
        return "\n".join(lines)
    
    def get_framebuffer(self) -> bytes:
        """Get display as framebuffer (1-bit per pixel)"""
        data = bytearray()
        for row in self.pixels:
            for i in range(0, self.width, 8):
                byte = 0
                for bit in range(8):
                    if i + bit < self.width and row[i + bit]:
                        byte |= (0x80 >> bit)
                data.append(byte)
        return bytes(data)
