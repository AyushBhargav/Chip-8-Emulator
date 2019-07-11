import video
from cpu import CPU

chip8 = CPU()
chip8.graphics[5] = True

video.start_loop(chip8)