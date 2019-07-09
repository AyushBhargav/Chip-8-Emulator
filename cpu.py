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
            # Unset Carry Flag
            self.reg[0xF] = 1
        self.reg[x] = self.reg[x] & 0xFFFF
        self.pc += 2