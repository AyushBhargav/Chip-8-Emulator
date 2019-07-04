extern crate rand;

use rand::Rng;

pub struct VirtualMachine {
    // RAM for CPU (4K bytes of memory)
    pub memory: [u8; 4096],
    // Registers from V0 to VF. VF will hold the carry flags for computations.
    pub registers: [u8; 16],
    pub vf: u8,
    // Index register
    pub index_register: u16,
    // Program counter
    pub program_counter: u16,
    // Graphics for (64 * 32) pixels
    pub video: [bool; 64 * 32],
    // Keypad for 16 buttons
    pub keypad: [bool; 16],
    // Timer registersu
    pub delay_timer: u8,
    pub sound_timer: u8, // Sounds a buzzer like sound whenver it reaches zero.
    // Program stack. Chip-8 can only go upto 16 level deep.
    pub stack: [u16; 16],
    pub stack_top: i8,
}

fn fetch_instruction(memory: [u8; 4096], program_counter: u16) -> u16{
    // Each opcode consists of two bytes. Second operand is casted as u16 as u16 | u8 is noit permissible. :(
    let opcode: u16 = ((memory[program_counter as usize] as u16) << 8) | (memory[(program_counter + 1) as usize] as u16);
    opcode
}

impl VirtualMachine {

    fn execute_op(&mut self, opcode: u16) {
        match opcode {
            // Jump statement.
            0x1000 ..= 0x1FFF => self.program_counter = opcode & 0xFFF,
            // Call the subroutine statement.
            0x2000 ..= 0x2FFF => {
                self.stack[self.stack_top as usize] = self.program_counter;
                self.stack_top += 1;
                self.program_counter = opcode * 0xFFF;
            },
            // Skip next instruction if given register equals the operand.
            0x3000 ..= 0x3FFF => {
                let x: u8 = ((opcode & 0xF00) >> 8) as u8;
                let vx: u8 = self.registers[x as usize];
                if vx == (opcode & 0xFF) as u8 {
                    self.program_counter += 4; // Skip 4 bytes.
                }
            },
            // Skip next instruction if given register doesn't equal the operand.
            0x4000 ..= 0x4FFF => {
                let x: u8 = ((opcode & 0xF00) >> 8) as u8;
                let vx: u8 = self.registers[x as usize];
                if vx != (opcode & 0xFF) as u8 {
                    self.program_counter += 4; // Skip 4 bytes.
                }
            },
            // Skip next instruction if given registers aren't equal.
            0x5000 ..= 0x5FFF => {
                let x: u8 = ((opcode & 0xF00) >> 8) as u8;
                let vx: u8 = self.registers[x as usize];
                let y: u8 = ((opcode & 0xF0) >> 4) as u8;
                let vy: u8 = self.registers[y as usize];
                if vx == vy {
                    self.program_counter += 4; // Skip 4 bytes.
                }
            },
            // Set given operand to specified register.
            0x6000 ..= 0x6FFF => {
                let x: u8 = ((opcode & 0xF00) >> 8) as u8;
                self.registers[x as usize] = (opcode & 0xFF) as u8;
                self.program_counter += 2;
            },
            // Add given operand to specified register.
            0x7000 ..= 0x7FFF => {
                let x: u8 = ((opcode & 0xF00) >> 8) as u8;
                self.registers[x as usize] += (opcode & 0xFF) as u8;
                self.program_counter += 2;
            },
            // Register manipulation.
            0x8000 ..= 0x8FFF => {
                let x: u8 = ((opcode & 0xF00) >> 8) as u8;
                let y: u8 = ((opcode & 0xF0) as u8) >> 4;
                match opcode & 0xF {
                    0x0 => self.registers[x as usize] = self.registers[y as usize],
                    0x1 => self.registers[x as usize] |= self.registers[y as usize],
                    0x2 => self.registers[x as usize] &= self.registers[y as usize],
                    0x3 => self.registers[x as usize] ^= self.registers[y as usize],
                    0x4 => {
                        let sum: u16 = (self.registers[x as usize] + self.registers[y as usize]) as u16;
                        self.registers[x as usize] = (sum & 0xFF) as u8;
                        if sum > 0xFF {
                            // Set carry register.
                            self.registers[self.vf as usize] = 0x1;
                        }
                        else {
                            // Unset carry register.
                            self.registers[self.vf as usize] = 0x0;
                        }
                        self.program_counter += 2;
                    },
                    0x5 => {
                        let sub: u16 = (self.registers[x as usize] - self.registers[y as usize]) as u16;
                        self.registers[x as usize] = (sub & 0xFF) as u8;
                        if sub > 0 {
                            // Set carry register for no borrow.
                            self.registers[self.vf as usize] = 0x1;
                        }
                        else {
                            // Unset carry register for borrow.
                            self.registers[self.vf as usize] = 0x0;
                        }
                        self.program_counter += 2;
                    },
                    0x6 => {
                        self.registers[self.vf as usize] = self.registers[x as usize] & 0x01;
                        self.registers[x as usize] >>= 1;
                        self.program_counter += 2;
                    },
                    0x7 => {
                        let sub: u16 = (self.registers[y as usize] - self.registers[x as usize]) as u16;
                        self.registers[x as usize] = (sub & 0xFF) as u8;
                        if sub > 0 {
                            // Set carry register for no borrow.
                            self.registers[self.vf as usize] = 0x1;
                        }
                        else {
                            // Unset carry register for borrow.
                            self.registers[self.vf as usize] = 0x0;
                        }
                        self.program_counter += 2
                    },
                    0xE => {
                        self.registers[self.vf as usize] = self.registers[x as usize] >> 7;
                        self.registers[x as usize] <<= 1;
                        self.program_counter += 2
                    },
                    _ => panic!("Unrecognized opcode: {}", opcode)
                }
            },
            // Skip next instruction if Vx is not equal to Vy.
            0x9000 ..= 0x9FFF => {
                let x: u8 = ((opcode & 0xFFF) >> 8) as u8;
                let y: u8 = ((opcode & 0xFF) >> 4) as u8;
                if self.registers[x as usize] != self.registers[y as usize] {
                    self.program_counter += 4; // Skip next instruction.
                }
                else {
                    self.program_counter += 2;
                }
            },
            // Set index pointer to memory location.
            0xA000 ..= 0xAFFF => {
                self.index_register = opcode & (0x0FFF);
                self.program_counter += 2;
            },
            // Jump to given address + V0
            0xB000 ..= 0xBFFF => self.program_counter = ((opcode & 0x0FFF) + (self.registers[0 as usize] as u16)) as u16,
            // Assign random number to Vx register.
            0xC000 ..= 0xCFFF => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let n: u8 = (opcode & 0x00FF) as u8;
                let mut rng = rand::thread_rng();
                let random_number = rng.gen_range(0, 256) as u8;
                self.registers[x as usize] = n & random_number;
                self.program_counter += 2;
            },
            0xD000 ..= 0xDFFF => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let y: u8 = ((opcode & 0x00F0) >> 4) as u8;
                let n: u8 = (opcode & 0x000F) as u8;
                let pos_x: u8 = self.registers[x as usize];
                let pos_y: u8 = self.registers[y as usize];
                for offset in 0 .. n {
                    let sprite: u8 = self.memory[(self.index_register + offset as u16) as usize];
                    for i in 0 .. 8 {
                        if (sprite & (0x80 >> i)) != 0 {
                            // Sprite-pixel will be inverted.
                            if self.video[(pos_x + i + (pos_y + offset) * 64) as usize] {
                                self.registers[self.vf as usize] = 0x01;
                            }
                            self.video[(pos_x + i + (pos_y + offset) * 64) as usize] = !self.video[(pos_x + i + (pos_y + offset) * 64) as usize];
                        }
                    }
                }
                self.program_counter += 2;
            },
            0xE09E ..= 0xEF9E => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let key: u8 = self.registers[x as usize];
                if self.keypad[key as usize] {
                    self.program_counter += 4;
                }
                else {
                    self.program_counter += 2;
                }
            },
            0xE0A1 ..= 0xEFA1 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let key: u8 = self.registers[x as usize];
                if !self.keypad[key as usize] {
                    self.program_counter += 4;
                }
                else {
                    self.program_counter += 2;
                }
            },
            0xF007 ..= 0xFF07 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                self.delay_timer = self.registers[x as usize];
                self.program_counter += 2;
            },
            0xF00A ..= 0xFF0A => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let mut input_avail: bool = false;
                for (i, input) in self.keypad.iter().enumerate() {
                    if *input {
                        input_avail = true;
                        self.registers[x as usize] = i as u8;
                    }
                }
                if input_avail {
                    self.program_counter += 2;
                }
            },
            0xF015 ..= 0xFF15 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                self.delay_timer = self.registers[x as usize];
                self.program_counter += 2;
            },
            0xF018 ..= 0xFF18 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                self.sound_timer = self.registers[x as usize];
                self.program_counter += 2;
            },
            0xF01E ..= 0xFF1E => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                self.index_register += self.registers[x as usize] as u16;
                self.program_counter += 2;
            },
            0xF029 ..= 0xFF29 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let ch: u8 = self.registers[x as usize];
                self.index_register = self.memory[(ch * 5) as usize] as u16;
                self.program_counter += 2;
            },
            0xF033 ..= 0xFF33 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                let n: u8 = self.registers[x as usize];
                self.memory[self.index_register as usize] = (n / 100) as u8;
                self.memory[(self.index_register + 1) as usize] = ((n / 10) % 10) as u8;
                self.memory[(self.index_register + 2) as usize] = (n % 10) as u8;
                self.program_counter += 2;
            },
            0xF055 ..= 0xFF55 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                for i in 0 .. x + 1 {
                    self.memory[(self.index_register + i as u16) as usize] = self.registers[i as usize];
                }
                self.program_counter += 2;
            },
            0xF065 ..= 0xFF65 => {
                let x: u8 = ((opcode & 0x0F00) >> 8) as u8;
                for i in 0 .. x + 1 {
                    self.registers[i as usize] = self.memory[(self.index_register + i as u16) as usize];
                }
                self.program_counter += 2;
            },
            _ => {
                panic!("Can't recognize parsed opcode: {}", opcode);
            }
        }
    }

    #[no_mangle]
    // Load game fonts
    pub fn load_fonts(&mut self, font_set: [u8; 80]) {
        for i in 0 .. 80 {
            self.memory[i as usize] = font_set[i as usize];
        }
    }

    // Single CPU cycle
    #[no_mangle]
    pub fn tick(&mut self) {
        let opcode = fetch_instruction(self.memory, self.program_counter);
        self.execute_op(opcode);
    }
}

