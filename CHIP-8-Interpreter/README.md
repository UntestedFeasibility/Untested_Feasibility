# CHIP-8 Interpreter

A Python interpreter for the CHIP-8 programming language (1977).

## What is CHIP-8?

CHIP-8 is an interpreted programming language used on the COSMAC VIP and other early 8-bit microcomputers. It's a simple virtual machine with:

- 4KB memory
- 16 registers (V0-VF)
- 64x32 monochrome display
- 16-key hex keypad
- 35 opcodes

## Files

```
chip8/
├── main.py              # Entry point
├── requirements.txt     # Dependencies (none)
├── src/
│   ├── cpu.py          # CPU core (opcodes, registers, memory)
│   ├── display.py      # 64x32 display rendering
│   └── interpreter.py  # Main interpreter loop
├── tests/
│   └── test_cpu.py     # Unit tests
└── roms/               # ROM files go here
```

## Usage

```bash
# Run a ROM
python main.py roms/ibm.ch8

# Run built-in test
python main.py --test

# Run tests
python tests/test_cpu.py
```

## Opcodes

| Opcode | Description |
|--------|-------------|
| 00E0 | Clear screen |
| 00EE | Return from subroutine |
| 1NNN | Jump to NNN |
| 2NNN | Call subroutine at NNN |
| 3XNN | Skip if VX == NN |
| 4XNN | Skip if VX != NN |
| 5XY0 | Skip if VX == VY |
| 6XNN | Set VX = NN |
| 7XNN | Add NN to VX |
| 8XY0 | Set VX = VY |
| 8XY1 | VX = VX OR VY |
| 8XY2 | VX = VX AND VY |
| 8XY3 | VX = VX XOR VY |
| 8XY4 | VX = VX + VY (carry in VF) |
| 8XY5 | VX = VX - VY (borrow in VF) |
| 8XY6 | VX = VX >> 1 |
| 8XY7 | VX = VY - VX |
| 8XYE | VX = VX << 1 |
| 9XY0 | Skip if VX != VY |
| ANNN | Set I = NNN |
| BNNN | Jump to V0 + NNN |
| CXNN | VX = random() AND NN |
| DXYN | Draw sprite at (VX, VY), N bytes |
| EX9E | Skip if key VX is pressed |
| EXA1 | Skip if key VX not pressed |
| FX07 | VX = delay timer |
| FX0A | Wait for key press |
| FX15 | Delay timer = VX |
| FX18 | Sound timer = VX |
| FX1E | I = I + VX |
| FX29 | I = font sprite address |
| FX33 | Store BCD of VX |
| FX55 | Store V0-VX in memory |
| FX65 | Load V0-VX from memory |

## Controls

The 16-key keypad maps to:

```
1 2 3 C     →     1 2 3 4
4 5 6 D     →     Q W E R
7 8 9 E     →     A S D F
A 0 B F     →     Z X C V
```

## History

CHIP-8 was created in the mid-1970s by Joe Weisbecker. It was designed to make programming easier on early microcomputers like the COSMAC VIP and Telmac 1800.

## License

Educational use.
