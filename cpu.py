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

    def __init__(self, rom):
        self.memory = [0] * 4096
        self.reg = [0] * 16
        self.i_reg = 0
        self.pc = 0
        self.stack = _Stack()
        self.delay_timer = 0
        self.sound_timer = 0
        self.input = [False] * 16
        self.graphics = [[0 for _ in 32] for _ in 64]

    def cpu_cycle(self):
        if self.pc > len(self.memory):
            return -1 # Abort execution.

        instr = self._get_instr()
        # Really long if else ladder now.
        if instr == 0x00E0:
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
        else:
            raise Exception("Wrong opcode: " + str(instr))

    # Helper functions for CPU.
    def _get_instr(self):
        return (self.instructions[self.pc] << 4) | (self.instructions[self.pc + 1])

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
        x = self._get_nibbles[1]
        n = instr & 0x00FF
        if self.reg[x] == n:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _skip_if_neq_num(self, instr):
        x = self._get_nibbles[1]
        n = instr & 0x00FF
        if self.reg[x] != n:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _skip_if_eq_reg(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
        if self.reg[x] == self.reg[y]:
            # Skip
            self.pc += 4
        else:
            self.pc += 2

    def _set_reg_num(self, instr):
        x = self._get_nibbles[1]
        n = instr & 0x00FF
        self.reg[x] = n
        self.pc += 2

    def _add_reg_num(self, instr):
        x = self._get_nibbles[1]
        n = instr & 0x00FF
        self.reg[x] = (self.reg[x] + n) & 0xFFFF
        self.pc += 2

    def _assign_reg(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
        self.reg[x] = self.reg[y]
        self.pc += 2

    def _or_reg(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
        self.reg[x] = self.reg[x] | self.reg[y]
        self.pc += 2

    def _and_reg(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
        self.reg[x] = self.reg[x] & self.reg[y]
        self.pc += 2

    def _xor_reg(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
        self.reg[x] = self.reg[x] ^ self.reg[y]
        self.pc += 2

    def _add_regs(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
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
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
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
        x = self._get_nibbles[1]
        self.reg[0xF] = self.reg[x] & 0x1
        self.reg[x] >>= 1
        self.pc += 2

    def _sub_regs_rev(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
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
        x = self._get_nibbles[1]
        self.reg[0xF] = self.reg[x] >> 7
        self.reg[x] = (self.reg[x] << 1) & 0xFF
        self.pc += 2

    def _skip_if_neq_reg(self, instr):
        x = self._get_nibbles[1]
        y = self._get_nibbles[2]
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
        x = self._get_nibbles[1]
        addr = instr & 0x00FF
        self.reg[x] = random.randint(0, 0xFF) & addr
        self.pc += 2

    def _display_sprite(self, instr):
        collision_flag = False
        x = self.reg[self._get_nibbles[1]]
        y = self.reg[self._get_nibbles[2]]
        N = instr & 0x0F
        for n in range(0, N):
            for b in range(0, 8):
                # TODO: Fix overflow problem.
                old_pixel = self.graphics[x + b][n]
                self.graphics[x + b][n] |= bool((self.memory[self.i_reg + n] & (0x80 >> b)))
                if old_pixel and not self.graphics[x + b][n]:
                    # Collision detected
                    collision_flag = True
        if collision_flag:
            self.reg[0xF] = 1