// Static objects which will be interfaced with Javascript.
static mut CHIP8: VirtualMachine = VirtualMachine {
    memory: [0; 4096],
    registers: [0; 16],
    index_register: 0,
    vf: 15,
    // Programs start at memory location of 0x200.
    program_counter: 0x200,
    // Blank screen at the start.
    video: [false; 64 * 32],
    keypad: [false; 16],
    delay_timer: 0,
    sound_timer: 0,
    // Empty Stack.
    stack: [0; 16],
    stack_top: -1,
};

#[no_mangle]
pub fn cpu_cycle() {
    unsafe {
        CHIP8.tick();
    }
}

#[no_mangle]
pub fn get_graphics() -> &'static [bool; 64 * 32] {
    unsafe {
        &CHIP8.video
    }
}

#[no_mangle]
pub fn get_memory() -> &'static [u8; 4096] {
    unsafe {
        &CHIP8.memory
    }
}

#[no_mangle]
pub fn get_chip8_fontset() -> [u8; 80] {
    let chip8_fontset: [u8; 80] = [
        0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
        0x20, 0x60, 0x20, 0x20, 0x70, // 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
        0x90, 0x90, 0xF0, 0x10, 0x10, // 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
        0xF0, 0x10, 0x20, 0x40, 0x40, // 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, // A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
        0xF0, 0x80, 0x80, 0x80, 0xF0, // C
        0xE0, 0x90, 0x90, 0x90, 0xE0, // D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
        0xF0, 0x80, 0xF0, 0x80, 0x80  // F
    ];
    chip8_fontset
}

pub fn main() {
    
}