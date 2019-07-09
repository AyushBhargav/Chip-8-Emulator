class Rom:

    def __init__(self, code_bytes):
        self.instructions = code_bytes
        self.cur_pos = 0

    def next_instr(self):
        instr = (self.instructions[self.cur_pos] << 4) | (self.instructions[self.cur_pos + 1])
        self.cur_pos += 2
