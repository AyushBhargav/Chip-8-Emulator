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
        self.rom = rom
        self.input = [False] * 16
        self.graphics = [[0 for _ in 32] for _ in 64]

    def cpu_cycle(self):
        instr = self.rom.next_instr()