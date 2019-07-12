import sys
import video
from cpu import CPU

#if len(sys.argv) < 2:
#    print("Please specify Rom for Chip-8. [Usage]: python main.py file.ch8")
#    exit(0)

with open(".\\roms\\games\\Tank.ch8", 'rb') as f:
    hex_code = bytearray(f.read())
    chip8 = CPU()
    chip8.load_program(hex_code)
    chip8.load_font()
    video.start_loop(chip8)