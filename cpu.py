import random


class CPU:

    class _Stack:

        def __init__(self):
            self.stack = [0] * 16
            self.top = -1

        def pop(self):
            if self.top == -1:
                raise Exception("Popping empty stack.")
            self.top -= 1
            return self.stack[self.top + 1]

        def push(self, num):
            if self.top == 15:
                raise Exception("Pushing to fully filled stack.")
            self.top += 1
            self.stack[self.top] = num

    def __init__(self):
        self.memory = [0] * 4096
        self.reg = [0] * 16
        self.i_reg = 0
        self.pc = 0
        self.stack = self._Stack()
        self.delay_timer = 0
        self.sound_timer = 0
        self.input = [False] * 16
        self.graphics = [False] * (64 * 32)

    def load_program(self, hex_code):
        for i, b in enumerate(hex_code):
            self.memory[0x200 + i] = b

    def load_font(self):
        fonts = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        for i, font in enumerate(fonts):
            self.memory[i] = font

    def decrement_counters(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def cpu_cycle(self):
        if self.pc > len(self.memory):
            return -1 # Abort execution.

        instr = self._get_instr()
        # Really long if else ladder now.
        if 0x0000 <= instr <= 0x0FFF:
            self.pc += 2
            return # Do nothing for RCA 1802
        elif instr == 0x00E0:
            self._clear_screen()
        elif instr == 0x00EE:
            self._return_subroutine()
        elif 0x1000 <= instr <= 0x1FFF:
            self._goto_address(instr)
        elif 0x2000 <= instr <= 0x2FFF:
            self._call_subroutine(instr)
        elif 0x3000 <= instr <= 0x3FFF:
            self._skip_if_eq_num(instr)
        elif 0x4000 <= instr <= 0x4FFF:
            self._skip_if_neq_num(instr)
        elif 0x5000 <= instr <= 0x5FF0:
            self._skip_if_eq_reg(instr)
        elif 0x6000 <= instr <= 0x6FFF:
            self._set_reg_num(instr)
        elif 0x7000 <= instr <= 0x7FFF:
            self._add_reg_num(instr)
        elif 0x8000 <= instr <= 0x8FF0:
            self._assign_reg(instr)
        elif 0x8001 <= instr <= 0x8FF1:
            self._or_reg(instr)
        elif 0x8002 <= instr <= 0x8FF2:
            self._and_reg(instr)
        elif 0x8003 <= instr <= 0x8FF3:
            self._xor_reg(instr)
        elif 0x8004 <= instr <= 0x8FF4:
            self._add_regs(instr)
        elif 0x8005 <= instr <= 0x8FF5:
            self._sub_regs(instr)
        elif 0x8006 <= instr <= 0x8FF6:
            self._right_shift(instr)
        elif 0x8007 <= instr <= 0x8FF7:
            self._sub_regs_rev(instr)
        elif 0x800E <= instr <= 0x8FFE:
            self._left_shift(instr)
        elif 0x9000 <= instr <= 0x9FF0:
            self._skip_if_neq_reg(instr)
        elif 0xA000 <= instr <= 0xAFFF:
            self._set_index_reg(instr)
        elif 0xB000 <= instr <= 0xBFFF:
            self._jmp_addr_add(instr)
        elif 0xC000 <= instr <= 0xCFFF:
            self._set_rand_reg(instr)
        elif 0xD000 <= instr <= 0xDFFF:
            self._display_sprite(instr)
        elif 0xE09E <= instr <= 0xEF9E:
            self._skip_key_down(instr)
        elif 0xE0A1 <= instr <= 0xEFA1:
            self._skip_key_up(instr)
        elif 0xF007 <= instr <= 0xFF07:
            self._set_reg_delay(instr)
        elif 0xF00A <= instr <= 0xFF0A:
            self._wait_key_press(instr)
        elif 0xF015 <= instr <= 0xFF15:
            self._set_delay_timer(instr)
        elif 0xF018 <= instr <= 0xFF18:
            self._set_sound_timer(instr)
        elif 0xF01E <= instr <= 0xFF1E:
            self._increment_i(instr)
        elif 0xF029 <= instr <= 0xFF29:
            self._set_font(instr)
        elif 0xF033 <= instr <= 0xFF33:
            self._bcd(instr)
        elif 0xF055 <= instr <= 0xFF55:
            self._reg_dump(instr)
        elif 0xF065 <= instr <= 0xFF65:
            self._reg_load(instr)
        else:
            raise Exception("Wrong opcode: " + str(instr))

    # Helper functions for CPU.
    def _get_instr(self):
        return (self.memory[self.pc] << 8) | (self.memory[self.pc + 1])

    def _get_nibbles(self, instr):
        return [(instr & 0xF000) >> 12, (instr & 0x0F00) >> 8, (instr & 0x00F0) >> 4, (instr & 0x000F)]

    # Opcode specific functions.
    def _clear_screen(self):
        self.graphics = [False for _ in self.graphics]
        self.pc += 2

    def _return_subroutine(self):
        self.pc = self.stack.pop() + 1

    def _goto_address(self, instr):
        self.pc = instr & 0x0FFF

    def _call_subroutine(self, instr):
        self.stack.push(self.pc)
        addr = instr & 0x0FFF
        self.pc = addr

    def _skip_if_eq_num(self, instr):
        x = self._get_nibbles(instr)[1]
        n = instr & 0x00FF
        if self.reg[x] == n:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _skip_if_neq_num(self, instr):
        x = self._get_nibbles(instr)[1]
        n = instr & 0x00FF
        if self.reg[x] != n:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _skip_if_eq_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        if self.reg[x] == self.reg[y]:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _set_reg_num(self, instr):
        x = self._get_nibbles(instr)[1]
        n = instr & 0x00FF
        self.reg[x] = n
        self.pc += 2

    def _add_reg_num(self, instr):
        x = self._get_nibbles(instr)[1]
        n = instr & 0x00FF
        self.reg[x] = (self.reg[x] + n) & 0xFFFF
        self.pc += 2

    def _assign_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[y]
        self.pc += 2

    def _or_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[x] | self.reg[y]
        self.pc += 2

    def _and_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[x] & self.reg[y]
        self.pc += 2

    def _xor_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[x] ^ self.reg[y]
        self.pc += 2

    def _add_regs(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[x] + self.reg[y]
        # Check for carry
        if self.reg[x] > 0xFFFF:
            # Set Carry flag
            self.reg[0xF] = 1
        else:
            # Unset Carry Flag
            self.reg[0xF] = 0
        self.reg[x] = self.reg[x] & 0xFFFF
        self.pc += 2

    def _sub_regs(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[x] - self.reg[y]
        # Check for borrow
        if self.reg[x] < 0:
            # Unset Carry flag
            self.reg[0xF] = 0
        else:
            # Set Carry Flag
            self.reg[0xF] = 1
        self.reg[x] = self.reg[x] & 0xFFFF
        self.pc += 2

    def _right_shift(self, instr):
        x = self._get_nibbles(instr)[1]
        self.reg[0xF] = self.reg[x] & 0x1
        self.reg[x] >>= 1
        self.pc += 2

    def _sub_regs_rev(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        self.reg[x] = self.reg[y] - self.reg[x]
        # Check for borrow
        if self.reg[x] < 0:
            # Unset Carry flag
            self.reg[0xF] = 0
        else:
            # Set Carry Flag
            self.reg[0xF] = 1
        self.reg[x] = self.reg[x] & 0xFFFF
        self.pc += 2

    def _left_shift(self, instr):
        x = self._get_nibbles(instr)[1]
        self.reg[0xF] = self.reg[x] >> 7
        self.reg[x] = (self.reg[x] << 1) & 0xFF
        self.pc += 2

    def _skip_if_neq_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        y = self._get_nibbles(instr)[2]
        if self.reg[x] != self.reg[y]:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _set_index_reg(self, instr):
        addr = instr & 0x0FFF
        self.i_reg = addr
        self.pc += 2

    def _jmp_addr_add(self, instr):
        addr = instr & 0x0FFF
        self.pc = self.reg[0] + addr

    def _set_rand_reg(self, instr):
        x = self._get_nibbles(instr)[1]
        addr = instr & 0x00FF
        self.reg[x] = random.randint(0, 0xFF) & addr
        self.pc += 2

    def _display_sprite(self, instr):
        # TODO: Convert for single array 2D matrix.
        collision_flag = False
        x = self.reg[self._get_nibbles(instr)[1]]
        y = self.reg[self._get_nibbles(instr)[2]]
        N = instr & 0x0F
        for n in range(0, N):
            for b in range(0, 8):
                index = x + b + (y * (n - 1))
                old_pixel = self.graphics[index]
                self.graphics[index] ^= bool((self.memory[self.i_reg + n] & (0x80 >> b)))
                if old_pixel and not self.graphics[index]:
                    # Collision detected
                    collision_flag = True
        if collision_flag:
            self.reg[0xF] = 1

    def _skip_key_down(self, instr):
        x = self._get_nibbles(instr)[1]
        if self.input[self.reg[x]]:
            self.pc += 4
        else:
            self.pc += 2

    def _skip_key_up(self, instr):
        x  = self._get_nibbles(instr)[1]
        if not self.input[self.reg[x]]:
            self.pc += 4
        else:
            self.pc += 2

    def _set_reg_delay(self, instr):
        x = self._get_nibbles(instr)[1]
        self.reg[x] = self.delay_timer
        self.pc += 2

    def _wait_key_press(self, instr):
        x = self._get_nibbles(instr)[1]
        for i in self.input:
            if i:
                # Key is pressed. Move on to next instruction.
                self.pc += 2
                break

    def _set_delay_timer(self, instr):
        x = self._get_nibbles(instr)[1]
        self.delay_timer = self.reg[x]
        self.pc += 2

    def _set_sound_timer(self, instr):
        x = self._get_nibbles(instr)[1]
        self.sound_timer = self.reg[x]
        self.pc += 2

    def _increment_i(self, instr):
        x = self._get_nibbles(instr)[1]
        self.i_reg += self.reg[x]
        self.pc += 2

    def _set_font(self, instr):
        x = self._get_nibbles(instr)[1]
        self.i_reg = reg[x] * 5
        self.pc += 2

    def _bcd(self, instr):
        x = self._get_nibbles(instr)[1]
        self.memory[self.i_reg] = int(self.reg[x] / 100)
        self.memory[self.i_reg] = int(self.reg[x] / 10)
        self.memory[self.i_reg] = int(self.reg[x] % 10)
        self.pc += 2

    def _reg_dump(self, instr):
        x = self._get_nibbles(instr)[1]
        for offset in range(0, x + 1):
            self.memory[self.i_reg + offset] = self.reg[offset]
        self.pc += 2

    def _reg_load(self, instr):
        x = self._get_nibbles(instr)[1]
        for offset in range(0, x + 1):
            self.reg[offset] = self.memory[self.i_reg + offset] & 0xFFFF
        self.pc += 2
