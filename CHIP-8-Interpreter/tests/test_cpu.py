"""CHIP-8 CPU tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cpu import CPU


def test_reset():
    cpu = CPU()
    cpu.v[0] = 42
    cpu.pc = 0x400
    cpu.reset()
    assert cpu.pc == 0x200
    assert cpu.v[0] == 0
    print("PASS: test_reset")


def test_load_rom():
    cpu = CPU()
    rom = bytes([0xA2, 0x2A])  # LD I, 0x22A
    cpu.load_rom(rom)
    assert cpu.memory[0x200] == 0xA2
    assert cpu.memory[0x201] == 0x2A
    print("PASS: test_load_rom")


def test_fetch():
    cpu = CPU()
    cpu.memory[0x200] = 0x00
    cpu.memory[0x201] = 0xE0
    opcode = cpu.fetch()
    assert opcode == 0x00E0
    print("PASS: test_fetch")


def test_cls():
    cpu = CPU()
    cpu.display[0][0] = 1
    cpu.decode_and_execute(0x00E0)
    assert cpu.display[0][0] == 0
    assert cpu.draw_flag is True
    print("PASS: test_cls")


def test_ret():
    cpu = CPU()
    cpu.stack.append(0x300)
    cpu.decode_and_execute(0x00EE)
    assert cpu.pc == 0x300
    assert len(cpu.stack) == 0
    print("PASS: test_ret")


def test_jp():
    cpu = CPU()
    cpu.decode_and_execute(0x1456)
    assert cpu.pc == 0x456
    print("PASS: test_jp")


def test_call_ret():
    cpu = CPU()
    cpu.pc = 0x200
    cpu.decode_and_execute(0x2400)  # CALL 0x400
    assert cpu.pc == 0x400
    assert len(cpu.stack) == 1
    cpu.decode_and_execute(0x00EE)  # RET
    assert cpu.pc == 0x202
    print("PASS: test_call_ret")


def test_se_vx_nn():
    cpu = CPU()
    cpu.v[0] = 0x42
    cpu.pc = 0x200
    cpu.decode_and_execute(0x3042)  # SE V0, 0x42
    assert cpu.pc == 0x204  # Skip
    print("PASS: test_se_vx_nn")


def test_sne_vx_nn():
    cpu = CPU()
    cpu.v[0] = 0x42
    cpu.pc = 0x200
    cpu.decode_and_execute(0x4042)  # SNE V0, 0x42 (equal, no skip)
    assert cpu.pc == 0x202
    cpu.v[0] = 0x43
    cpu.pc = 0x200
    cpu.decode_and_execute(0x4042)  # SNE V0, 0x42 (not equal, skip)
    assert cpu.pc == 0x204
    print("PASS: test_sne_vx_nn")


def test_ld_vx_nn():
    cpu = CPU()
    cpu.decode_and_execute(0x60FF)  # LD V0, 0xFF
    assert cpu.v[0] == 0xFF
    print("PASS: test_ld_vx_nn")


def test_add_vx_nn():
    cpu = CPU()
    cpu.v[0] = 0x10
    cpu.decode_and_execute(0x7020)  # ADD V0, 0x20
    assert cpu.v[0] == 0x30
    cpu.v[0] = 0xFF
    cpu.decode_and_execute(0x7001)  # ADD V0, 0x01 (overflow wraps)
    assert cpu.v[0] == 0x00
    print("PASS: test_add_vx_nn")


def test_ld_i():
    cpu = CPU()
    cpu.decode_and_execute(0xA123)  # LD I, 0x123
    assert cpu.i == 0x123
    print("PASS: test_ld_i")


def test_add_i():
    cpu = CPU()
    cpu.i = 0x100
    cpu.v[5] = 0x20
    cpu.decode_and_execute(0xF51E)  # ADD I, V5
    assert cpu.i == 0x120
    print("PASS: test_add_i")


def test_ld_bcd():
    cpu = CPU()
    cpu.v[3] = 254
    cpu.i = 0x300
    cpu.decode_and_execute(0xF333)  # LD B, V3
    assert cpu.memory[0x300] == 2  # Hundreds
    assert cpu.memory[0x301] == 5  # Tens
    assert cpu.memory[0x302] == 4  # Ones
    print("PASS: test_ld_bcd")


def test_ld_vx_vy():
    cpu = CPU()
    cpu.v[1] = 0x42
    cpu.decode_and_execute(0x8010)  # LD V0, V1
    assert cpu.v[0] == 0x42
    print("PASS: test_ld_vx_vy")


def test_add_vx_vy():
    cpu = CPU()
    cpu.v[0] = 10
    cpu.v[1] = 20
    cpu.decode_and_execute(0x8014)  # ADD V0, V1
    assert cpu.v[0] == 30
    assert cpu.v[0xF] == 0  # No carry
    print("PASS: test_add_vx_vy")


def test_add_vx_vy_carry():
    cpu = CPU()
    cpu.v[0] = 0xFF
    cpu.v[1] = 0x01
    cpu.decode_and_execute(0x8014)  # ADD V0, V1
    assert cpu.v[0] == 0x00
    assert cpu.v[0xF] == 1  # Carry
    print("PASS: test_add_vx_vy_carry")


def test_sub_vx_vy():
    cpu = CPU()
    cpu.v[0] = 30
    cpu.v[1] = 10
    cpu.decode_and_execute(0x8015)  # SUB V0, V1
    assert cpu.v[0] == 20
    assert cpu.v[0xF] == 1  # No borrow
    print("PASS: test_sub_vx_vy")


def test_sub_vx_vy_borrow():
    cpu = CPU()
    cpu.v[0] = 10
    cpu.v[1] = 30
    cpu.decode_and_execute(0x8015)  # SUB V0, V1
    assert cpu.v[0] == 236  # Wraps around
    assert cpu.v[0xF] == 0  # Borrow
    print("PASS: test_sub_vx_vy_borrow")


def test_and():
    cpu = CPU()
    cpu.v[0] = 0xF0
    cpu.v[1] = 0x0F
    cpu.decode_and_execute(0x8012)  # AND V0, V1
    assert cpu.v[0] == 0x00
    print("PASS: test_and")


def test_or():
    cpu = CPU()
    cpu.v[0] = 0xF0
    cpu.v[1] = 0x0F
    cpu.decode_and_execute(0x8011)  # OR V0, V1
    assert cpu.v[0] == 0xFF
    print("PASS: test_or")


def test_xor():
    cpu = CPU()
    cpu.v[0] = 0xFF
    cpu.v[1] = 0x0F
    cpu.decode_and_execute(0x8013)  # XOR V0, V1
    assert cpu.v[0] == 0xF0
    print("PASS: test_xor")


def test_shr():
    cpu = CPU()
    cpu.v[0] = 0b1010
    cpu.decode_and_execute(0x8006)  # SHR V0
    assert cpu.v[0] == 0b0101
    assert cpu.v[0xF] == 0
    print("PASS: test_shr")


def test_shl():
    cpu = CPU()
    cpu.v[0] = 0b10000000
    cpu.decode_and_execute(0x800E)  # SHL V0
    assert cpu.v[0] == 0b00000000
    assert cpu.v[0xF] == 1
    print("PASS: test_shl")


def test_ld_dt():
    cpu = CPU()
    cpu.delay_timer = 42
    cpu.decode_and_execute(0xF007)  # LD V0, DT
    assert cpu.v[0] == 42
    print("PASS: test_ld_dt")


def test_ld_st():
    cpu = CPU()
    cpu.v[5] = 30
    cpu.decode_and_execute(0xF518)  # LD ST, V5
    assert cpu.sound_timer == 30
    print("PASS: test_ld_st")


def test_ld_f_vx():
    cpu = CPU()
    cpu.v[0] = 0xA
    cpu.decode_and_execute(0xF029)  # LD F, V0
    assert cpu.i == 0xA * 5  # Font A at address 50
    print("PASS: test_ld_f_vx")


def test_skp():
    cpu = CPU()
    cpu.pc = 0x200
    cpu.v[0] = 5
    cpu.keypad[5] = 1
    cpu.decode_and_execute(0xE09E)  # SKP V0
    assert cpu.pc == 0x204
    print("PASS: test_skp")


def test_sknp():
    cpu = CPU()
    cpu.pc = 0x200
    cpu.v[0] = 5
    cpu.keypad[5] = 0
    cpu.decode_and_execute(0xE0A1)  # SKNP V0
    assert cpu.pc == 0x204
    print("PASS: test_sknp")


def test_timers():
    cpu = CPU()
    cpu.delay_timer = 5
    cpu.sound_timer = 3
    cpu.update_timers()
    assert cpu.delay_timer == 4
    assert cpu.sound_timer == 2
    cpu.update_timers()
    cpu.update_timers()
    cpu.update_timers()
    assert cpu.delay_timer == 1
    assert cpu.sound_timer == 0
    cpu.update_timers()
    assert cpu.delay_timer == 0
    assert cpu.sound_timer == 0
    print("PASS: test_timers")


def test_draw():
    cpu = CPU()
    # Load a simple sprite (1 byte: 0xFF = 8 pixels)
    cpu.i = 0x300
    cpu.memory[0x300] = 0xFF
    cpu.v[0] = 0  # x
    cpu.v[1] = 0  # y
    cpu.decode_and_execute(0xD011)  # DRW V0, V1, 1
    assert cpu.display[0][0] == 1
    assert cpu.display[0][7] == 1
    assert cpu.v[0xF] == 0  # No collision
    # Draw again to test collision
    cpu.decode_and_execute(0xD011)
    assert cpu.v[0xF] == 1  # Collision
    assert cpu.display[0][0] == 0
    print("PASS: test_draw")


if __name__ == '__main__':
    print("Running CHIP-8 CPU tests...")
    test_reset()
    test_load_rom()
    test_fetch()
    test_cls()
    test_ret()
    test_jp()
    test_call_ret()
    test_se_vx_nn()
    test_sne_vx_nn()
    test_ld_vx_nn()
    test_add_vx_nn()
    test_ld_i()
    test_add_i()
    test_ld_bcd()
    test_ld_vx_vy()
    test_add_vx_vy()
    test_add_vx_vy_carry()
    test_sub_vx_vy()
    test_sub_vx_vy_borrow()
    test_and()
    test_or()
    test_xor()
    test_shr()
    test_shl()
    test_ld_dt()
    test_ld_st()
    test_ld_f_vx()
    test_skp()
    test_sknp()
    test_timers()
    test_draw()
    print("\nAll tests passed!")
