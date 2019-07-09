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
            _clear_screen()
        elif instr == 0x00EE:
            _return_subroutine()
        elif 0x1000 <= instr <= 0x1FFF:
            _goto_address(instr)
        elif 0x2000 <= instr <= 0x2FFF:
            _call_subroutine(instr)
        elif 0x3000 <= instr <= 0x3FFF:
            _skip_if_eq_num(instr)
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
